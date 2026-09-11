"""Heuristic source scan. Never print matched secret values; not a substitute for secret scanning."""
from pathlib import Path
import re
import subprocess
import sys
root=Path(__file__).resolve().parents[1]
try:
    names=subprocess.check_output(['git','ls-files'],cwd=root,text=True,stderr=subprocess.DEVNULL).splitlines()
    paths=[root/p for p in names] if names else list(root.rglob('*'))
except (subprocess.CalledProcessError,FileNotFoundError):
    paths=list(root.rglob('*'))
patterns=[r'(?:AKIA|ASIA)[A-Z0-9]{16}',r'gh[pousr]_[A-Za-z0-9]{30,}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'(?i)aws_secret_access_key\s*[=:]\s*[\x22\x27]?[A-Za-z0-9/+=]{30,}']
ignore={'.git','.venv','__pycache__','.decisionpilot','upload'}
issues=[]
for p in paths:
    if not p.is_file() or any(part in ignore for part in p.relative_to(root).parts): continue
    if p.name=='.env' or p.suffix in ('.pem','.key','.db'): issues.append(str(p.relative_to(root)))
    if p.suffix.lower() in ('.png','.jpg','.zip','.pyc'): continue
    try: value=p.read_text()
    except (UnicodeError,OSError): continue
    if any(re.search(pattern,value) for pattern in patterns): issues.append(str(p.relative_to(root)))
if issues:
    print('Review potential secrets in:', ', '.join(sorted(set(issues))))
    sys.exit(1)
print('PASS: no credential patterns or sensitive runtime files found in scanned source.')
