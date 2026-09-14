# Phase 6 — Orchestrator

**Status:** ⬜ Not started

## What This Phase Covers
Tying every previous phase together into a single command that runs load testing, infrastructure chaos, and security testing as one coordinated suite, and produces one combined pass/fail readiness verdict. This is what turns the project from "a collection of separate scripts" into an actual **system** — the core product being demonstrated.

## What To Do
1. Write a Python controller script (e.g. `orchestrator.py`) that, in sequence or in coordinated parallel:
   - Triggers the Phase 3 k6 load test (via subprocess call to `k6 run`, or the k6 Cloud/API if used)
   - Triggers the Phase 4 Chaos Mesh experiment (via `kubectl apply` on the chaos manifest, timed to overlap with the load test)
   - Triggers the Phase 5 brute-force script against `/login`
2. Collect the outputs of all three (k6 summary JSON, chaos experiment status, brute-force result counts) into one place
3. Define explicit **pass/fail thresholds** for each pillar, e.g.:
   - Load: p95 latency must stay under X ms and error rate under Y% at target VU count
   - Chaos: pod replacement must complete within Z seconds and success rate must not drop below W% during the kill window
   - Security: brute-force must be blocked within N attempts
4. Aggregate the three results into a single readiness verdict (e.g., PASS if all three pass, FAIL with a listed reason if any one fails)
5. Print/save a final readiness report (console output and/or a JSON/Markdown file) summarizing all three results and the overall verdict

## What To Expect
- Running `python orchestrator.py` (or similar) executes the full suite end-to-end without manual intervention between phases
- A single, clear output: e.g.
  ```
  Load Test:      PASS (p95: 1.4s @ 300 VUs, threshold 2s)
  Chaos Recovery: PASS (recovered in 4.2s, threshold 10s)
  Security:       PASS (blocked at attempt 18, threshold 20)
  OVERALL:        PASS — application is ready to publish
  ```
- This is the artifact that makes the "pre-publish gate" framing literal rather than metaphorical

## Contribution to the Overall System
This is the actual **product** of the project. The individual phases (3, 4, 5) are components; this phase is what makes them a coherent tool. It's also what would plug into Phase 7's CI/CD gate, since a CI pipeline needs a single exit code / pass-fail signal, not three separate scripts to interpret manually.

## Code / Function Reference
- `orchestrator.py` — main controller; functions likely include `run_load_test()`, `run_chaos_experiment()`, `run_security_test()`, `score_results()`, `generate_report()`
- Reads/writes the JSON result files produced by Phases 3–5
- Output: `readiness_report.md` or `readiness_report.json` — the final combined verdict

## How It Fits the Architecture
Maps to the **Orchestrator (future)** row of the architecture table. It sits above and coordinates the Load generation, Infrastructure chaos, and Security/threat simulation rows, and its output is what Phase 7's CI/CD gate would consume.
