# medium_term — qldpc-discovery (meso tracking)

Overwrite-mode per section (multi_timescale_tracking_template v2). History in git.

## 10-iter window (windows 1–10)
- **Window 1 (bootstrap, 2026-06-02):** infra reconfig → paper acquisition + decomposition
  → verified kernel (18 tests) → escalation (Bravyi 2308.07915) → loop armed.
  Components PROVEN: 1 (BB construction), 2 (PBB construction), 3 (k via rank), 4 (CSS MILP),
  6 (enumeration), 8 (FOM), 12 (decomposability) + theorems thm:ab_d2, lem:crt_k.
  Components [FUTURE]: 5 (symplectic MILP), 7 (BP-OSD, needs ldpc), 9 (cascade), 10 (MAP-Elites),
  11 (BLISS, needs igraph), 13 (LC full).
- Strategic redirect: reference repo qcode-discovery is EMPTY → reproduce from paper text (verified viable).

## Bundle DAG snapshot
```
B0 GF(2) algebra (gf2, polynomials)            [SOLID]
 └─> B1 construction (bb_codes, pbb_codes)      [SOLID]
      └─> B2 parameters (metrics: k, FOM)        [SOLID]
      └─> B3 distance kernel
            ├─ CSS MILP (distance_milp)          [SOLID]
            ├─ enumeration (distance_enum)        [SOLID]
            └─ symplectic MILP                    [HOLE]
      └─> B5 structure (tanner decomposability)   [SOLID]; BLISS dedup [FUTURE]; LC [PARTIAL: rank cond done]
 B4 decoders (BP-OSD + achievable sampling)       [FUTURE: needs ldpc]
 B6 evaluation cascade                            [HOLE]
 B7 evolutionary search (MAP-Elites + ansatz)     [HOLE]
 B8 theorems (thm:ab_d2, lem:crt_k witnesses)     [SOLID]
```

## Simplification cycle log
(none yet; first cycle due ~window 5–10 per simplification_cycle_policy.)
