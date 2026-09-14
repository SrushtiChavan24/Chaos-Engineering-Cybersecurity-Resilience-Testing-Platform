"""
Lightweight observability — an alternative to running full
Prometheus/Grafana locally. Continuously polls the app's /health
endpoint and logs timestamp, response time, and success/failure to a
CSV file. Good enough to prove uptime/latency behavior during chaos
experiments without the overhead of the full monitoring stack.

Usage:
    python log_parser.py --url http://127.0.0.1:5000 --duration 120 \
        --output ../results/uptime_log.csv

Run this in its own terminal while you run the load test / chaos
experiment in others — it keeps recording independently.
"""

import argparse
import csv
import time
import requests


def monitor(base_url: str, duration: int, output: str):
    end_time = time.time() + duration
    with open(output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "response_time_ms", "success"])
        while time.time() < end_time:
            t0 = time.time()
            try:
                resp = requests.get(f"{base_url}/health", timeout=3)
                success = resp.status_code == 200
            except requests.exceptions.RequestException:
                success = False
            elapsed_ms = round((time.time() - t0) * 1000, 2)
            writer.writerow([time.time(), elapsed_ms, success])
            f.flush()
            time.sleep(1)
    print(f"Monitoring complete. Log written to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    parser.add_argument("--duration", type=int, default=120, help="seconds to monitor")
    parser.add_argument("--output", default="../results/uptime_log.csv")
    args = parser.parse_args()
    monitor(args.url, args.duration, args.output)
