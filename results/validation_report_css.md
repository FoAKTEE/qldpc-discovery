# Validation report (CSS) — blind discoveries vs arXiv:2606.02418 (post-hoc)

Reference codes: 227 (css catalog + landmarks). The catalog is a HELD-OUT TEST SET — never consulted during the blind search.

Blind seed: 31  ·  k-screened: 800  ·  distance-evals: 18

| blind discovery | FOM | exact | verdict | matched paper code |
|---|---|---|---|---|
| [[72,12,6]] | 6.0 | False | UB_CONSISTENT | [[72,12,6]] landmark:bravyi2024high(MILP-validation) |
| [[144,4,14]] | 5.444 | False | PARAMS_NOT_IN_REF_AT_N | — |
| [[72,8,6]] | 4.0 | False | PARAMS_NOT_IN_REF_AT_N | — |
| [[72,4,8]] | 3.556 | True | PARAMS_NOT_IN_REF_AT_N | — |
| [[144,8,8]] | 3.556 | False | UB_CONSISTENT | [[144,8,12]] css_catalog |
| [[144,24,4]] | 2.667 | False | UB_CONSISTENT | [[144,24,6]] css_catalog |
| [[72,16,2]] | 0.889 | False | PARAMS_NOT_IN_REF_AT_N | — |

## Summary

- **PARAMS_NOT_IN_REF_AT_N**: 4
- **UB_CONSISTENT**: 3

Verdict key: MATCH = same (n,k,d) exact vs an exact reference; POLY_MATCH = identical (A,B) polynomial sets; UB_CONSISTENT = same (n,k), our d (upper bound) consistent with the reference d; NOVEL_AT_N = no reference code at this block length (the CSS catalog starts at n=144).
