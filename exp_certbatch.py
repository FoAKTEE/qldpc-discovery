"""Drive certify_geq over a set of candidate codes to PROVE d>=T (or witness d<T).

Reads a JSON list of records [{l,m,A,B}, ...] (A,B as lists of [a,b]) and, for
each, runs the MILP infeasibility certifier at the requested target T.  Prints a
rigorous verdict per code.  This is the instrument we trust for 'd>=10'.
"""
import sys
import time
import json

from exp_certlb import certify_geq


def verdict(l, m, A, B, T, tl, tb):
    c, rX, rZ = certify_geq(l, m, A, B, T, tl, tb)
    if rX[0] == "certified" and rZ[0] == "certified":
        v = "CERTIFIED d>=%d" % T
    elif "witness" in (rX[0], rZ[0]):
        ws = [r[1][0] for r in (rX, rZ) if r[0] == "witness"]
        v = "WITNESS d<=%d (so d<%d)" % (min(ws), T)
    else:
        v = "UNRESOLVED"
    return c, v, rX[0], rZ[0]


if __name__ == "__main__":
    path = sys.argv[1]
    T = int(sys.argv[2])
    tl = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    tb = int(sys.argv[4]) if len(sys.argv) > 4 else 400
    topn = int(sys.argv[5]) if len(sys.argv) > 5 else 10
    with open(path) as f:
        recs = json.load(f)
    # accept either search-output dicts (with fom) or plain {l,m,A,B}
    recs = sorted(recs, key=lambda r: r.get("fom", 0), reverse=True)[:topn]
    for r in recs:
        l = r.get("l"); m = r.get("m")
        if l is None:
            # infer from n if needed; require explicit l,m otherwise
            l = r["l"]; m = r["m"]
        A = [tuple(t) for t in r["A"]]
        B = [tuple(t) for t in r["B"]]
        t = time.time()
        c, v, sx, sz = verdict(l, m, A, B, T, tl, tb)
        print("[[%d,%d,?]] A=%s B=%s -> %s  (X:%s Z:%s, %.0fs)"
              % (c.n, c.k(), A, B, v, sx, sz, time.time() - t), flush=True)
