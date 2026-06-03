# current_iter — 8-GPU blind search, iter 8 (overwrite-mode)

## Anchor
User: launch the full-coverage scan with PROPER FILTERS (codes like [[112,24,20]] are too-good-to-be-true
BP-OSD overestimates); then, after the scan, launch the CERTIFIERS.

## EDIT
- RATE-AWARE trust filter (scripts/search/blind_search.jl): keep iff d/sqrt(n) < cap(k/n) with
  cap = 1.8 (k/n<=0.06) / 1.4 (<=0.12) / 1.1 (>0.12). BP-OSD overestimates d MORE at high rate
  (paper's finding); real high-rate codes obey the rate-distance tradeoff -> a high d/sqrt(n) at high
  rate is an overestimate. Drops [[112,24,20]] (k/n=0.21, d/sqrt(n)=1.89). Frontier now records k/n;
  added a machine-readable frontier.md.tsv sidecar (all cells) for the certifier.
- CERTIFIER (scripts/search/certify.jl): per code, parallel — (1) high-effort BP-OSD (HITRIALS=300,
  large max_iter) tightens the upper bound, exposing overestimates; (2) min_distance_bz EXACT for
  small codes (n<=200). Writes certified.md showing d0(scan) -> d(certified) + EXACT/UB status.

## VERIFY (TRF-R)
- Filter smoke (-t 48,2, WALL=20): top frontier now ALL low-rate (k/n 0.006-0.067), no high-rate
  overestimates; e.g. [[560,12,40]] k/n=0.021, [[180,12,18]] k/n=0.067. TSV sidecar: 101 rows. DONE exit 0.

## Status
FULL scan DONE (bgvzl89jr exit 0): screened=183151 dist_evals=10913 cells=418 elapsed=619s,
throughput ~296 cand/s on 200 cores. Top BP-OSD UB: [[336,20,32]] FOM60.95, [[780,16,50]] 51.28,
[[720,16,48]] 51.20, [[528,16,40]] 48.48. Rate filter HELD: top frontier all low-rate (k/n<=0.06),
no [[112,24,20]]-style overestimates survived. frontier.md (top 40) + frontier.md.tsv (all 418) written.

CERTIFIER DONE (bfm56zivl exit 0): 418 certified, 39 EXACT (min_distance_bz gap=0), 379 UB, 0 err.
Demoted overestimates ([[336,20,32]]->[[336,20,26]], [[528,16,40]]->[[528,16,28]], [[780,16,50]]->42).
Top certified FOM: [[840,16,46]] 40.30, [[336,20,26]] 40.24, [[600,16,38]] 38.51. -> certified.md (full).
Honest: scan d's are BP-OSD UPPER bounds (rate-filtered); certifier gives EXACT (small n) or tightened UB.
code_quality_policy_pass: R1 (rate-aware filter + certifier pipeline) -> PROVEN.

## VALIDATION (post-hoc, blind discipline honored)
Blind search REDISCOVERED [[144,12,12]] (gross-code params) at (12,6) with a DIFFERENT poly pair than
canonical; certifier d0=14 -> d=12. Held-out paper landmark reached blind => apparatus validated.

## MISSION COMPLETE
Scan + certify + record + validate all DONE. RESEARCH_NOTE.md updated with results. Committing blind-zero.

## Port to main (DONE)
Per user "make the same change of source code and script to main branch": ported bposd.jl heap-corruption
fix + max_iter, CUDA warp kernel, threaded packing, regression test, blind_search.jl/certify.jl to main
(90816c8). Verified on main: runtests.jl all PASS, regression 35/35, 0 failures. blind-zero pushed (af3f381).
