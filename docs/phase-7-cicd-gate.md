# Phase 7 — CI/CD Gate (Optional)

**Status:** ⬜ Not started (optional)

## What This Phase Covers
Automating the Phase 6 orchestrator inside a CI/CD pipeline (GitHub Actions), so a bad deployment is blocked automatically rather than relying on someone manually running the test suite. This turns the project from "a tool you run by hand" into "a gate that enforces the standard automatically."

## What To Do
1. Write a GitHub Actions workflow (`.github/workflows/resilience-gate.yml`) that, on a trigger (e.g. push to a branch, or a manual `workflow_dispatch`):
   - Spins up (or connects to) a test environment with Minikube/Kubernetes available
   - Deploys the target app
   - Runs `orchestrator.py` from Phase 6
   - Fails the workflow (non-zero exit code) if the orchestrator's overall verdict is FAIL
2. Demonstrate the gate actually blocking a bad deployment: temporarily remove the Phase 5 rate limiting, push, and show the pipeline fail on the security check
3. Re-add the fix, push again, and show the pipeline pass — a live, convincing "before/after" for the whole system, not just one component

## What To Expect
- A GitHub Actions run that shows red (failed) when the app doesn't meet the readiness bar, and green (passed) once it does
- This is the most "production-realistic" artifact in the project — it's the same pattern real DevSecOps teams use for deployment gates

## Contribution to the Overall System
This phase is optional but is the strongest possible capstone: it proves the orchestrator isn't just a local demo script, it's usable as a real automated gate in a real deployment pipeline. It's also the easiest phase to skip under time pressure without weakening the core three pillars, since Phases 3–6 already constitute a complete, demonstrable system on their own.

## Code / Function Reference
- `.github/workflows/resilience-gate.yml` — CI pipeline definition
- Re-uses `orchestrator.py` (Phase 6) as the actual test runner inside the pipeline
- Exit code of `orchestrator.py` (0 = pass, non-zero = fail) is what GitHub Actions uses to mark the job pass/fail

## How It Fits the Architecture
Maps to the **CI/CD gate (optional/future)** row. It consumes the Phase 6 orchestrator's verdict directly — no new testing logic is introduced here, only automation around when and how the existing suite runs.
