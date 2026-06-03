"""POST-HOC validation: compare BLIND discoveries against the paper (held-out test set).

This is the ONLY module permitted to read the paper catalog / reported [[n,k,d]]
(blind_discovery_policy). It runs strictly AFTER a blind discovery campaign and never
feeds anything back into the search. It parses the CSS catalog tables and a small set of
paper-referenced landmark codes, then classifies each discovery as a parameter MATCH,
UPPER-BOUND-CONSISTENT, or NOVEL-at-n. Paper anchor: arXiv:2606.02418 catalogs + Sec V.B. R2.
"""
from __future__ import annotations

import re
from pathlib import Path

from ..algebra.polynomials import parse_poly, normalize_terms


def _num(tok: str):
    """Extract (value:int|None, is_upper:bool) from a catalog k/d cell (handles \\leq, \\textbf)."""
    is_upper = ("leq" in tok) or ("<=" in tok) or ("\\leq" in tok)
    m = re.search(r"\d+", tok.replace(",", ""))
    return (int(m.group()) if m else None), is_upper


def parse_css_catalog(tex_path: str | Path) -> list[dict]:
    """Parse css_catalog_tables.tex rows into reported CSS codes (held-out reference)."""
    text = Path(tex_path).read_text()
    codes: list[dict] = []
    for raw in text.splitlines():
        line = raw.strip()
        if " & " not in line or not line.endswith("\\\\"):
            continue
        cols = [c.strip() for c in line[:-2].split("&")]
        latt = re.search(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)", cols[1]) if len(cols) > 1 else None
        if not latt or len(cols) < 7:
            continue
        l, m = int(latt.group(1)), int(latt.group(2))
        k, _ = _num(cols[4])
        d, d_up = _num(cols[5])
        if k is None or d is None:
            continue
        codes.append({
            "l": l, "m": m, "n": 2 * l * m, "k": k, "d": d, "d_is_upper": d_up,
            "A": cols[2], "B": cols[3], "pattern": cols[10] if len(cols) > 10 else "",
            "source": "css_catalog",
        })
    return codes


def parse_pbb_catalog(tex_path: str | Path) -> list[dict]:
    """Parse pbb_catalog_tables.tex rows into reported non-CSS PBB codes (held-out reference).

    Columns: Cl & (l,m) & A & B & C & D & k & d & FOM.
    """
    text = Path(tex_path).read_text()
    codes: list[dict] = []
    for raw in text.splitlines():
        line = raw.strip()
        if " & " not in line or not line.endswith("\\\\"):
            continue
        cols = [c.strip() for c in line[:-2].split("&")]
        latt = re.search(r"\(\s*(\d+)\s*,\s*(\d+)\s*\)", cols[1]) if len(cols) > 1 else None
        if not latt or len(cols) < 9:
            continue
        l, m = int(latt.group(1)), int(latt.group(2))
        k, _ = _num(cols[6])
        d, d_up = _num(cols[7])
        if k is None or d is None:
            continue
        codes.append({"l": l, "m": m, "n": 2 * l * m, "k": k, "d": d, "d_is_upper": d_up,
                      "A": cols[2], "B": cols[3], "pattern": "PBB", "source": "pbb_catalog"})
    return codes


def landmark_codes() -> list[dict]:
    """Paper-referenced CSS landmark/validation codes (Bravyi gross-code family, Sec V.B)."""
    return [
        {"l": 12, "m": 6, "n": 144, "k": 12, "d": 12, "d_is_upper": False,
         "A": "y+y^2+x^3", "B": "y^3+x+x^2", "pattern": "gross", "source": "landmark:bravyi2024high"},
        {"l": 6, "m": 6, "n": 72, "k": 12, "d": 6, "d_is_upper": False,
         "A": "y+y^2+x^3", "B": "y^3+x+x^2", "pattern": "gross-family", "source": "landmark:bravyi2024high(MILP-validation)"},
    ]


def _poly_set(expr, l, m):
    try:
        return frozenset(normalize_terms(parse_poly(expr, l, m), l, m))
    except Exception:
        return None


def validate(discoveries: list[dict], catalog_tex: str | Path | None, kind: str = "css") -> dict:
    """Classify each blind discovery against the paper reference. Returns a report dict.

    kind: 'css' (landmarks + CSS catalog, polynomial-set matching) or 'pbb' (PBB catalog,
    (n,k,d)-only matching since PBB equivalence is local-Clifford-level).
    classification per discovery:
      - 'MATCH'            : a reference code at the same n with equal k and equal d (both exact).
      - 'UB_CONSISTENT'    : same (n,k); our d is an upper bound consistent with reference d.
      - 'POLY_MATCH'       : same (l,m) and identical (A,B) polynomial sets as a reference code (css only).
      - 'NOVEL_AT_N'       : no reference code at this n (e.g. CSS catalog starts at n=144).
    """
    if kind == "pbb":
        reference = parse_pbb_catalog(catalog_tex) if (catalog_tex and Path(catalog_tex).exists()) else []
    else:
        reference = list(landmark_codes())
        if catalog_tex and Path(catalog_tex).exists():
            reference += parse_css_catalog(catalog_tex)
    ref_by_n: dict[int, list] = {}
    for r in reference:
        ref_by_n.setdefault(r["n"], []).append(r)

    results = []
    for disc in discoveries:
        n, k, d = disc["n"], disc["k"], disc.get("d")
        d_exact = disc.get("exact", False)
        refs = ref_by_n.get(n, [])
        verdict, matched = "NOVEL_AT_N", None
        if not refs:
            verdict = "NOVEL_AT_N"
        else:
            disc_A = _poly_set(disc["A"], disc["l"], disc["m"]) if isinstance(disc.get("A"), str) else \
                frozenset(map(tuple, disc.get("A", [])))
            disc_B = _poly_set(disc["B"], disc["l"], disc["m"]) if isinstance(disc.get("B"), str) else \
                frozenset(map(tuple, disc.get("B", [])))
            for r in refs:
                if r["k"] != k:
                    continue
                rA = _poly_set(r["A"], r["l"], r["m"])
                rB = _poly_set(r["B"], r["l"], r["m"])
                poly_hit = (disc_A is not None and rA is not None and
                            {disc_A, disc_B} == {rA, rB})
                # Identical polynomials => the SAME code. POLY_MATCH regardless of our d-estimate
                # (a BP-OSD upper bound may overestimate the reference's true d).
                if poly_hit:
                    verdict, matched = "POLY_MATCH", r
                    break
                if d is not None and d == r["d"] and d_exact and not r["d_is_upper"]:
                    verdict, matched = "MATCH", r
                    break
                if d is not None and d <= r["d"]:        # our (possibly upper-bound) d consistent
                    verdict, matched = "UB_CONSISTENT", r
            if matched is None and refs:
                verdict = "PARAMS_NOT_IN_REF_AT_N"
        results.append({"discovery": f"[[{n},{k},{d}]]", "fom": disc.get("fom"),
                        "exact": d_exact, "verdict": verdict,
                        "matched_ref": (f"[[{matched['n']},{matched['k']},{matched['d']}{'(<=)' if matched['d_is_upper'] else ''}]]"
                                        f" {matched['source']}") if matched else None})
    summary = {}
    for r in results:
        summary[r["verdict"]] = summary.get(r["verdict"], 0) + 1
    return {"n_reference_codes": len(reference), "results": results, "summary": summary}
