# Phase 5 — Security Testing

**Status:** ⬜ Not started

## What This Phase Covers
Proving the "safe when a threat tries to enter" pillar with a real, measurable before/after: an unprotected `/login` endpoint gets attacked and broken, then protected and re-attacked to prove the fix works.

## What To Do
1. Write `bruteforce_test.py` — a script that sends repeated login attempts against `/login` with varying credentials (a small wordlist is enough; this doesn't need to be sophisticated, it needs to be measurable)
2. Run it against the **unprotected** endpoint from Phase 1 and record: total attempts sent, how many were processed/accepted by the server (e.g., 200/200), and how long the run took
3. Implement a fix in `app.py` — rate limiting on `/login` (e.g., via `Flask-Limiter`, or a simple in-memory/IP-based attempt counter with a lockout window)
4. Redeploy the updated app (rebuild image, `kubectl rollout restart` or re-apply the Deployment)
5. Re-run `bruteforce_test.py` against the **protected** endpoint and record the new numbers (e.g., blocked after attempt 20)
6. (Optional, stronger) Run OWASP ZAP as an automated scanner against the app for a broader vulnerability pass beyond just the brute-force case, and note any additional findings

## What To Expect
- **Before:** all (or nearly all) brute-force attempts succeed/are processed by the server — e.g., "200/200 requests processed, no blocking"
- **After:** the same script gets blocked well before completion — e.g., "blocked after attempt 20, remaining 180 requests rejected with 429"
- This is your cleanest, most presentation-ready before/after result in the whole project — it's the kind of result that visually demos well ("watch the attack succeed... now watch it fail")

## Contribution to the Overall System
This is the third pillar ("security resilience") turned into evidence, and it's the strongest kind of evidence in the whole project because it's a direct causal before/after on the *same* endpoint, with the *same* attack script, only the app code changed. It's also the piece most reviewers/evaluators will find intuitively easy to grasp and be impressed by, even without deep security background.

## Code / Function Reference
- `bruteforce_test.py` — sends N login attempts, logs success/failure counts and timing
- `app.py` (updated) — adds rate limiting to `/login` (e.g. `Flask-Limiter` decorator, or custom attempt-counter + lockout logic)
- Optional: OWASP ZAP scan config/report
- Output: `results_before.json` / `results_after.json` (or equivalent) with attempt counts, block point, and timing, for direct before/after comparison in Phase 8

## How It Fits the Architecture
Maps to the **Security/threat simulation** row. Its "before" run establishes a baseline vulnerability; its "after" run is the proof that a real fix was applied and verified — not just claimed. This before/after pair is a direct input to the Phase 6 orchestrator's pass/fail scoring.
