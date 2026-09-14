# Phase 1 — Target Application: Build & Deploy

**Status:** ✅ Done

## What This Phase Covers
Building the actual "application under test" and getting it running inside Kubernetes with multiple replicas. This app is the *subject* of every experiment in later phases — it is not the testing tool itself, it's what gets stressed, broken, and attacked.

## What To Do
1. Write a minimal Flask application (`app.py`) exposing at least three endpoints:
   - `/health` — a liveness/readiness check endpoint
   - `/data` — a representative "normal work" endpoint that simulates real application load
   - `/login` — an authentication endpoint (intentionally left without protections at this stage — it becomes the security-testing target in Phase 5)
2. Write a `Dockerfile` that packages the Flask app and its dependencies into a container image
3. Build the image and load it into Minikube's local image registry (`minikube image load` or by pointing your Docker daemon at Minikube's)
4. Write a Kubernetes `Deployment` manifest specifying **3 replicas** of the app, plus a `Service` manifest to expose it inside the cluster
5. Apply the manifests with `kubectl apply -f` and confirm all 3 pods reach `Running` state

## What To Expect
- `kubectl get pods` shows 3 pods for the app, all `Running` and `Ready`
- `kubectl get svc` shows a Service routing traffic to those pods
- Hitting `/health` and `/data` (via `kubectl port-forward` or the Service) returns successful responses
- `/login` accepts POST requests but has no rate limiting or brute-force protection yet — this is intentional and gets exploited/fixed in Phase 5

## Contribution to the Overall System
This is the **target**, not the **tester**. Every other phase acts *on* this app:
- Phase 3 (load testing) sends traffic at `/data`
- Phase 4 (chaos) kills its pods
- Phase 5 (security) attacks `/login`
- Phase 6 (orchestrator) measures all of the above against this same deployment

Having it running on 3 replicas (not 1) is what makes Kubernetes self-healing and load distribution meaningful to test in the first place.

## Code / Function Reference
- `app.py` — Flask app defining `/health`, `/data`, `/login`
- `Dockerfile` — builds the container image for `app.py`
- `k8s/deployment.yaml` — Deployment spec, `replicas: 3`
- `k8s/service.yaml` — Service exposing the Deployment inside the cluster

## How It Fits the Architecture
Maps directly to the **Target application** and **Containerization** rows of the architecture table, and is the first concrete instance of the **Orchestration (Kubernetes)** row. Everything downstream references this Deployment/Service by name.
