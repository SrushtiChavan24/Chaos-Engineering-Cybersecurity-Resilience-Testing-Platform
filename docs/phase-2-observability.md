# Phase 2 — Observability

**Status:** ⬜ Not started

## What This Phase Covers
Giving yourself visibility into what's actually happening inside the cluster *while* later tests run. Without this, Phases 3–5 only produce end-results (pass/fail numbers) with no insight into *why* — no CPU/memory graphs, no request-latency-over-time view, no way to correlate "pod died at 14:32:07" with "latency spiked at 14:32:05."

## What To Do
Two viable approaches — pick one based on time budget:

**Option A — Full stack (stronger for the report, more setup time):**
1. Install Prometheus into the cluster (via Helm chart or manifests) to scrape metrics from the app and from Kubernetes itself (kube-state-metrics, node exporter)
2. Install Grafana and connect it to Prometheus as a data source
3. Build 1–2 dashboards: request rate/latency for the Flask app, pod count/restarts over time
4. Add basic instrumentation to `app.py` (e.g. `prometheus_client` middleware) so `/data` and `/login` expose request counters and latency histograms

**Option B — Lightweight custom logging (faster, still credible):**
1. Add structured logging to `app.py` (timestamp, endpoint, response time, status code) written to a file or stdout
2. Write a small script to tail/aggregate these logs during test runs into a simple CSV or plot

## What To Expect
- A dashboard (Option A) or a log/CSV trail (Option B) that shows request volume, latency, and pod health *over time*, not just a final number
- The ability to visually correlate events across phases — e.g., overlay the Phase 4 pod-kill timestamp on the Phase 3 latency graph

## Contribution to the Overall System
This phase doesn't test anything itself — it makes every other phase's results *legible and provable*. "Latency exceeded 2s at 300 concurrent users" (Phase 3) and "success rate dropped when a pod was killed under load" (Phase 4) are much stronger claims with a graph behind them than as a bare number.

## Code / Function Reference
- (Option A) `prometheus_client` integration in `app.py`; Helm values files for Prometheus/Grafana; Grafana dashboard JSON
- (Option B) a logging decorator/middleware in `app.py`; a `parse_logs.py` aggregation script

## How It Fits the Architecture
Maps to the **Observability** row of the architecture table. It sits "beside" the pipeline rather than in it — every other phase (3, 4, 5, 6) can optionally feed data into whatever you build here.
