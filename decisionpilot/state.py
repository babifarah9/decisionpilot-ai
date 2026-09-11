"""Transactional durable state; human decisions are not agent tools.

SQLite is for one persistent host. Never put this database on ephemeral AgentCore storage.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import hmac
import json
import math
import os
import secrets
import sqlite3
import time
import uuid

from .catalog import rank

DB_PATH = Path(os.getenv('DECISIONPILOT_DB', '.decisionpilot/workflows-v2.db'))


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


@contextmanager
def connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH, timeout=15)
    c.row_factory = sqlite3.Row
    try:
        c.execute('PRAGMA foreign_keys=ON')
        c.execute('BEGIN IMMEDIATE')
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()


def init_db():
    with connection() as c:
        c.execute('CREATE TABLE IF NOT EXISTS workflows (id TEXT PRIMARY KEY, owner_hash TEXT NOT NULL, data TEXT NOT NULL)')
        c.execute('CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL REFERENCES workflows(id), kind TEXT NOT NULL, message TEXT NOT NULL, created_at TEXT NOT NULL)')
        c.execute('CREATE TABLE IF NOT EXISTS provider_receipts (proposal_id TEXT PRIMARY KEY, data TEXT NOT NULL)')


def _event(c, tid, kind, message):
    c.execute('INSERT INTO events(task_id,kind,message,created_at) VALUES(?,?,?,?)', (tid, kind, message, utc()))


def _load(c, tid, owner=None):
    row = c.execute('SELECT * FROM workflows WHERE id=?', (tid,)).fetchone()
    if not row or (owner is not None and not hmac.compare_digest(row['owner_hash'], digest(owner))):
        raise PermissionError('Workflow not found or not owned by this session.')
    return json.loads(row['data'])


def _save(c, t):
    t['updated_at'] = utc()
    c.execute('UPDATE workflows SET data=? WHERE id=?', (json.dumps(t), t['id']))


def create_task(objective, owner, budget=180.0, daypart='morning', manual_minutes=35, mode='offline'):
    if not isinstance(objective, str) or not 10 <= len(objective.strip()) <= 1200:
        raise ValueError('Enter an objective between 10 and 1,200 characters.')
    if not owner or len(owner) < 24:
        raise PermissionError('A session owner is required.')
    rank([], budget, daypart)
    if not isinstance(manual_minutes, (int, float)) or not math.isfinite(manual_minutes) or not 1 <= manual_minutes <= 240:
        raise ValueError('Manual estimate must be 1–240 minutes.')
    if mode not in ('offline', 'bedrock', 'agentcore'):
        raise ValueError('Unknown execution mode.')
    init_db()
    t = dict(id=uuid.uuid4().hex, objective=objective.strip(), budget=budget, daypart=daypart,
             status='PLANNING', manual_minutes=manual_minutes, attention_seconds=0,
             mode=mode, candidates=[], proposals=[], booking=None, verified=False,
             created_at=utc(), updated_at=utc(), error=None)
    with connection() as c:
        if mode != 'offline':
            today = utc()[:10]
            used = c.execute("SELECT COUNT(*) FROM workflows WHERE json_extract(data, '$.mode') != 'offline' AND substr(json_extract(data, '$.created_at'),1,10)=?", (today,)).fetchone()[0]
            if used >= int(os.getenv('DECISIONPILOT_DAILY_CLOUD_RUNS', '30')):
                raise ValueError('Daily cloud run limit reached.')
        recent = c.execute("SELECT COUNT(*) FROM workflows WHERE owner_hash=? AND json_extract(data,'$.created_at') > ?", (digest(owner), datetime.fromtimestamp(time.time()-60, timezone.utc).isoformat())).fetchone()[0]
        if recent >= 10:
            raise ValueError('Please wait before creating more workflows.')
        c.execute('INSERT INTO workflows VALUES(?,?,?)', (t['id'], digest(owner), json.dumps(t)))
        _event(c, t['id'], 'OBJECTIVE_RECEIVED', objective.strip())
        _event(c, t['id'], 'PLAN', 'Search inventory → compare price and rating → propose → wait for human → execute → verify.')
    return t['id']


def propose(tid, candidates, selected_id, reason):
    """Controller validates model output against trusted inventory before saving."""
    with connection() as c:
        t = _load(c, tid)
        if t['status'] != 'PLANNING':
            raise ValueError('Planning has already ended.')
        ranked = rank(candidates, t['budget'], t['daypart'])
        t['candidates'] = ranked
        _event(c, tid, 'SEARCH', f'Evaluated {len(ranked)} synthetic appointments.')
        eligible = [x for x in ranked if x['eligible']]
        if not eligible:
            t['status'] = 'NO_MATCH'
            _event(c, tid, 'NO_MATCH', 'No appointment satisfies the confirmed constraints. No action taken.')
        else:
            if selected_id != eligible[0]['id']:
                raise ValueError('Planner did not choose the strongest eligible candidate.')
            if not isinstance(reason, str) or not 1 <= len(reason) <= 2000:
                raise ValueError('A concise rationale is required.')
            p = dict(id=uuid.uuid4().hex, candidate=eligible[0], reason=reason,
                     status='PENDING', expires_at=time.time()+1800, created_at=utc())
            p['fingerprint'] = digest(p['candidate'])
            t['proposals'].append(p)
            t['status'] = 'WAITING_FOR_HUMAN'
            _event(c, tid, 'EVALUATION', 'Equal weight: normalized rating and price headroom. Budget and morning constraints enforced.')
            _event(c, tid, 'DECISION_GATE', f"Proposed {selected_id} at ${p['candidate']['cost']:.2f}; no booking executed.")
        _save(c, t)


def fail(tid, message):
    with connection() as c:
        t = _load(c, tid)
        if t['status'] == 'PLANNING':
            t['status'] = 'FAILED'
            t['error'] = message
            _event(c, tid, 'ERROR', message)
            _save(c, t)


def decide(tid, proposal_id, owner, approved, attention_seconds=0):
    """Human controller only. No LLM, tool registration or agent-facing endpoint."""
    if type(approved) is not bool:
        raise ValueError('Approval must be an explicit boolean.')
    if not isinstance(attention_seconds, (int, float)) or not math.isfinite(attention_seconds) or not 0 <= attention_seconds <= 86400:
        raise ValueError('Invalid attention duration.')
    with connection() as c:
        t = _load(c, tid, owner)  # Check owner and task BEFORE any mutation.
        p = next((p for p in t['proposals'] if p['id'] == proposal_id), None)
        if not p:
            raise ValueError('Proposal does not belong to this workflow.')
        if t['status'] != 'WAITING_FOR_HUMAN' or p['status'] != 'PENDING':
            raise ValueError('This proposal was already decided or is no longer pending.')
        if time.time() >= p['expires_at']:
            p['status'] = t['status'] = 'EXPIRED'
            _event(c, tid, 'EXPIRED', 'Proposal expired. Start a fresh search.')
        else:
            if digest(p['candidate']) != p['fingerprint']:
                raise ValueError('Proposal content changed.')
            p['status'] = t['status'] = 'APPROVED' if approved else 'REJECTED'
            p['decided_at'] = utc()
            t['attention_seconds'] += attention_seconds
            _event(c, tid, 'HUMAN_APPROVAL' if approved else 'HUMAN_REJECTION', f"Human {'approved' if approved else 'rejected'} proposal {proposal_id}.")
        _save(c, t)
        return t['status']


def execute(tid, owner):
    """Idempotent mock provider execution, reachable only from the human controller."""
    with connection() as c:
        t = _load(c, tid, owner)
        if t['booking']:
            return t['booking']
        if t['status'] != 'APPROVED':
            raise ValueError('Booking blocked: explicit human approval is required.')
        p = t['proposals'][-1]
        if p['status'] != 'APPROVED' or digest(p['candidate']) != p['fingerprint']:
            raise ValueError('Approved proposal is invalid.')
        if time.time() >= p['expires_at']:
            t['status'] = p['status'] = 'EXPIRED'
            _event(c, tid, 'EXPIRED', 'Approved quote expired before execution; no booking created.')
            _save(c, t)
            return None
        item = p['candidate']
        if not rank([item], t['budget'], t['daypart'])[0]['eligible']:
            raise ValueError('Approved appointment violates constraints.')
        receipt = dict(proposal_id=p['id'], candidate_id=item['id'], provider=item['provider'], slot=item['slot'],
                       cost=item['cost'], currency='USD', confirmation='SIM-'+secrets.token_hex(4).upper(), simulated=True)
        # A unique proposal key prevents duplicate side effects, even across concurrent requests.
        c.execute('INSERT INTO provider_receipts VALUES(?,?)', (p['id'], json.dumps(receipt)))
        t['booking'] = receipt
        t['status'] = 'VERIFYING'
        _event(c, tid, 'EXECUTION', f"Simulated provider accepted booking; {receipt['confirmation']}.")
        _save(c, t)
        return receipt


def verify(tid, owner):
    with connection() as c:
        t = _load(c, tid, owner)
        if t['status'] == 'COMPLETED':
            return True
        if t['status'] not in ('VERIFYING', 'VERIFICATION_FAILED'):
            raise ValueError('No executed booking to verify.')
        p = t['proposals'][-1]
        row = c.execute('SELECT data FROM provider_receipts WHERE proposal_id=?', (p['id'],)).fetchone()
        r = json.loads(row['data']) if row else None
        t['verified'] = bool(r and r == t['booking'] and r['cost'] == p['candidate']['cost']
                             and r['slot'] == p['candidate']['slot'] and r['provider'] == p['candidate']['provider']
                             and r['candidate_id'] == p['candidate']['id'] and r['confirmation'].startswith('SIM-'))
        t['status'] = 'COMPLETED' if t['verified'] else 'VERIFICATION_FAILED'
        _event(c, tid, 'VERIFICATION', 'Receipt, provider, slot and price match approved proposal.' if t['verified'] else 'Provider receipt mismatch; completion withheld.')
        _save(c, t)
        return t['verified']


def snapshot(tid, owner):
    with connection() as c:
        t = _load(c, tid, owner)
        events = [dict(x) for x in c.execute('SELECT seq,kind,message,created_at FROM events WHERE task_id=? ORDER BY seq', (tid,))]
    t['audit'] = events
    potential = round(max(0, t['manual_minutes'] - t['attention_seconds']/60), 1)
    t['metrics'] = dict(manual_minutes_estimate=t['manual_minutes'], human_attention_seconds=round(t['attention_seconds'], 1),
                        human_minutes_saved=potential if t['verified'] else 0,
                        label='Estimated savings; baseline is user supplied, attention is browser active time. Not an empirical productivity claim.')
    return t


def list_tasks(owner):
    init_db()
    with connection() as c:
        return [json.loads(r['data']) for r in c.execute('SELECT data FROM workflows WHERE owner_hash=? ORDER BY rowid DESC LIMIT 20', (digest(owner),))]


def recover_interrupted_planning():
    """Single-host startup recovery. Never rerun an interrupted model call automatically."""
    init_db()
    with connection() as c:
        rows = c.execute("SELECT data FROM workflows WHERE json_extract(data,'$.status')='PLANNING'").fetchall()
        for row in rows:
            t = json.loads(row['data'])
            t['status'] = 'FAILED'
            t['error'] = 'Planning was interrupted by a server restart. Start a fresh search; no booking was made.'
            _event(c, t['id'], 'RECOVERY', t['error'])
            _save(c, t)
