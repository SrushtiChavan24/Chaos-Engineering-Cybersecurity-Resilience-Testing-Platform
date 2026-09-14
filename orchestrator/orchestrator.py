"""
Orchestrator — runs the full resilience + security test suite against
the target application and produces a single readiness report.

What it does, in order:
  1. Starts the k6 load test in the background
  2. While load is running, applies the Chaos Mesh pod-kill experiment
  3. Waits for the load test to finish, collects its JSON summary
  4. Runs the brute-force security test ("before" run)
  5. Compares results against defined thresholds
  6. Writes results/readiness_report.md with a pass/fail verdict

Requirements: kubectl and k6 must be on PATH, the app must already be
deployed (see README.md Quick start steps 1-4), and this script must be
run from the orchestrator/ folder (or adjust the RESULTS_DIR path).

Usage:
    python orchestrator.py --base-url http://<minikube-service-url>
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# ---- Thresholds — edit these to define what "ready to publish" means ----
THRESHOLDS = {
    "max_http_failure_rate": 0.05,     # 5% of requests may fail
    "max_p95_latency_ms": 500,         # 95th percentile latency ceiling
    "max_pod_recovery_seconds": 15,    # how fast a killed pod must be replaced
    "max_bruteforce_processed": 30,    # max attempts allowed through before blocking
}


def run(cmd, **kwargs):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=False, **kwargs)


def run_load_test(base_url: str):
    """Runs k6 in the background so chaos can be injected mid-test."""
    load_test_path = ROOT / "load-testing" / "load_test.js"
    print("\n=== Phase 3: Starting load test (background) ===")
    proc = subprocess.Popen(
        ["k6", "run", "--env", f"BASE_URL={base_url}", str(load_test_path)],
        cwd=str(ROOT / "load-testing"),
    )
    return proc


def trigger_chaos():
    """Applies the pod-kill experiment partway through the load test."""
    print("\n=== Phase 4: Waiting 20s into load test, then killing a pod ===")
    time.sleep(20)
    chaos_file = ROOT / "chaos" / "podchaos.yaml"
    start = time.time()
    run(["kubectl", "apply", "-f", str(chaos_file)])

    # Poll pod count until it returns to 3 (recovered) or we time out
    recovered_at = None
    timeout = 60
    while time.time() - start < timeout:
        result = subprocess.run(
            ["kubectl", "get", "pods", "-l", "app=target-app",
             "--field-selector=status.phase=Running", "-o", "name"],
            capture_output=True, text=True,
        )
        running_count = len([l for l in result.stdout.splitlines() if l.strip()])
        if running_count >= 3:
            recovered_at = time.time()
            break
        time.sleep(1)

    recovery_seconds = round(recovered_at - start, 2) if recovered_at else None
    print(f"Pod recovery time: {recovery_seconds}s" if recovery_seconds else "Pod did not recover within timeout")
    return {"pod_recovery_seconds": recovery_seconds}


def run_security_test(base_url: str, label: str):
    print(f"\n=== Phase 5: Running brute-force test ({label}) ===")
    output_path = RESULTS_DIR / f"security_{label}.json"
    script = ROOT / "security" / "bruteforce_test.py"
    run([
        sys.executable, str(script),
        "--url", base_url,
        "--attempts", "200",
        "--output", str(output_path),
    ])
    with open(output_path) as f:
        return json.load(f)


def load_k6_summary():
    summary_path = RESULTS_DIR / "results_phase3.json"
    if not summary_path.exists():
        print("Warning: k6 summary not found, skipping load-test scoring")
        return None
    with open(summary_path) as f:
        return json.load(f)


def score_and_report(k6_summary, chaos_result, security_before, security_after=None):
    lines = ["# Readiness Report\n"]
    verdicts = []

    # --- Load / stress scoring ---
    lines.append("## Stress / Load Test\n")
    if k6_summary:
        metrics = k6_summary.get("metrics", {})
        fail_rate = metrics.get("http_req_failed", {}).get("values", {}).get("rate", None)
        p95 = metrics.get("http_req_duration", {}).get("values", {}).get("p(95)", None)
        if fail_rate is not None:
            ok = fail_rate <= THRESHOLDS["max_http_failure_rate"]
            verdicts.append(ok)
            lines.append(f"- HTTP failure rate: {fail_rate:.2%} "
                          f"(threshold: {THRESHOLDS['max_http_failure_rate']:.0%}) "
                          f"— {'PASS' if ok else 'FAIL'}")
        if p95 is not None:
            ok = p95 <= THRESHOLDS["max_p95_latency_ms"]
            verdicts.append(ok)
            lines.append(f"- p95 latency: {p95:.1f}ms "
                          f"(threshold: {THRESHOLDS['max_p95_latency_ms']}ms) "
                          f"— {'PASS' if ok else 'FAIL'}")
    else:
        lines.append("- No load test data available.")
    lines.append("")

    # --- Chaos / integrity scoring ---
    lines.append("## Infrastructure Chaos / Integrity\n")
    recovery = chaos_result.get("pod_recovery_seconds")
    if recovery is not None:
        ok = recovery <= THRESHOLDS["max_pod_recovery_seconds"]
        verdicts.append(ok)
        lines.append(f"- Pod recovery time: {recovery}s "
                      f"(threshold: {THRESHOLDS['max_pod_recovery_seconds']}s) "
                      f"— {'PASS' if ok else 'FAIL'}")
    else:
        verdicts.append(False)
        lines.append("- Pod did not recover within timeout — FAIL")
    lines.append("")

    # --- Security scoring ---
    lines.append("## Security / Threat Resilience\n")
    lines.append(f"- Before hardening: {security_before['processed_by_server']} of "
                  f"{security_before['total_attempts']} attempts processed "
                  f"(blocked: {security_before['blocked']})")
    if security_after:
        ok = security_after["processed_by_server"] <= THRESHOLDS["max_bruteforce_processed"]
        verdicts.append(ok)
        lines.append(f"- After hardening: {security_after['processed_by_server']} of "
                      f"{security_after['total_attempts']} attempts processed "
                      f"(blocked: {security_after['blocked']}) "
                      f"— {'PASS' if ok else 'FAIL'}")
    else:
        lines.append("- No 'after' run yet. Enable RATE_LIMIT_ENABLED, redeploy, "
                      "and re-run with --security-after to complete this section.")
    lines.append("")

    # --- Overall verdict ---
    overall = "READY TO PUBLISH" if verdicts and all(verdicts) else "NOT READY — see failures above"
    lines.insert(1, f"**Overall verdict: {overall}**\n")

    report_path = RESULTS_DIR / "readiness_report.md"
    report_path.write_text("\n".join(lines))
    print(f"\nReadiness report written to {report_path}")
    print(f"\nOVERALL VERDICT: {overall}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True, help="Live URL of the deployed app")
    parser.add_argument("--security-after", action="store_true",
                         help="Also run the 'after hardening' security test "
                              "(run this AFTER setting RATE_LIMIT_ENABLED=true and redeploying)")
    args = parser.parse_args()

    load_proc = run_load_test(args.base_url)
    chaos_result = trigger_chaos()
    load_proc.wait()  # wait for k6 to finish its full ramp

    security_before = run_security_test(args.base_url, "before")

    security_after = None
    if args.security_after:
        security_after = run_security_test(args.base_url, "after")

    k6_summary = load_k6_summary()
    score_and_report(k6_summary, chaos_result, security_before, security_after)


if __name__ == "__main__":
    main()
