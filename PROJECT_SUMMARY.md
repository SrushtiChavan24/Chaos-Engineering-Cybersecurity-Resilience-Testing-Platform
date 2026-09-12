# Project Summary : Chaos Engineering + Cybersecurity Resilience Testing Platform

## What This Project Is
A **pre-publish resilience and security readiness gate** for web applications. Before an app is published/deployed, this system deliberately puts it through three real-world conditions in a controlled, isolated environment with heavy traffic, infrastructure failure, and simulated cyberattack and produces a clear, evidence-backed verdict on whether the app is actually ready for real users.


## System Architecture
    chaos-resilience-platform/
    │
    ├── README.md
    ├── PROJECT_SUMMARY.md
    ├── requirements.txt
    ├── .gitignore
    │
    ├── docs/
    │   ├── phase-0-environment-setup.md
    │   ├── phase-1-target-app-deployment.md
    │   ├── phase-1b-self-healing-proof.md
    │   ├── phase-2-observability.md
    │   ├── phase-3-load-testing.md
    │   ├── phase-4-infrastructure-chaos.md
    │   ├── phase-5-security-testing.md
    │   ├── phase-6-orchestrator.md
    │   ├── phase-7-cicd-gate.md
    │   └── phase-8-documentation.md
    │
    ├── app/
    │   ├── app.py                  # Flask target app: /health, /data, /login
    │   ├── Dockerfile
    │   └── requirements.txt        # app-only deps (flask, flask-limiter, prometheus-client)
    │
    ├── k8s/
    │   ├── deployment.yaml          # 3-replica Deployment
    │   └── service.yaml
    │
    ├── chaos/
    │   └── podchaos.yaml            # Chaos Mesh PodChaos experiment
    │
    ├── load-testing/
    │   └── load_test.js             # k6 script (ramping VU stages)
    │
    ├── security/
    │   └── bruteforce_test.py       # brute-force attack simulation
    │
    ├── observability/               # Phase 2 — pick one path
    │   ├── prometheus-values.yaml   # if using Helm stack
    │   ├── grafana-dashboard.json
    │   └── log_parser.py            # if using lightweight logging instead
    │
    ├── orchestrator/
    │   └── orchestrator.py          # runs load+chaos+security, scores, reports
    │
    ├── results/                     # generated at runtime, not hand-written
    │   ├── results_phase3.json
    │   ├── results_phase4.json
    │   ├── security_before.json
    │   ├── security_after.json
    │   └── readiness_report.md
    │
    └── .github/
        └── workflows/
            └── resilience-gate.yml  # optional CI/CD gate (Phase 7)

## The Problem It Solves
Applications are typically only tested against the "happy path" like normal traffic, cooperative users, no failures. In production, three things inevitably happen:
1. Traffic behaves unpredictably (spikes, sustained heavy load)
2. Infrastructure fails (servers crash, dependencies become unavailable)
3. Attackers probe for weaknesses (brute-force logins, malformed requests)

Most teams only discover how their app handles these *after* launch, when something breaks in front of real users. This project causes all three conditions *before* launch, safely, and gives a pass/fail verdict backed by real numbers.

## The Three Pillars
| Pillar (your framing) | What it technically means | Proven in |
|---|---|---|
| "Handle stress" | Load/traffic resilience to have performance under heavy demand | Phase 3 (k6) |
| "Maintain integrity during stress" | Data consistency and correctness while stressed, not just staying online | Phase 4 (Chaos Mesh + k6 combined) |
| "Safe when a threat tries to enter" | Security resilience by detecting/resisting simulated attacks | Phase 5 (brute-force + rate limiting) |

## System Architecture
| Component | Role | Tool |
|---|---|---|
| Target application | The app under test | Flask app (`app.py`) : `/health`, `/data`, `/login` |
| Containerization | Packages the app portably | Docker |
| Orchestration | Runs and self-heals the app across replicas | Kubernetes (via Minikube) |
| Load generation | Simulates real user traffic at scale | k6 |
| Infrastructure chaos | Kills pods, injects failure | Chaos Mesh |
| Security/threat simulation | Simulates attacks (brute-force login, etc.) | Custom Python scripts, optionally OWASP ZAP |
| Observability | Watches what's happening during tests | Prometheus + Grafana (or lightweight logging) |
| Orchestrator | Runs all tests together, scores results | Python controller script |
| CI/CD gate (optional) | Blocks publishing if tests fail | GitHub Actions |

## Roadmap at a Glance
| Phase | Covers | Status |
|---|---|---|
| 0 | Environment setup | ✅ Done |
| 1 | Target app on Kubernetes (3 replicas) | ✅ Done |
| 1b | Self-healing proof | ✅ Done |
| 2 | Observability | ⬜ Not started |
| 3 | Load testing (k6) | 🔄 In progress |
| 4 | Infrastructure chaos (Chaos Mesh) | 🔄 In progress |
| 5 | Security testing | ⬜ Not started |
| 6 | Orchestrator | ⬜ Not started |
| 7 | CI/CD gate | ⬜ Not started (optional) |
| 8 | Documentation | ⬜ Ongoing |

See the individual `phase-*.md` files for a full breakdown of each phase's tasks, expected outcomes, and contribution to the system.

## End Result : What the Finished Project Looks Like
1. A working, containerized, self-healing web app running on Kubernetes with multiple replicas
2. A documented breaking point under load (a real number from a real k6 run)
3. A documented resilience result under *combined* stress (pod kill + load simultaneously)
4. A documented security before/after (unprotected `/login` broken, then fixed and proven resistant)
5. A single orchestrator that runs all of the above and outputs one pass/fail readiness report
6. (Optional) A CI/CD pipeline that automatically blocks a bad deployment and passes a fixed one
7. A final report package: architecture diagram, three-pillar explanation, before/after tables, screenshots/recordings, and a debugging narrative
8. A live, demoable system and not just slides

## Why This Matters
This isn't "an app deployed with Kubernetes" but it's a working instance of **Security Chaos Engineering**, a real, still-emerging discipline in industry and academic research (associated with Kelly Shortridge & Aaron Rinehart's foundational work), applied as a concrete, automated pre-publish gate. It demonstrates infrastructure skill (Docker/Kubernetes), testing rigor (load testing), security awareness (attack simulation and mitigation), and most importantly the engineering discipline to *measure and prove* resilience rather than assume it.

## Real Engineering Challenges Already Solved
- Python venv / `ModuleNotFoundError` from VS Code interpreter mismatch
- Debian `externally-managed-environment` (PEP 668) restriction
- `sudo`/`apt` dpkg lock issue
- Docker `permission denied on docker.sock` (fixed via `docker` group)
- WSL distro / VS Code remote mismatch (was hitting `docker-desktop` distro instead of real Ubuntu)
- Deployed a 3-replica Kubernetes app and proved self-healing by manually killing a pod

These are genuine DevOps troubleshooting wins worth keeping in the final report for real engineering judgment, not tutorial-following.
