from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({"status": "ok", "service": "demo-app"})


@app.route("/healthz")
def healthz():
    return jsonify({"healthy": True})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
