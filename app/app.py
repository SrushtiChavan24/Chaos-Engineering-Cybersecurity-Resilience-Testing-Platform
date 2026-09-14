"""
Target application under test.

Endpoints:
  GET  /health           -> liveness/readiness probe target
  GET  /data              -> simulates real backend work
  POST /login             -> deliberately testable auth endpoint
  GET  /login-attempts     -> introspection endpoint for the security test
  GET  /metrics            -> Prometheus metrics endpoint

Rate limiting on /login is OFF by default (RATE_LIMIT_ENABLED=false) so
Phase 5's "before" attack run has something real to break. Set the
environment variable RATE_LIMIT_ENABLED=true (and redeploy) to turn it
on for the "after" run.
"""

import os
import time
import random
from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "false").lower() == "true"

# ---- Prometheus metrics (Phase 2 observability) ----
REQUEST_COUNT = Counter(
    "app_requests_total", "Total requests", ["endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds", "Request latency", ["endpoint"]
)

# ---- Fake "database" of valid users ----
VALID_USERS = {"admin": "supersecret123"}

# ---- In-memory login-attempt tracking (used for both rate limiting and
# for the security test's introspection endpoint) ----
login_attempts = {}          # ip -> total attempts ever
login_attempts_window = {}   # ip -> (window_start_time, count_in_window)

RATE_LIMIT_MAX = 5           # max attempts allowed per window
RATE_LIMIT_WINDOW_SECONDS = 60


def is_rate_limited(ip: str) -> bool:
    if not RATE_LIMIT_ENABLED:
        return False
    now = time.time()
    window_start, count = login_attempts_window.get(ip, (now, 0))
    if now - window_start > RATE_LIMIT_WINDOW_SECONDS:
        # window expired, reset it
        login_attempts_window[ip] = (now, 1)
        return False
    if count >= RATE_LIMIT_MAX:
        return True
    login_attempts_window[ip] = (window_start, count + 1)
    return False


@app.route("/health")
def health():
    REQUEST_COUNT.labels(endpoint="/health", status="200").inc()
    return jsonify(status="ok"), 200


@app.route("/data")
def data():
    start = time.time()
    time.sleep(random.uniform(0.05, 0.2))  # simulate processing time
    if random.random() < 0.01:             # 1% baseline random failure
        REQUEST_COUNT.labels(endpoint="/data", status="500").inc()
        REQUEST_LATENCY.labels(endpoint="/data").observe(time.time() - start)
        return jsonify(error="internal error"), 500

    REQUEST_COUNT.labels(endpoint="/data", status="200").inc()
    REQUEST_LATENCY.labels(endpoint="/data").observe(time.time() - start)
    return jsonify(message="here is your data", value=random.randint(1, 100))


@app.route("/login", methods=["POST"])
def login():
    ip = request.remote_addr
    login_attempts[ip] = login_attempts.get(ip, 0) + 1

    if is_rate_limited(ip):
        REQUEST_COUNT.labels(endpoint="/login", status="429").inc()
        return jsonify(status="blocked", message="too many attempts"), 429

    body = request.get_json(force=True, silent=True) or {}
    username = body.get("username", "")
    password = body.get("password", "")

    if VALID_USERS.get(username) == password:
        REQUEST_COUNT.labels(endpoint="/login", status="200").inc()
        return jsonify(status="success", message="logged in"), 200

    REQUEST_COUNT.labels(endpoint="/login", status="401").inc()
    return jsonify(status="failure", message="invalid credentials"), 401


@app.route("/login-attempts")
def get_attempts():
    return jsonify(login_attempts)


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
