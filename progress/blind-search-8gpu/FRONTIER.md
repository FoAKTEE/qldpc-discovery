# Definitive discovered frontier — blind-zero (consolidated, honesty-ordered)

Best code per (n,k) across ALL blind campaigns (scan/broadened/high-k/evolved incl. the iter30
SOUND-fitness honest evolution). Ordered by TRUST: EXACT certificates first, then ISD-tight upper
bounds, then BP-OSD-tightened upper bounds.

**iter26/30 caveat:** the EXACT section is the genuinely verified frontier. Upper-bound sections
can overestimate; the iter30 honest evolution (sound k-scaled+capped ISD fitness) yields max
FOM 5.78 with NO artifacts — no blind code is a certified beat of the paper.

1556 distinct (n,k); 423 EXACT, 33 ISD-tight, 1100 BP-OSD-tightened.

## Verified frontier — EXACT (Brouwer–Zimmermann / enumeration gap=0)

| [[n,k,d]] | FOM | source |
|---|---|---|
| [[54,8,8]] | 9.5 | certified_broadened.md |
| [[48,10,6]] | 7.5 | certified_broadened.md |
| [[40,8,6]] | 7.2 | certified_broadened.md |
| [[54,6,8]] | 7.1 | certified_broadened.md |
| [[56,6,8]] | 6.9 | certified.md |
| [[24,10,4]] | 6.7 | certified_broadened.md |
| [[98,26,5]] | 6.6 | certified_highk2.md |
| [[56,10,6]] | 6.4 | certified_broadened.md |
| [[52,4,9]] | 6.2 | certified_broadened.md |
| [[42,4,8]] | 6.1 | certified_broadened.md |
| [[48,8,6]] | 6.0 | certified_broadened.md |
| [[36,6,6]] | 6.0 | certified_broadened.md |
| [[44,4,8]] | 5.8 | certified_broadened.md |
| [[100,36,4]] | 5.8 | certified_highk2.md |
| [[50,18,4]] | 5.8 | certified_highk2.md |
| [[70,6,8]] | 5.5 | certified.md |
| [[28,6,5]] | 5.4 | certified_broadened.md |
| [[48,4,8]] | 5.3 | certified_broadened.md |
| [[24,8,4]] | 5.3 | certified_broadened.md |
| [[42,6,6]] | 5.1 | certified.md |
| [[84,12,6]] | 5.1 | certified.md |
| [[140,44,4]] | 5.0 | certified_highk2.md |
| [[70,22,4]] | 5.0 | certified_highk2.md |
| [[72,10,6]] | 5.0 | certified_broadened.md |
| [[32,10,4]] | 5.0 | certified_broadened.md |
| [[30,6,5]] | 5.0 | certified_broadened.md |
| [[50,10,5]] | 5.0 | certified_broadened.md |
| [[40,4,7]] | 4.9 | certified_broadened.md |
| [[30,4,6]] | 4.8 | certified.md |
| [[60,8,6]] | 4.8 | certified.md |

## ISD-tight upper bounds (blind evolution; iter30 = sound capped fitness, validated honest)

| [[n,k,d]] | FOM | source |
|---|---|---|
| [[288,104,4]] | 5.8 | evolved_frontier_honest |
| [[360,128,4]] | 5.7 | evolved_frontier_honest |
| [[360,80,5]] | 5.6 | evolved_frontier_honest |
| [[288,90,4]] | 5.0 | evolved_frontier |
| [[288,78,4]] | 4.3 | evolved_frontier_honest |
| [[288,8,12]] | 4.0 | evolved_frontier |
| [[360,4,18]] | 3.6 | evolved_frontier |
| [[288,16,8]] | 3.6 | evolved_frontier |
| [[288,108,3]] | 3.4 | evolved_frontier |
| [[288,58,4]] | 3.2 | evolved_frontier |
| [[360,8,12]] | 3.2 | evolved_frontier |
| [[360,70,4]] | 3.1 | evolved_frontier |
| [[360,16,8]] | 2.8 | evolved_frontier_honest |
| [[288,50,4]] | 2.8 | evolved_frontier |
| [[360,108,3]] | 2.7 | evolved_frontier |
| [[288,48,4]] | 2.7 | evolved_frontier |
| [[360,52,4]] | 2.3 | evolved_frontier |
| [[288,68,3]] | 2.1 | evolved_frontier |
| [[288,150,2]] | 2.1 | evolved_frontier |
| [[360,186,2]] | 2.1 | evolved_frontier |

## BP-OSD-tightened upper bounds (UNCERTIFIED — may overestimate)

| [[n,k,d]] | FOM | source |
|---|---|---|
| [[352,20,28]] | 44.5 | certified_broadened.md |
| [[840,16,46]] | 40.3 | certified.md |
| [[336,20,26]] | 40.2 | certified.md |
| [[280,12,30]] | 38.6 | certified_broadened.md |
| [[600,16,38]] | 38.5 | certified.md |
| [[780,16,42]] | 36.2 | certified.md |
| [[336,12,31]] | 34.3 | certified_broadened.md |
| [[686,12,44]] | 33.9 | certified.md |
| [[300,16,24]] | 30.7 | certified.md |
| [[320,12,28]] | 29.4 | certified_broadened.md |
| [[240,12,24]] | 28.8 | certified_broadened.md |
| [[280,10,28]] | 28.0 | certified_broadened.md |
| [[324,10,30]] | 27.8 | certified_broadened.md |
| [[208,16,19]] | 27.8 | certified_broadened.md |
| [[350,10,31]] | 27.5 | certified_broadened.md |
