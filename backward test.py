# ============================================================
# SageMath script: grobner_experiment.py
# ============================================================

import time
from sage.all import *

INPUT_FILE = "/home/aubrey/PycharmProjects/PythonProject/backwardinput2"
OUTPUT_FILE = "backwardresults2.txt"


# ============================================================
# -------- parsing your (c,(e1,...,en)) format ---------------
# ============================================================

def parse_poly(poly_str, R, gens):
    """
    Convert:
        (2,(1,0,0)),(-3,(0,1,0))
    into Sage polynomial
    """
    if poly_str.strip() == "":
        return R(0)

    terms = poly_str.split("),(")

    f = R(0)

    for t in terms:
        t = t.replace("(", "").replace(")", "")
        c, exps = t.split(",", 1)

        coeff = QQ(int(c))
        exps = tuple(int(x) for x in exps.split(","))

        mon = coeff
        for g, e in zip(gens, exps):
            mon *= g**e

        f += mon

    return f


def parse_ideal(side):
    polys_str = side.split(";")

    # detect number of variables from first monomial
    first = polys_str[0]
    tup = first[first.find("(")+1:first.find(")")]
    n = len(tup.split(","))

    R = PolynomialRing(QQ, n, "x")
    gens = R.gens()

    polys = [parse_poly(p, R, gens) for p in polys_str]

    return R, polys


# ============================================================
# ---------------- complexity measures -----------------------
# ============================================================

def gb_stats(polys, R):
    I = R.ideal(polys)

    start = time.time()
    G = I.groebner_basis()
    elapsed = time.time() - start

    max_deg = max(g.total_degree() for g in G)
    terms = sum(len(g.monomials()) for g in G)

    return elapsed, len(G), max_deg, terms


# ============================================================
# ----------------------- main loop --------------------------
# ============================================================

with open(INPUT_FILE) as fin, open(OUTPUT_FILE, "w") as fout:

    for line in fin:
        line = line.strip()
        if not line:
            continue

        left, right = line.split("|")

        # only analyze messed-up side
        R, polys = parse_ideal(right)

        t, gsize, dmax, terms = gb_stats(polys, R)

        # write numbers only (easy for later plotting)
        fout.write(f"{t},{gsize},{dmax},{terms}\n")
