"""
Simulates a brute-force login attack against the target app.

Usage:
    python bruteforce_test.py --url http://127.0.0.1:5000 --attempts 200 \
        --output ../results/security_before.json

Run once before enabling RATE_LIMIT_ENABLED (output to security_before.json),
then again after enabling it and redeploying (output to security_after.json).
The orchestrator compares the two automatically.
"""

import argparse
import json
import time
import requests


def run_attack(base_url: str, attempts: int) -> dict:
    blocked = 0
    processed = 0
    errors = 0
    start = time.time()

    for i in range(attempts):
        try:
            resp = requests.post(
                f"{base_url}/login",
                json={"username": "admin", "password": f"guess{i}"},
                timeout=3,
            )
            if resp.status_code == 429:
                blocked += 1
            else:
                processed += 1
        except requests.exceptions.RequestException:
            errors += 1

    elapsed = time.time() - start
    result = {
        "total_attempts": attempts,
        "processed_by_server": processed,
        "blocked": blocked,
        "network_errors": errors,
        "elapsed_seconds": round(elapsed, 2),
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:5000")
    parser.add_argument("--attempts", type=int, default=200)
    parser.add_argument("--output", default=None, help="path to write JSON result")
    args = parser.parse_args()

    result = run_attack(args.url, args.attempts)

    print("\n--- Brute-force simulation results ---")
    for k, v in result.items():
        print(f"{k}: {v}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\nResult written to {args.output}")
