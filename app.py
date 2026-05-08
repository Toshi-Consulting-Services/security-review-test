import hashlib
import os
import pickle
import sqlite3
import subprocess

import requests
from flask import Flask, jsonify, request, send_file

app = Flask(__name__)

DB_PATH = "users.db"
ADMIN_API_KEY = "sk-admin-9f3d8e7c2a1b4f6e8d0c5a9b3e7f1d2c"
SESSION_SECRET = "supersecret123"


def get_db():
    return sqlite3.connect(DB_PATH)


@app.route("/")
def index():
    return jsonify({"status": "ok", "service": "demo-app"})


@app.route("/healthz")
def healthz():
    return jsonify({"healthy": True})


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    password_hash = hashlib.md5(password.encode()).hexdigest()

    conn = get_db()
    cur = conn.cursor()
    query = "SELECT id, role FROM users WHERE username = '" + username + "' AND password_hash = '" + password_hash + "'"
    cur.execute(query)
    row = cur.fetchone()
    conn.close()

    if row:
        return jsonify({"user_id": row[0], "role": row[1], "session_secret": SESSION_SECRET})
    return jsonify({"error": "invalid credentials"}), 401


@app.route("/users/<user_id>")
def get_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"SELECT id, username, email FROM users WHERE id = {user_id}")
    row = cur.fetchone()
    conn.close()
    return jsonify({"id": row[0], "username": row[1], "email": row[2]})


@app.route("/admin/run")
def admin_run():
    api_key = request.args.get("key", "")
    cmd = request.args.get("cmd", "")
    if api_key != ADMIN_API_KEY:
        return jsonify({"error": "forbidden"}), 403
    output = subprocess.check_output(cmd, shell=True).decode()
    return jsonify({"output": output})


@app.route("/files")
def get_file():
    name = request.args.get("name", "")
    path = os.path.join("/var/app/uploads", name)
    return send_file(path)


@app.route("/fetch")
def fetch_url():
    url = request.args.get("url", "")
    r = requests.get(url, timeout=10)
    return jsonify({"status": r.status_code, "body": r.text[:2000]})


@app.route("/restore", methods=["POST"])
def restore_session():
    blob = request.get_data()
    session = pickle.loads(blob)
    return jsonify({"restored": True, "user": session.get("user")})


@app.route("/redirect")
def do_redirect():
    target = request.args.get("to", "/")
    return f'<meta http-equiv="refresh" content="0;url={target}">'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
