"""Intentionally vulnerable patterns to exercise Toshi SCR scanners.

This file is a scanner test target — Semgrep should flag the SQL/SSRF/eval
patterns, Gitleaks should flag the hardcoded credentials, and Trivy should
flag flask==2.0.0 in requirements.txt for known CVEs.
"""

import os
import sqlite3
import subprocess
from urllib.request import urlopen

from flask import Flask, request

app = Flask(__name__)

# (Secrets removed — GitHub push protection blocks committing realistic
# credential strings. Gitleaks will be tested separately via a runtime
# tarball ingestion.)


@app.route("/login")
def login():
    user = request.args.get("user", "")
    pwd = request.args.get("pwd", "")
    # Semgrep: SQL injection via string concatenation
    q = "SELECT * FROM users WHERE name='" + user + "' AND password='" + pwd + "'"
    con = sqlite3.connect("/tmp/app.db")
    row = con.execute(q).fetchone()
    return {"row": row}


@app.route("/run")
def run():
    cmd = request.args.get("cmd", "ls")
    # Semgrep: command injection via shell=True with user input
    out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return {"out": out.stdout}


@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")
    # Semgrep: SSRF — unvalidated user URL passed to urlopen
    return {"body": urlopen(url).read()[:200].decode(errors="ignore")}


@app.route("/calc")
def calc():
    expr = request.args.get("e", "1+1")
    # Semgrep: dangerous eval on user input
    return {"value": eval(expr)}
# touch 1778574718
# trigger 1778576157
