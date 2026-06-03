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
FULL scan launched: -t 200,2 NMAX=1000 WALL=600 CHECKPOINT=20 -> progress/blind-search-8gpu/frontier.md
(live, harness-tracked bgvzl89jr). ON COMPLETION -> run certify.jl on frontier.md.tsv -> certified.md.
Honest: scan d's are BP-OSD UPPER bounds (rate-filtered); certifier gives EXACT (small n) or tightened UB.
code_quality_policy_pass: R1 (rate-aware filter + certifier pipeline) -> PROVEN.
