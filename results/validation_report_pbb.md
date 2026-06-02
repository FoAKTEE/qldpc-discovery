# Validation report (PBB) — blind discoveries vs arXiv:2606.02418 (post-hoc)

Reference codes: 368 (pbb catalog + landmarks). The catalog is a HELD-OUT TEST SET — never consulted during the blind search.

Blind seed: 5  ·  k-screened: 800  ·  distance-evals: 16

| blind discovery | FOM | exact | verdict | matched paper code |
|---|---|---|---|---|
| [[36,8,4]] | 3.556 | False | PARAMS_NOT_IN_REF_AT_N | — |
| [[36,4,5]] | 2.778 | True | UB_CONSISTENT | [[36,4,6]] pbb_catalog |
| [[36,2,6]] | 2.0 | True | MATCH | [[36,2,6]] pbb_catalog |
| [[36,4,4]] | 1.778 | True | UB_CONSISTENT | [[36,4,6]] pbb_catalog |
| [[36,12,2]] | 1.333 | False | PARAMS_NOT_IN_REF_AT_N | — |
| [[36,10,2]] | 1.111 | False | PARAMS_NOT_IN_REF_AT_N | — |
| [[36,2,4]] | 0.889 | False | UB_CONSISTENT | [[36,2,6]] pbb_catalog |
| [[36,8,2]] | 0.889 | False | PARAMS_NOT_IN_REF_AT_N | — |
| [[36,6,2]] | 0.667 | False | PARAMS_NOT_IN_REF_AT_N | — |

## Summary

- **MATCH**: 1
- **PARAMS_NOT_IN_REF_AT_N**: 5
- **UB_CONSISTENT**: 3

Verdict key: MATCH = same (n,k,d) exact vs an exact reference; POLY_MATCH = identical (A,B) polynomial sets; UB_CONSISTENT = same (n,k), our d (upper bound) consistent with the reference d; NOVEL_AT_N = no reference code at this block length (the CSS catalog starts at n=144).
