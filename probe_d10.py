import time, json
from qcode import bb
from exp_certlb import _type_geq_T
# both proven-d>=9 codes, probe T=10
CODES=[(12,6,[(0,0),(4,3),(11,3)],[(0,0),(5,5),(10,1)]),
       (6,12,[(0,0),(1,8),(2,1)],[(0,0),(3,10),(3,11)])]
T=10; out=[]
for (l,m,A,B) in CODES:
    c=bb.BBCode(l,m,A,B); dl=time.time()+700; t=time.time()
    rX=_type_geq_T(c.HZ,c.HX,T,60,dl); rZ=_type_geq_T(c.HX,c.HZ,T,60,dl)
    wit=None
    for r in (rX,rZ):
        if r[0]=='witness': wit=r[1][0] if wit is None else min(wit,r[1][0])
    if rX[0]=='certified' and rZ[0]=='certified': v='d >= 10 PROVEN'
    elif wit is not None: v='witness w=%d (d<=%d, so d in [9,%d])'%(wit,wit,wit)
    else: v='d>=10 UNRESOLVED in budget (X:%s Z:%s) -- d>=9 stands'%(rX[0],rZ[0])
    print('(l,m)=(%d,%d) A=%s B=%s -> %s (%.0fs)'%(l,m,A,B,v,time.time()-t),flush=True)
    out.append(dict(l=l,m=m,A=A,B=B,verdict=v))
    json.dump(out,open('results/_probe_d10.json','w'),indent=2)
print('# wrote',flush=True)
