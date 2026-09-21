# Chaos Engineering + Cybersecurity Resilience Testing Platform

A pre-publish resilience and security readiness gate for web applications, deploys a target app into an isolated environment and deliberately subjects it to load, infrastructure failure, and simulated attack, producing a single pass/fail readiness verdict.

See `PROJECT_SUMMARY.md` for the full project explanation, and the individual `phase-*.md` files for phase-by-phase implementation details.

## Requirements

### System Requirements
- Linux, macOS, or Windows with WSL2
- At least 8 GB RAM available (Minikube + multiple pods + load generation)
- Docker installed and running
- `sudo`/admin access for initial tool installation

### Tech Stack
| Layer | Tool | Purpose |
|---|---|---|
| Language | Python 3.x | Target app, test scripts, orchestrator |
| Web framework | Flask | Target application under test |
| Containerization | Docker | Packaging the target app |
| Orchestration | Kubernetes (Minikube) | Running/self-healing the app |
| Cluster CLI | kubectl | Interacting with the cluster |
| Load testing | k6 | Traffic/stress simulation |
| Chaos engineering | Chaos Mesh | Infrastructure failure injection |
| Security testing | Custom Python (`bruteforce_test.py`), optionally OWASP ZAP | Attack simulation |
| Observability | Prometheus + Grafana, or custom logging | Metrics/visibility during tests |
| CI/CD (optional) | GitHub Actions | Automated readiness gate |

### Python Dependencies
Install inside a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r app/requirements.txt
```
`requirements.txt` should include (adjust to what you actually use): `flask`, `requests`, `flask-limiter` (for Phase 5 rate limiting), `prometheus-client` (if using Phase 2 Option A).

## How to Run

### 1. Start the cluster
```bash
minikube start
kubectl get nodes   # confirm cluster is Ready
```

### 2. Build and deploy the target app
```bash
docker build -t resilience-target-app:latest .
minikube image load resilience-target-app:latest
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get pods    # confirm 3 replicas Running
```

### 3. (Optional) Set up observability
```bash
# If using Prometheus/Grafana via Helm, adjust to your actual setup
helm install prometheus prometheus-community/kube-prometheus-stack
```

### 4. Run the load test
```bash
k6 run load_test.js --summary-export=results_phase3.json
```

### 5. Run the combined chaos + load test
```bash
kubectl apply -f chaos/podchaos.yaml
k6 run load_test.js --summary-export=results_phase4.json
```

### 6. Run the security test (before and after adding rate limiting)
```bash
python bruteforce_test.py --target http://<service-url>/login   # before fix
# apply rate limiting in app.py, redeploy
kubectl rollout restart deployment/<deployment-name>
python bruteforce_test.py --target http://<service-url>/login   # after fix
```

### 7. Run the full orchestrator
```bash
python orchestrator.py
```

### 8. (Optional) Trigger the CI/CD gate
Push to the configured branch, or manually trigger the `resilience-gate.yml` workflow from the GitHub Actions tab.

## Expected Outcome
Running the orchestrator end-to-end should produce a single readiness report similar to:
```
Load Test:      PASS/FAIL (p95 latency, error rate vs. threshold)
Chaos Recovery: PASS/FAIL (pod recovery time, success rate during kill vs. threshold)
Security:       PASS/FAIL (attempts before block vs. threshold)
OVERALL:        PASS/FAIL (application is/is not ready to publish)
```

This report, along with the individual phase results (`results_phase3.json`, `results_phase4.json`, before/after security numbers), is the evidence base for the final project documentation (see `phase-8-documentation.md`).

## Project Status
Currently ~35–40% complete. Phases 0, 1, and 1b are done. Phases 3 and 4 are in progress. See `PROJECT_SUMMARY.md` for the full roadmap table.
