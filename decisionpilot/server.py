"""Single-host synthetic demo server. Use an HTTPS reverse proxy for public hosting."""
from concurrent.futures import ThreadPoolExecutor
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
import json
import os
import secrets
import threading
import time
from urllib.parse import urlsplit
from . import state
from .agent import run_task

POOL = ThreadPoolExecutor(max_workers=2)
SLOTS = threading.BoundedSemaphore(2)
MODE = os.getenv('DECISIONPILOT_MODE', 'offline')


def background(tid, owner):
    try:
        run_task(tid, owner)
    except Exception:
        pass  # A safe error is persisted by run_task.
    finally:
        SLOTS.release()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # No cookie, objective, task URL or private request logging.

    def owner(self):
        cookies = SimpleCookie()
        try:
            cookies.load(self.headers.get('Cookie', ''))
        except Exception:
            pass
        token = cookies.get('dp_session')
        value = token.value if token else ''
        if len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            value = secrets.token_hex(32)
            self.new_cookie = value
        return value

    def send(self, code, body, content_type='application/json'):
        raw = json.dumps(body).encode() if content_type == 'application/json' else body
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        if getattr(self, 'new_cookie', None):
            secure = '; Secure' if os.getenv('DECISIONPILOT_PUBLIC_ORIGIN', '').startswith('https://') else ''
            self.send_header('Set-Cookie', f'dp_session={self.new_cookie}; HttpOnly; SameSite=Strict; Path=/; Max-Age=2592000{secure}')
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        try:
            self.new_cookie = None
            owner = self.owner()
            path = urlsplit(self.path).path
            if path == '/health':
                return self.send(200, {'status': 'ok', 'mode': MODE})
            if path == '/api/session':
                return self.send(200, {'csrf': state.digest('csrf'+owner), 'mode': MODE,
                                       'tasks': [dict(id=t['id'], status=t['status']) for t in state.list_tasks(owner)]})
            if path.startswith('/api/tasks/'):
                return self.send(200, state.snapshot(path.rsplit('/', 1)[-1], owner))
            assets = {'/': ('index.html', 'text/html; charset=utf-8'), '/app.js': ('app.js', 'text/javascript'), '/style.css': ('style.css', 'text/css')}
            if path in assets:
                name, mime = assets[path]
                return self.send(200, files('decisionpilot').joinpath('web', name).read_bytes(), mime)
            self.send(404, {'error': 'Not found'})
        except PermissionError:
            self.send(404, {'error': 'Workflow not found'})

    def do_POST(self):
        self.new_cookie = None
        owner = self.owner()
        try:
            import hmac
            expected_origin = os.getenv('DECISIONPILOT_PUBLIC_ORIGIN', f'http://{self.headers.get("Host", "localhost")}')
            if self.headers.get('Origin') != expected_origin or not hmac.compare_digest(self.headers.get('X-CSRF-Token', ''), state.digest('csrf'+owner)):
                return self.send(403, {'error': 'Session or origin validation failed. Reload the page.'})
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 8192 or self.headers.get('Content-Type') != 'application/json':
                return self.send(400, {'error': 'Expected a small JSON request.'})
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('Expected an object.')
            path = urlsplit(self.path).path
            if path == '/api/tasks':
                if not SLOTS.acquire(blocking=False):
                    return self.send(429, {'error': 'Planner is busy. Please try again shortly.'})
                try:
                    tid = state.create_task(data.get('objective'), owner, data.get('budget', 180), data.get('daypart', 'morning'), data.get('manual_minutes', 35), MODE)
                    POOL.submit(background, tid, owner)
                except Exception:
                    SLOTS.release()
                    raise
                return self.send(202, {'id': tid})
            if path == '/api/decision':
                status = state.decide(data['task_id'], data['proposal_id'], owner, data['approved'], data.get('attention_seconds', 0))
                # Stop here: UI shows APPROVED before requesting a resume.
                return self.send(200, {'status': status})
            if path == '/api/resume':
                state.execute(data['task_id'], owner)
                return self.send(200, state.snapshot(data['task_id'], owner))
            if path == '/api/verify':
                state.verify(data['task_id'], owner)
                return self.send(200, state.snapshot(data['task_id'], owner))
            self.send(404, {'error': 'Not found'})
        except PermissionError:
            self.send(404, {'error': 'Workflow not found'})
        except (ValueError, KeyError, TypeError):
            self.send(409, {'error': 'Request is invalid or the workflow state changed. Refresh and check the audit trail.'})
        except Exception:
            self.send(500, {'error': 'Operation failed. Refresh to inspect durable state before retrying.'})


def main():
    state.recover_interrupted_planning()
    address = (os.getenv('HOST', '127.0.0.1'), int(os.getenv('PORT', '8080')))
    print(f'DecisionPilot AI: http://{address[0]}:{address[1]} ({MODE}; simulated bookings)', flush=True)
    ThreadingHTTPServer(address, Handler).serve_forever()


if __name__ == '__main__':
    main()
