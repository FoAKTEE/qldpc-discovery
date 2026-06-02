"""qcode: a minimal, verified kernel for bivariate bicycle (BB) CSS codes.

Discovered cold from the mathematics: GF(2) linear algebra, the BB
construction, code dimension k, and two independent distance routines
(exhaustive low-weight enumeration and an exact MILP).
"""

from . import gf2, bb, distance, search

__all__ = ["gf2", "bb", "distance", "search"]
