#!/usr/bin/env python3
"""Send a PR diff to NVIDIA NIM and emit a markdown security-review report."""

import json
import os
import sys
from urllib.request import Request, urlopen

MODEL = os.environ.get("NIM_MODEL", "nvidia/llama-3.3-nemotron-super-49b-v1.5")
ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"
MAX_DIFF_CHARS = 80_000

diff = open(sys.argv[1]).read()
if len(diff) > MAX_DIFF_CHARS:
    diff = diff[:MAX_DIFF_CHARS] + "\n\n[diff truncated]"

system = "You are a senior application-security engineer performing a focused code review."

user = f"""Review the following pull-request diff for security issues.

For every issue, output one bullet:
- **Severity:** critical | high | medium | low | info
- **Location:** file:line
- **Issue:** short description
- **Fix:** concrete remediation

Cover:
- Injection (SQL, command, XSS, SSRF, path traversal, template, LDAP)
- Authentication / authorization flaws (missing checks, IDOR, priv-esc)
- Hardcoded secrets, credentials, tokens, API keys
- Cryptographic misuse (weak algorithms, hardcoded keys, bad randomness)
- Unsafe deserialization (pickle, yaml.load, eval, exec)
- Insecure input validation and unsafe redirects
- Sensitive data exposure in logs / errors / responses
- Race conditions / TOCTOU
- Dependency or supply-chain red flags

Group findings under `### Critical`, `### High`, `### Medium`, `### Low`, `### Info`.
End with one line: `**Verdict:** SAFE TO MERGE | CHANGES REQUESTED | BLOCK`.

```diff
{diff}
```
"""

body = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ],
    "temperature": 0.2,
    "top_p": 0.9,
    "max_tokens": 4096,
}

req = Request(
    ENDPOINT,
    data=json.dumps(body).encode(),
    headers={
        "Authorization": f"Bearer {os.environ['NVIDIA_API_KEY']}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    },
)

with urlopen(req, timeout=180) as resp:
    payload = json.loads(resp.read())

content = payload["choices"][0]["message"]["content"]

print("## NIM Security Review")
print(f"_Model: `{MODEL}` via NVIDIA NIM_\n")
print(content)
