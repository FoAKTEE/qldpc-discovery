#!/usr/bin/env python3
"""Reproduce arXiv:2606.02418 Fig. (pareto) "Rate-distance landscape" EXACTLY (2x2 layout),
but plotting the codes WE found on blind-zero-2.

Two output versions:
  fig_pareto_reproduction_asfound.png   -- our codes with AS-FOUND distances (BP-OSD scan for CSS,
                                           exact symplectic for PBB). Honors "no matter correct or not";
                                           the high-k/high-FOM region is dominated by BP-OSD overestimates.
  fig_pareto_reproduction_certified.png -- only codes we CERTIFIED, with certified (ISD/BZ) distances.
                                           The honest landscape.

Paper layout (from VLM read of figures/fig_pareto_frontier.pdf):
  (a) CSS  k vs d     | (b) CSS  FOM=kd^2/n vs n
  (c) PBB  k vs d     | (d) PBB  FOM vs n
  red '+' = Bravyi et al. baselines; red dotted = FOM=12 (gross code); gray dashed = Pareto frontier.
"""
import os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

O = "progress/blind-zero-2"
BRAVYI = [(72,12,6),(144,12,12),(288,12,18),(360,12,24)]   # paper red baselines (labels use <=24 for last)
BRAVYI_LAB = ["[[72,12,6]]","[[144,12,12]]","[[288,12,18]]","[[360,12,$\\leq$24]]"]

def read_tsv(fn):
    p=os.path.join(O,fn); out=[]
    if not os.path.exists(p): return out
    for ln in open(p).read().splitlines()[1:]:
        c=ln.split("\t")
        if len(c)<9 or not c[0].isdigit(): continue
        n,k,d=int(c[0]),int(c[1]),int(c[2])
        wt=int(c[8]) if c[8].isdigit() else 0
        A,B=c[6],c[7]
        if k>0 and d>0: out.append(dict(n=n,k=k,d=d,wt=wt,A=A,B=B))
    return out

def read_certified(fn):
    p=os.path.join(O,fn); m={}
    if not os.path.exists(p): return m
    for ln in open(p):
        g=re.match(r'\|\s*\[\[(\d+),(\d+),(\d+)\]\]\s*\|\s*(\w+)',ln)
        if not g: continue
        n,k,d=int(g[1]),int(g[2]),int(g[3])
        key=(n,k)
        # keep the SMALLEST certified d per (n,k) (tightest/honest)
        if key not in m or d<m[key]: m[key]=d
    return m

css = read_tsv("frontier_css.md.tsv") + read_tsv("frontier_highk.md.tsv")
pbb = read_tsv("frontier_pbb.md.tsv")
cert = {}
for f in ("CERTIFIED_FINAL_FOM.md","CERTIFIED_FINAL_HIGHK.md","INTERIM_CERT.md","ROBUST2_OUT.md"):
    for kk,dd in read_certified(f).items():
        if kk not in cert or dd<cert[kk]: cert[kk]=dd

def wt_cat(w):
    if w<=6: return "weight-6"
    if w==8: return "weight-8"
    return "weight$\\geq$10"
CATSTYLE={"weight-6":("o","#6baed6"),"weight-8":("s","#fd8d3c"),"weight$\\geq$10":("D","#9e7bb5")}

def pareto_kd(points):
    # upper-left staircase: for increasing d, the running max k among points with distance>=d
    if not points: return [],[]
    ds=sorted(set(p[1] for p in points))
    xs,ys=[],[]
    for d in ds:
        kmax=max((p[0] for p in points if p[1]>=d), default=None)
        if kmax is not None: xs.append(d); ys.append(kmax)
    # make it a descending staircase (k non-increasing as d grows)
    out_x,out_y=[],[]; cur=10**9
    for d,k in zip(xs,ys):
        cur=min(cur,k); out_x.append(d); out_y.append(cur)
    return out_x,out_y

def make_figure(mode, outfile):
    fig,axes=plt.subplots(2,2,figsize=(14,11))
    (axa,axb),(axc,axd)=axes
    # ---- choose distances ----
    if mode=="asfound":
        cssd=[(c["n"],c["k"],c["d"],wt_cat(c["wt"])) for c in css]
        pbbd=[(c["n"],c["k"],c["d"]) for c in pbb]
        dtag="AS-FOUND (BP-OSD scan upper bounds, CSS; exact symplectic, PBB) — UNCERTIFIED"
    else:
        cssd=[(c["n"],c["k"],cert[(c["n"],c["k"])],wt_cat(c["wt"])) for c in css if (c["n"],c["k"]) in cert]
        pbbd=[(c["n"],c["k"],c["d"]) for c in pbb]   # PBB already exact symplectic
        dtag="CERTIFIED (ISD-tightened / Brouwer-Zimmermann exact; PBB exact symplectic)"

    # ===== Panel (a): CSS k vs d =====
    for cat,(mk,col) in CATSTYLE.items():
        pts=[(d,k) for (n,k,d,c) in cssd if c==cat]
        if pts: axa.scatter([p[0] for p in pts],[p[1] for p in pts],marker=mk,c=col,s=34,
                            edgecolors="k",linewidths=0.3,alpha=0.8,label=f"{cat.replace('$\\geq$','>=')} ({len(pts)})")
    px,py=pareto_kd([(k,d) for (n,k,d,c) in cssd])
    if px: axa.step(px,py,where="post",color="0.5",ls="--",lw=1.3,label="Pareto frontier")
    for (n,k,d),lab in zip(BRAVYI,BRAVYI_LAB):
        axa.scatter([d],[k],marker="P",c="red",s=120,edgecolors="k",linewidths=0.6,zorder=5)
        axa.annotate(lab,(d,k),textcoords="offset points",xytext=(2,-12),fontsize=7,color="red")
    axa.scatter([],[],marker="P",c="red",s=120,label="Bravyi et al.")
    axa.set_xlabel("MILP distance $d$  (ours: BP-OSD/ISD)"); axa.set_ylabel("Encoding dimension $k$")
    axa.set_title("(a) Rate-distance tradeoff (CSS codes)"); axa.legend(fontsize=7,loc="upper right")

    # ===== Panel (b): CSS FOM vs n  (paper filter d>=4) =====
    for cat,(mk,col) in CATSTYLE.items():
        pts=[(n,k*d*d/n) for (n,k,d,c) in cssd if c==cat and d>=4]
        if pts: axb.scatter([p[0] for p in pts],[p[1] for p in pts],marker=mk,c=col,s=34,
                            edgecolors="k",linewidths=0.3,alpha=0.8,label=f"{cat.replace('$\\geq$','>=')}")
    axb.axhline(12,color="red",ls=":",lw=1.2,label="FOM = 12 (gross code)")
    for (n,k,d),lab in zip(BRAVYI,BRAVYI_LAB):
        axb.scatter([n],[k*d*d/n],marker="P",c="red",s=120,edgecolors="k",linewidths=0.6,zorder=5)
        axb.annotate(lab,(n,k*d*d/n),textcoords="offset points",xytext=(2,4),fontsize=7,color="red")
    axb.scatter([],[],marker="P",c="red",s=120,label="Bravyi et al.")
    axb.set_xlabel("Block length $n$"); axb.set_ylabel("Figure of merit $kd^2/n$")
    axb.set_title("(b) FOM vs block length (CSS, $d\\geq4$)"); axb.legend(fontsize=7,loc="upper left")

    # ===== Panel (c): PBB k vs d =====
    if pbbd:
        axc.scatter([d for (n,k,d) in pbbd],[k for (n,k,d) in pbbd],marker="o",c="#6baed6",s=40,
                    edgecolors="k",linewidths=0.3,label=f"PBB exact ({len(pbbd)})")
        px,py=pareto_kd([(k,d) for (n,k,d) in pbbd])
        if px: axc.step(px,py,where="post",color="0.5",ls="--",lw=1.3,label="Pareto frontier")
    for (n,k,d),lab in zip(BRAVYI,BRAVYI_LAB):
        axc.scatter([d],[k],marker="P",c="red",s=120,edgecolors="k",linewidths=0.6,zorder=5)
        axc.annotate(lab,(d,k),textcoords="offset points",xytext=(2,-12),fontsize=7,color="red")
    axc.scatter([],[],marker="P",c="red",s=120,label="Bravyi et al.")
    axc.set_xlabel("MILP distance $d$  (ours: exact symplectic)"); axc.set_ylabel("Encoding dimension $k$")
    axc.set_title("(c) Rate-distance tradeoff (non-CSS PBB codes)"); axc.legend(fontsize=7,loc="upper right")

    # ===== Panel (d): PBB FOM vs n =====
    if pbbd:
        axd.scatter([n for (n,k,d) in pbbd],[k*d*d/n for (n,k,d) in pbbd],marker="o",c="#6baed6",s=40,
                    edgecolors="k",linewidths=0.3,label=f"PBB exact ({len(pbbd)})")
    axd.axhline(12,color="red",ls=":",lw=1.2,label="FOM = 12 (gross code)")
    for (n,k,d),lab in zip(BRAVYI,BRAVYI_LAB):
        axd.scatter([n],[k*d*d/n],marker="P",c="red",s=120,edgecolors="k",linewidths=0.6,zorder=5)
    axd.scatter([],[],marker="P",c="red",s=120,label="Bravyi et al.")
    axd.set_xlabel("Block length $n$"); axd.set_ylabel("Figure of merit $kd^2/n$")
    axd.set_title("(d) FOM vs block length (non-CSS PBB)"); axd.legend(fontsize=7,loc="upper right")

    for ax in (axa,axb,axc,axd): ax.grid(True,alpha=0.25)
    fig.suptitle(f"blind-zero-2 rediscovered codes in the format of arXiv:2606.02418 Fig. (pareto)\n"
                 f"distances = {dtag}",fontsize=11)
    fig.tight_layout(rect=[0,0,1,0.96])
    fig.savefig(os.path.join(O,outfile),dpi=130)
    plt.close(fig)
    ncss=len(cssd); npbb=len(pbbd)
    print(f"{outfile}: CSS={ncss} PBB={npbb}  maxk={max([k for (n,k,d,*_) in cssd],default=0)} "
          f"maxd={max([d for (n,k,d,*_) in cssd],default=0)} "
          f"maxFOM={max([k*d*d/n for (n,k,d,*_) in cssd],default=0):.1f}")

make_figure("asfound","fig_pareto_reproduction_asfound.png")
make_figure("certified","fig_pareto_reproduction_certified.png")
print(f"certified (n,k) map size: {len(cert)}")
