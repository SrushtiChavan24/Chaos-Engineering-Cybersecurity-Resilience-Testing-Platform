# Phase 0 — Environment Setup

**Status:** ✅ Done

## What This Phase Covers
Standing up the local toolchain needed to build, containerize, and orchestrate the target application before any testing logic exists. Nothing in later phases (load testing, chaos injection, security testing) can run without this foundation working correctly.

## What To Do
- Install and verify Docker (Docker Desktop with WSL2 backend on Windows, or native Docker Engine on Linux)
- Install Python 3.x and set up a virtual environment (`venv`) for all Python tooling used later (Flask app, `bruteforce_test.py`, orchestrator script)
- Install Minikube (local single-node Kubernetes cluster) and `kubectl` (Kubernetes CLI)
- Confirm WSL2 distro alignment if on Windows — make sure VS Code, Docker, and the terminal are all pointed at the *same* Ubuntu distro, not Docker's internal `docker-desktop` distro
- Add your user to the `docker` group so Docker commands don't require `sudo` every time
- Verify everything with basic sanity commands: `docker --version`, `minikube status`, `kubectl version --client`, `python3 --version`

## What To Expect
A working local machine where:
- `docker run hello-world` succeeds without permission errors
- `minikube start` brings up a healthy single-node cluster
- `kubectl get nodes` shows that node as `Ready`
- A Python venv activates cleanly and installs packages without system-permission errors

No application code exists yet — this phase produces *infrastructure readiness*, not a running app.

## Contribution to the Overall System
This is the foundation layer everything else sits on. Every later phase — the Flask app, Kubernetes deployment, k6 load tests, Chaos Mesh experiments, security scripts — depends on Docker and Kubernetes being correctly installed and reachable from the same environment. Time spent here prevents cascading environment failures later.

## Known Issues Solved Here (worth keeping in your report)
- `ModuleNotFoundError` caused by VS Code's selected Python interpreter not matching the activated terminal venv → fixed by explicitly selecting the venv interpreter in VS Code
- Debian/Ubuntu `externally-managed-environment` (PEP 668) blocking `pip install` → fixed by always installing inside the venv instead of forcing a system-wide install
- `sudo apt install` hanging on a dpkg lock → fixed by resolving the lock (checking for a stuck `apt`/`dpkg` process) before retrying
- `permission denied on docker.sock` → fixed by adding the user to the `docker` group and restarting the session
- WSL distro mismatch (VS Code Remote connecting to Docker's internal `docker-desktop` distro instead of the real Ubuntu distro) → fixed by explicitly selecting the correct distro in the WSL/Remote connection

## How It Fits the Architecture
Phase 0 has no direct component in the architecture table — it's the substrate the "Containerization" (Docker) and "Orchestration" (Kubernetes) rows depend on. Every subsequent phase assumes this environment is stable and correctly configured.
