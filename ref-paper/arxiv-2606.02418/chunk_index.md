# Chunk Index — arXiv:2606.02418

Paper chunking plan for "Evolutionary Discovery of Bivariate Bicycle Codes with
LLM-Guided Search" (Cruz-Benito, Cross, Kremer, Faro; IBM Research; PRX Quantum).
Pipeline-0 (source-import) artifact. Each chunk is a contiguous tex range with a
matching TYPED digest under `digest/`. Default modality of digest entries is
`LiteratureGrounded` unless a proof/derivation is present (then `ExactProof`/
`SymbolicDerivation`); cited-but-not-reproduced results are `[AXIOM]`.

Source files (read-only mirror, per `PROVENANCE.md`):
- `src/paper.tex` — 1091 lines (main text l.1-770, `\appendix` l.791, `\bibliography` l.1089, `\end{document}` l.1091).
- `src/supplemental.tex` — 715 lines.
- Catalog tables included by the SM: `src/css_catalog_tables.tex`, `src/pbb_catalog_tables.tex`.

PDF: `paper.pdf`, 42 pages total (main text + appendices + bibliography + supplemental
in one document). Page ranges below are pinned from `paper.pdf` text extraction.

---

## Chunk plan (3 chunks)

| Chunk id | Source file | Tex line range | Page range (of 42) | Sections covered | Named objects | Digest path | Status |
|---|---|---|---|---|---|---|---|
| chunk_001 | `src/paper.tex` | l.60-770 | pp.1-16 | Main text: `sec:intro` (61), `sec:related` (108), `sec:prelim` (151) incl. `sec:bb` (155) / `sec:pbb` (171) / `sec:fom` (199) / `sec:ab_trap` (206); `sec:method` (214) incl. `sec:framework` (218) / `sec:cascade` (244) / `sec:campaigns` (261); `sec:verification` (303) incl. `sec:bposd_limits` (307) / `sec:milp` (320) / `sec:noncss_pipeline` (339) / `sec:trust` (367); `sec:results` (374) incl. `sec:families` (378) / `sec:tradeoff` (534) / `sec:comparison` (563) / `sec:code_capacity` (633) / `sec:bposd_findings` (671) / `sec:ablation` (704); `sec:discussion` (724); `sec:conclusion` (754) | 35 labels: 25 `sec:*` (13 sections + 12 subsections), 5 `tab:*` (`tab:campaigns`, `tab:pbb_best`, `tab:codes`, `tab:comparison`, `tab:useful`), 4 `fig:*` (`fig:pipeline`, `fig:pareto`, `fig:ler_curves`, `fig:tightening`), 1 `fn:depolarizing-decoder`. No `thm`/`lem`/`eq` labels in this range (statements forward-referenced). | `digest/chunk_001_main_pp.md` | DIGESTED |
| chunk_002 | `src/paper.tex` | l.791-1088 | pp.17-20 | Appendices (`\appendix` l.791): App A `app:threshold` (793) code-capacity data; App B `app:ablation` (849) ablation data; App C `app:mutations` (907) LLM mutation diffs; App D `app:ab_trap` (956) — **Theorem `thm:ab_d2`** (959) + proof; App E `app:crt` (982) — **Theorem `lem:crt_k`** (985) + proof; App F `app:lc` (1026) LC-CSS equivalence of PBB. (Bibliography l.1089 and `\end{document}` l.1091 lie just past the chunk, pp.21-22.) | 15 labels: 5 `app:*`, 2 theorem labels (`thm:ab_d2` l.960, `lem:crt_k` l.986), 3 `fig:*` (`fig:mut1/2/3`), 5 `tab:*` (`tab:threshold_css`, `tab:threshold_noncss`, `tab:ablation_k`, `tab:ablation_per_lattice`). | `digest/chunk_002_appendix.md` | DIGESTED |
| chunk_003 | `src/supplemental.tex` | l.1-715 | pp.23-42 | Supplemental Material: `sm:css_catalog` (47), `sm:pbb_catalog` (70), `sm:decoders` (81), `sm:per_batch` (111), `sm:tightening` (213), `sm:univariate` (243), `sm:threshold` (316), `sm:utility` (507), `sm:comparison` (523) incl. `sm:novelty` (526) / `sm:weight8` (540); `sm:campaigns` (549), `sm:ablation` (620), `sm:milp` (656) incl. CSS formulation (659) / non-CSS symplectic (676) / validation & audits (693). Pulls in `css_catalog_tables.tex` + `pbb_catalog_tables.tex`. | 31 labels: 14 `sm:*` sections, 11 `tab:*`, 2 `fig:*` (`fig:sm_per_batch`, `fig:sm_trajectory`), 4 `eq:*` (`eq:milp_obj` l.663, `eq:milp_commute` l.664, `eq:milp_anticommute` l.665, `eq:milp_binary` l.666). | `digest/chunk_003_supplemental.md` | DIGESTED |

Named-object total across chunks: 35 + 15 + 31 = 81 `\label`s (sections + theorems + tables + figures + equations + footnote). All three digests exist; status `DIGESTED`.

---

## Boundary notes (verbatim-load-bearing)

- **chunk_001 / chunk_002 boundary.** The main text ends at `sec:conclusion` (l.754); the
  range l.770-790 is acknowledgments/whitespace; `\appendix` begins at l.791. Splitting at
  l.770/l.791 keeps the appendices (which carry the two proved theorems) as one chunk.
- **Tex-order vs PDF-order of appendix lettering.** In `paper.tex` the order is
  A=`app:threshold`, B=`app:ablation`, C=`app:mutations`, D=`app:ab_trap` (`thm:ab_d2`),
  E=`app:crt` (`lem:crt_k`), F=`app:lc`. The rendered PDF reorders so that the univariate
  appendix (`app:crt`) appears as "Appendix C". The digest follows TEX ORDER (the
  verification anchor); the labels `thm:ab_d2` (l.960) and `lem:crt_k` (l.986) are the
  stable join keys regardless of PDF letter.
- **chunk_002 / chunk_003 boundary.** `paper.tex` bibliography (pp.21-22) sits between the
  appendices (chunk_002, ending l.1088) and the Supplemental Material, which is a separate
  toplevel file (`supplemental.tex`, pp.23-42 = chunk_003). The bibliography is not assigned
  a content chunk (reference data only).
- **`eq:milp_*` labels are CSS-block only.** The four equation labels live exclusively in the
  CSS distance formulation (supplemental.tex l.663-666); the non-CSS symplectic `align` block
  (l.676-691) carries NO `\label` (confirmed in chunk_003 digest SM-MILP-2). Do not attribute
  `eq:milp_*` to the symplectic MILP.

---

## Provenance convention (shared with digests + `reformulate/`)

`P.l.NNN` = `paper.tex` line N; `S.l.NNN` = `supplemental.tex` line N. Tex labels
(`thm:ab_d2`, `lem:crt_k`, `eq:milp_obj`, `eq:milp_commute`, `eq:milp_anticommute`,
`eq:milp_binary`, and all `sec:*`/`app:*`/`sm:*`/`tab:*`/`fig:*`) preserved VERBATIM.
