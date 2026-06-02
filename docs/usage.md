# Usage

## Install

```bash
pip install -e .                 # core (numpy, scipy)
pip install -e ".[decoders]"     # + ldpc (BP-OSD) + python-igraph (exact BLISS dedup)
pip install -e ".[dev]"          # + pytest
```
Without installing, prefix commands with `PYTHONPATH=src`.

## Library (public API)

```python
from qcode_discovery import (
    BBCode, PBBCode, css_k, fom,
    css_distance_milp, bposd_distance, css_distance_enum,
    is_decomposable, dedup_bliss, lc_css_classify,
    blind_search_css, verify_elites_milp, validate,
    verify_ab_d2, verify_crt_k,
)

code = BBCode(12, 6, "y+y^2+x^3", "y^3+x+x^2")   # the gross code [[144,12,12]]
print(code.n, css_k(code.HX, code.HZ))            # 144 12
print(css_distance_milp(BBCode(6, 6, "1+x+y", "1+x+y"), time_limit=20)["d"])  # A=B -> 2
```

## CLI

```bash
qcode-discover --type css --distance-method bposd --stage3-verify --lattices 6x6,12x6
qcode-validate --type css            # post-hoc; reads results/runs/, writes results/validation/
qcode-audit                          # static code-quality audit (exit !=0 on CRITICAL/HIGH)
qcode-discovery <discover|validate|audit> ...   # dispatcher form
```

- `--type {css,pbb}` · `--distance-method {milp,bposd}` · `--stage3-verify` (MILP-certify survivors)
  · `--lattices LxM,...` · `--seed` · `--n-random` · `--budget` · `--gens`.
- **Discovery is catalog-blind**: it never reads the paper catalog. `qcode-validate` is the only
  catalog reader and runs *after* discovery, against built-in landmark codes by default; pass
  `--catalog <paper.tex>` to compare against the full (held-out, not bundled) paper catalog.
- `qcode-discover` writes its run JSON under `results/runs/` (created on demand); `qcode-validate`
  writes a report under `results/validation/`.

## Tests & audit

```bash
python -m pytest -q          # 54 tests (3 skip unless the paper catalog is supplied)
qcode-audit                  # 0 blocking findings
```
