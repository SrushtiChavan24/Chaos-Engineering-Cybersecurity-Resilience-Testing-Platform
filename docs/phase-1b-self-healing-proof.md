# Phase 1b — Self-Healing Proof

**Status:** ✅ Done

## What This Phase Covers
A manual, controlled demonstration that Kubernetes' self-healing actually works on your deployment — before you automate any chaos experiments. This is a sanity check that de-risks Phase 4.

## What To Do
1. Confirm the 3-replica Deployment from Phase 1 is healthy: `kubectl get pods`
2. Manually delete one pod: `kubectl delete pod <pod-name>`
3. Immediately re-run `kubectl get pods` in a loop (or `kubectl get pods --watch`) and observe Kubernetes scheduling a replacement pod automatically
4. Record the time between deletion and the replacement pod reaching `Running`/`Ready`
5. Confirm the Service continued routing traffic to the remaining 2 pods during the gap (optional: hit `/health` repeatedly during the kill to confirm zero full outage)

## What To Expect
- The killed pod disappears from `kubectl get pods`
- A new pod with a new name appears within seconds, reaches `Running`, then `Ready`
- The Deployment's replica count returns to 3 without any manual intervention
- No sustained downtime — the Service kept serving from the surviving replicas

## Contribution to the Overall System
This is your first piece of **evidence**, not just a claim: "Kubernetes self-heals" is proven, on your own cluster, with a timestamped before/after. This result becomes:
- A screenshot/recording for Phase 8 documentation
- The baseline behavior that Phase 4's chaos experiments build on (Phase 4 does this same kill, but *automated* and *combined with load*, to see if self-healing still holds up under stress)

## Code / Function Reference
No new code — this phase uses `kubectl` directly against the Phase 1 Deployment. Optionally, a short shell loop can be saved for the report:
```bash
kubectl get pods -w
```

## How It Fits the Architecture
Validates the **Orchestration (Kubernetes)** row of the architecture in isolation, under a manual failure, before Phase 4 introduces automated, combined failure conditions via Chaos Mesh.
