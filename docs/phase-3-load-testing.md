# Phase 3 — Load Testing (k6)

**Status:** 🔄 In progress (setup done, first real run pending)

## What This Phase Covers
Finding the target application's actual breaking point under realistic and increasing traffic — the "handle stress" pillar. This produces the first hard, real number in the project.

## What To Do
1. Write a k6 script (e.g. `load_test.js`) that targets the `/data` endpoint of the deployed app (via the Kubernetes Service, exposed through `kubectl port-forward` or a NodePort/Minikube tunnel)
2. Define a **ramping load profile** in the script — start low (e.g. 10 virtual users), step up over stages (e.g. 10 → 50 → 100 → 300 → 500), holding each stage for a fixed duration
3. Configure k6 thresholds (e.g. `http_req_duration: p(95)<2000`) so the script can programmatically flag when performance degrades past an acceptable bound
4. Run the script: `k6 run load_test.js`
5. Re-run at least once with a plain baseline (no chaos, no attack) to establish the app's *unstressed* ceiling before Phase 4 combines this with pod kills

## What To Expect
- A k6 summary output showing requests/sec, response time percentiles (p50/p95/p99), and error rate at each load stage
- A concrete "breaking point" — e.g., "response time exceeds 2 seconds past ~300 concurrent virtual users" or "error rate exceeds 5% at 400 VUs"
- This number becomes a fixed reference point: Phase 4 will re-run a similar load *while* killing pods, to see whether the breaking point gets worse under combined stress

## Contribution to the Overall System
This is the first of your three pillars ("handle stress") turned into evidence. It also acts as the control/baseline that Phase 4's combined chaos+load experiment is measured against — without this baseline, you can't claim chaos made things worse, because you won't know what "normal" looked like.

## Code / Function Reference
- `load_test.js` — k6 script: ramping VU stages, thresholds, targets `/data` (and optionally `/health`)
- Output: raw k6 summary (save with `k6 run --summary-export=results_phase3.json load_test.js`) for later comparison in Phase 8

## How It Fits the Architecture
Maps to the **Load generation (k6)** row. Its output feeds directly into Phase 4 (as the "load" half of the combined chaos+load experiment) and into Phase 6 (as one of the orchestrator's scored inputs).
