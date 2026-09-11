import http.client
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from decisionpilot import state
from decisionpilot.server import Handler, ThreadingHTTPServer


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = state.DB_PATH
        state.DB_PATH = Path(self.tmp.name)/'http.db'
        state.init_db()
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.cookie = ''
        code, s, headers = self.request('GET','/api/session')
        self.cookie = headers['Set-Cookie'].split(';')[0]
        self.csrf = s['csrf']

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        state.DB_PATH = self.old
        self.tmp.cleanup()

    def request(self, method, path, body=None, headers=None):
        c=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        h={'Cookie':self.cookie, 'Origin':f'http://127.0.0.1:{self.port}', 'Content-Type':'application/json','X-CSRF-Token':getattr(self,'csrf','')}
        h.update(headers or {})
        c.request(method,path,body=json.dumps(body) if body is not None else None,headers=h)
        r=c.getresponse(); raw=r.read(); meta=dict(r.getheaders()); code=r.status;c.close()
        return code,json.loads(raw) if meta['Content-Type']=='application/json' else raw,meta

    def start(self):
        code,t,_=self.request('POST','/api/tasks',{'objective':'Schedule my annual car service under $180.'})
        self.assertEqual(code,202)
        for _ in range(40):
            _,s,_=self.request('GET','/api/tasks/'+t['id'])
            if s['status']!='PLANNING': return s
            time.sleep(.02)
        self.fail('Planning did not complete')

    def test_http_lifecycle(self):
        s=self.start();p=s['proposals'][-1];self.assertEqual(s['status'],'WAITING_FOR_HUMAN')
        self.assertEqual(self.request('POST','/api/resume',{'task_id':s['id']})[0],409)
        self.assertEqual(self.request('POST','/api/decision',{'task_id':s['id'],'proposal_id':p['id'],'approved':True,'attention_seconds':45})[0],200)
        self.assertEqual(self.request('POST','/api/resume',{'task_id':s['id']})[1]['status'],'VERIFYING')
        self.assertEqual(self.request('POST','/api/verify',{'task_id':s['id']})[1]['status'],'COMPLETED')

    def test_csrf_rejected(self):
        self.assertEqual(self.request('POST','/api/tasks',{}, {'X-CSRF-Token':'wrong'})[0],403)

    def test_foreign_origin_rejected(self):
        self.assertEqual(self.request('POST','/api/tasks',{}, {'Origin':'https://evil.example'})[0],403)

    def test_session_isolation(self):
        t=self.start()
        self.assertEqual(self.request('GET','/api/tasks/'+t['id'],headers={'Cookie':''})[0],404)

    def test_asset_and_security_headers(self):
        code,html,h=self.request('GET','/')
        self.assertEqual(code,200)
        self.assertIn(b'Approve simulated booking',html)
        self.assertIn("frame-ancestors 'none'",h['Content-Security-Policy'])
        self.assertIn('HttpOnly',self.request('GET','/api/session',headers={'Cookie':''})[2]['Set-Cookie'])

    def test_invalid_payload(self):
        self.assertEqual(self.request('POST','/api/tasks',{'objective':'x'})[0],409)
        self.assertEqual(self.request('POST','/api/tasks',[])[0],409)


if __name__=='__main__': unittest.main()
