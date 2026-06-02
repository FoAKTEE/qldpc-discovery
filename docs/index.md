# qcode-discovery — documentation

A verified, **catalog-blind** reproduction of *"Evolutionary Discovery of Bivariate Bicycle Codes
with LLM-Guided Search"* (arXiv:2606.02418). The LLM/search proposes generator ansätze; a scientific
kernel admits them; the paper catalog is consulted only **post-hoc** as a held-out test set.

## Contents

- **[usage.md](usage.md)** — install, the public API, the CLI (`qcode-discover` / `qcode-validate` /
  `qcode-audit`), running a blind campaign and validating it.
- **[architecture.md](architecture.md)** — the kernel ⊕ discovery ⊕ validation design, the five
  subpackages, the 13 reproduced pipeline components, and the 3-stage cascade.
- **[REPORT.md](REPORT.md)** — the scientific final report (method, verified results, the honest
  clean-room finding, limitations).
- **[EXTENDING.md](EXTENDING.md)** — how to add a reference paper / a kernel component, and the
  tracking cadence.

## At a glance

- Library: `src/qcode_discovery/` — `algebra · codes · distance · structure · discovery`.
- Public API: `from qcode_discovery import BBCode, css_distance_milp, blind_search_css, validate, ...`
- Tests: `python -m pytest -q` (49 passing). Audit: `qcode-audit`.
- Optional deps `[decoders]` (`ldpc`, `python-igraph`) unlock BP-OSD distance + exact BLISS dedup.

See the repository [README](../README.md) for the high-level overview and results.
