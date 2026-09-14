# Phase 4 — Infrastructure Chaos (Chaos Mesh)

**Status:** 🔄 In progress (Chaos Mesh install/permissions being resolved)

## What This Phase Covers
Deliberately injecting infrastructure failure — starting with pod kills — *while the app is under load from Phase 3* to test the "maintain integrity during stress" pillar. This is where "self-healing" (Phase 1b) gets tested under realistic, adverse conditions instead of in isolation.

## What To Do
1. Install Chaos Mesh into the Minikube cluster (via Helm), and resolve any RBAC/permission issues so its controller can create/manage chaos experiments in your namespace
2. Define a `PodChaos` experiment manifest that kills one (or a percentage) of the app's pods, either once or on a repeating schedule
3. Run the Phase 3 k6 load test and the Chaos Mesh pod-kill experiment **at the same time**, targeting the same Deployment
4. Capture: how the app's success rate, latency, and error rate behave during the kill window, and how long it takes for the replacement pod to become `Ready` and start receiving traffic again *while load is still being generated*
5. Repeat the same experiment with different intensities (kill 1 pod vs. kill 2 of 3) if time allows, for a richer before/after comparison

## What To Expect
- A concrete answer to: "Does self-healing still work fast enough when the app is also under heavy load?"
- A likely-measurable dip in success rate / latency spike during the pod-kill window, followed by recovery once the replacement pod is Ready
- A comparison point against the Phase 3 baseline — e.g., "p95 latency was 800ms under load alone, but spiked to 3.2s for ~6 seconds during the pod kill, before recovering"

## Contribution to the Overall System
This is the second pillar ("integrity under stress") turned into evidence, and it directly builds on Phase 1b and Phase 3: it's the same self-healing behavior, but now proven under the exact conditions a production incident would actually look like (traffic + failure at the same time), not in isolation.

## Code / Function Reference
- `chaos/podchaos.yaml` — Chaos Mesh `PodChaos` experiment manifest (target selector, kill mode, schedule/duration)
- Re-uses `load_test.js` from Phase 3, run concurrently with the chaos experiment
- Output: k6 summary during the chaos window (`results_phase4.json`) for direct comparison against `results_phase3.json`

## How It Fits the Architecture
Maps to the **Infrastructure chaos (Chaos Mesh)** row, and is explicitly the point where the **Load generation** and **Orchestration** rows are exercised together rather than separately. This combined result is one of the key inputs to the Phase 6 orchestrator's scoring.
