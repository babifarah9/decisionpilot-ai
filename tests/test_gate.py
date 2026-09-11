import concurrent.futures
import json
from pathlib import Path
import secrets
import tempfile
import unittest
from unittest.mock import patch
from decisionpilot import state
from decisionpilot.agent import run_task
from decisionpilot.catalog import inventory, rank
from decisionpilot.tools import TOOL_NAMES

OBJECTIVE = 'Schedule my annual car service under $180, mornings preferred.'


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = state.DB_PATH
        state.DB_PATH = Path(self.tmp.name)/'test.db'
        self.owner = secrets.token_hex(32)
        self.tid = state.create_task(OBJECTIVE, self.owner)
        run_task(self.tid, self.owner)
        self.p = self.snap()['proposals'][-1]

    def tearDown(self):
        state.DB_PATH = self.old
        self.tmp.cleanup()

    def snap(self):
        return state.snapshot(self.tid, self.owner)

    def approve(self):
        state.decide(self.tid, self.p['id'], self.owner, True, 60)

    def mutate(self, change):
        with state.connection() as c:
            t = state._load(c, self.tid)
            change(t)
            state._save(c, t)

    def test_end_to_end(self):
        t = self.snap()
        self.assertEqual(t['status'], 'WAITING_FOR_HUMAN')
        self.assertEqual(self.p['candidate']['cost'], 139)
        self.assertIsNone(t['booking'])
        self.assertEqual(t['metrics']['human_minutes_saved'], 0)
        self.approve()
        self.assertEqual(self.snap()['status'], 'APPROVED')
        state.execute(self.tid, self.owner)
        self.assertEqual(self.snap()['status'], 'VERIFYING')
        self.assertTrue(state.verify(self.tid, self.owner))
        t = self.snap()
        self.assertEqual(t['status'], 'COMPLETED')
        self.assertEqual(t['metrics']['human_minutes_saved'], 34)
        self.assertEqual([e['kind'] for e in t['audit']][-3:], ['HUMAN_APPROVAL','EXECUTION','VERIFICATION'])

    def test_execution_blocked_before_approval(self):
        with self.assertRaises(ValueError): state.execute(self.tid, self.owner)
        self.assertIsNone(self.snap()['booking'])

    def test_rejection_is_terminal(self):
        state.decide(self.tid, self.p['id'], self.owner, False)
        with self.assertRaises(ValueError): state.execute(self.tid, self.owner)
        with self.assertRaises(ValueError): self.approve()
        self.assertEqual(self.snap()['status'], 'REJECTED')
        self.assertEqual(self.snap()['metrics']['human_minutes_saved'], 0)

    def test_wrong_owner_cannot_read_or_approve(self):
        before = self.snap()
        with self.assertRaises(PermissionError): state.decide(self.tid, self.p['id'], 'wrong', True)
        with self.assertRaises(PermissionError): state.snapshot(self.tid, 'wrong')
        self.assertEqual(before, self.snap())

    def test_cross_task_proposal_no_mutation(self):
        other = state.create_task(OBJECTIVE, self.owner)
        with self.assertRaises(ValueError): state.decide(other, self.p['id'], self.owner, True)
        self.assertEqual(self.snap()['status'], 'WAITING_FOR_HUMAN')

    def test_approval_replay(self):
        self.approve()
        with self.assertRaises(ValueError): self.approve()
        self.assertEqual(self.snap()['attention_seconds'], 60)

    def test_duplicate_execution_is_idempotent(self):
        self.approve()
        first = state.execute(self.tid, self.owner)
        self.assertEqual(first, state.execute(self.tid, self.owner))
        self.assertEqual(sum(e['kind']=='EXECUTION' for e in self.snap()['audit']), 1)

    def test_concurrent_execution(self):
        self.approve()
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(lambda _: state.execute(self.tid, self.owner), range(6)))
        self.assertTrue(all(r==results[0] for r in results))
        self.assertEqual(sum(e['kind']=='EXECUTION' for e in self.snap()['audit']), 1)

    def test_concurrent_approval(self):
        def approve(_):
            try:
                self.approve()
                return True
            except ValueError:
                return False
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(approve, range(4)))
        self.assertEqual(sum(results), 1)

    def test_expired_proposal(self):
        self.mutate(lambda t: t['proposals'][-1].update(expires_at=0))
        self.assertEqual(state.decide(self.tid, self.p['id'], self.owner, True), 'EXPIRED')
        with self.assertRaises(ValueError): state.execute(self.tid, self.owner)

    def test_expired_after_approval(self):
        self.approve()
        self.mutate(lambda t: t['proposals'][-1].update(expires_at=0))
        self.assertIsNone(state.execute(self.tid, self.owner))
        self.assertEqual(self.snap()['status'], 'EXPIRED')

    def test_tampered_proposal(self):
        self.mutate(lambda t: t['proposals'][-1]['candidate'].update(cost=1))
        with self.assertRaises(ValueError): self.approve()

    def test_verify_failure_never_completes(self):
        self.approve()
        state.execute(self.tid, self.owner)
        with state.connection() as c:
            c.execute('DELETE FROM provider_receipts')
        self.assertFalse(state.verify(self.tid, self.owner))
        self.assertEqual(self.snap()['status'], 'VERIFICATION_FAILED')
        self.assertEqual(self.snap()['metrics']['human_minutes_saved'], 0)

    def test_verification_before_execution_blocked(self):
        with self.assertRaises(ValueError): state.verify(self.tid, self.owner)

    def test_restart_persistence(self):
        import subprocess, sys
        code = 'from pathlib import Path;from decisionpilot import state;import sys;state.DB_PATH=Path(sys.argv[1]);print(state.snapshot(sys.argv[2],sys.argv[3])["status"])'
        result = subprocess.check_output([sys.executable,'-c',code,str(state.DB_PATH),self.tid,self.owner], text=True)
        self.assertEqual(result.strip(), 'WAITING_FOR_HUMAN')

    def test_no_match(self):
        tid = state.create_task(OBJECTIVE, self.owner, budget=100)
        run_task(tid, self.owner)
        t = state.snapshot(tid, self.owner)
        self.assertEqual(t['status'], 'NO_MATCH')
        self.assertEqual(t['proposals'], [])

    def test_budget_strict_and_morning(self):
        for c in rank(inventory(), 139, 'morning'):
            self.assertFalse(c['eligible'])
        self.assertEqual(rank(inventory(),180,'morning')[0]['id'], 'central-0830')

    def test_nonfinite_budget_rejected(self):
        for budget in (float('nan'),float('inf'),-1):
            with self.assertRaises(ValueError): state.create_task(OBJECTIVE, self.owner, budget=budget)

    def test_no_approval_tool(self):
        self.assertEqual(TOOL_NAMES, ('search_appointments','evaluate_appointments'))
        self.assertNotIn('approve', ' '.join(TOOL_NAMES))

    def test_wrong_model_selection_fails_closed(self):
        tid = state.create_task(OBJECTIVE, self.owner, mode='bedrock')
        with patch('decisionpilot.agent.plan_with_strands', return_value={'selected_id':'invented','reason':'fake'}):
            with self.assertRaises(ValueError): run_task(tid, self.owner)
        self.assertEqual(state.snapshot(tid,self.owner)['status'], 'FAILED')

    def test_cloud_failure_is_not_offline_fallback(self):
        tid = state.create_task(OBJECTIVE, self.owner, mode='bedrock')
        with patch('decisionpilot.agent.plan_with_strands', side_effect=RuntimeError('sensitive provider error')):
            with self.assertRaises(RuntimeError): run_task(tid, self.owner)
        t = state.snapshot(tid,self.owner)
        self.assertEqual(t['status'], 'FAILED')
        self.assertNotIn('sensitive',json.dumps(t))

    def test_cloud_run_cap(self):
        with patch.dict('os.environ', {'DECISIONPILOT_DAILY_CLOUD_RUNS':'0'}):
            with self.assertRaises(ValueError): state.create_task(OBJECTIVE, self.owner, mode='bedrock')

    def test_approval_must_be_boolean(self):
        with self.assertRaises(ValueError): state.decide(self.tid, self.p['id'], self.owner, 'true')

    def test_negative_attention_rejected(self):
        with self.assertRaises(ValueError): state.decide(self.tid, self.p['id'], self.owner, True, -1)

    def test_interrupted_planning_recovery_preserves_gate(self):
        tid = state.create_task(OBJECTIVE, self.owner)
        state.recover_interrupted_planning()
        self.assertEqual(state.snapshot(tid, self.owner)['status'], 'FAILED')
        self.assertEqual(self.snap()['status'], 'WAITING_FOR_HUMAN')

    def test_pending_proposal_cannot_be_replaced(self):
        with self.assertRaises(ValueError): state.propose(self.tid,inventory(),'central-0830','another proposal')


if __name__ == '__main__': unittest.main()
