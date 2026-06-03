# Extending qcode-discovery

How to add to the package. The one hard rule: keep discovery **catalog-blind** — only
`src/discovery/validation.py` may read a paper catalog, and only *post-hoc*.

## Package layout (one kind per subpackage)

```
src/
  algebra/     gf2, polynomials            GF(2) linear algebra; the ring R=F2[x,y]/(xˡ−1,yᵐ−1)
  codes/       bb_codes, pbb_codes,        BB (CSS) & PBB (non-CSS) construction; k, logicals, FOM;
               metrics, theorems           thm:ab_d2 / lem:crt_k witnesses
  distance/    distance_milp, _enum,       exact MILP (CSS + symplectic); enumeration; BP-OSD bound
               _bposd
  structure/   tanner, dedup,              decomposability; exact BLISS dedup; LC-CSS equivalence
               clifford_equiv
  discovery/   evaluation, search,         catalog-blind cascade; GA / ansatz evolution;
               evolve, validation          post-hoc catalog validation (the ONLY catalog reader)
  cli.py                                   qcode-discover / qcode-validate / qcode-audit
tests/         test_kernel, test_discovery, test_cli
```

## Add a kernel component (module)

1. Create `src/<subpackage>/<name>.py`. The module docstring carries a **paper anchor**
   (`arXiv:2606.02418 §X`) and a **risk tier** (R0–R4). A discovery-path module imports only the
   kernel — never the catalog.
2. Re-export the public symbols from `src/__init__.py` (`__all__`).
3. Add a closed-loop test in `tests/test_*.py` — assert against an **independent method** where
   possible (e.g. MILP ↔ enumeration agreement), not just a golden value.
4. Gate before committing: `python -m pytest -q` green **and** `qcode-audit` PASS (0 CRITICAL/HIGH).

## Run discovery + validate

```bash
qcode-discover --type css --distance-method bposd --stage3-verify --lattices 6x6,12x6
qcode-validate --type css            # post-hoc; built-in landmarks, or --catalog <paper.tex>
```
Discovery writes `results/runs/blind_<type>_discovery.json`; validation writes `results/validation/`.
Every discovered `[[n,k,d]]` carries an evidence modality + verifier status (MILP gap=0 / enumeration /
BP-OSD upper bound) — never promote a BP-OSD upper bound to an exact distance.

## Optional dependencies

`pip install -e ".[decoders]"` adds `ldpc` (BP-OSD distance) and `python-igraph` (exact BLISS dedup).
Tests that need them use `pytest.importorskip`; tests that need the (un-bundled) paper catalog skip
unless a local copy is present.
