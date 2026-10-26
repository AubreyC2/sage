# ============================================================
# SageMath script: grobner_experiment.py  (ROBUST VERSION)
# Reliable per-instance timeout using multiprocessing
# ============================================================

import time
import multiprocessing as mp
from sage.all import *

INPUT_FILE = "/home/aubrey/PycharmProjects/PythonProject/backwardinput5"
OUTPUT_FILE = "backwardresults5.txt"

TIME_LIMIT = 5   # seconds per Groebner computation


# ============================================================
# ---------------- parsing utilities -------------------------
# ============================================================

def parse_poly(poly_str, R, gens):
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

    first = polys_str[0]
    tup = first[first.find("(")+1:first.find(")")]
    n = len(tup.split(","))

    R = PolynomialRing(QQ, n, "x")
    gens = R.gens()

    polys = [parse_poly(p, R, gens) for p in polys_str]

    return R, polys


# ============================================================
# ------------- worker (runs in separate process) ------------
# ============================================================

def gb_worker(polys, R, queue):
    """
    Runs Groebner basis computation in a child process.
    Sends result back through queue.
    """
    start = time.time()

    G = R.ideal(polys).groebner_basis()

    elapsed = time.time() - start
    max_deg = max(g.total_degree() for g in G)
    terms = sum(len(g.monomials()) for g in G)

    queue.put((elapsed, len(G), max_deg, terms))


# ============================================================
# ----------- safe timeout wrapper (ALWAYS WORKS) ------------
# ============================================================

def gb_stats_timeout(polys, R):

    queue = mp.Queue()
    p = mp.Process(target=gb_worker, args=(polys, R, queue))

    p.start()
    p.join(TIME_LIMIT)

    # still running → kill it
    if p.is_alive():
        p.terminate()
        p.join()
        return None, None, None, None, True

    # finished normally
    return (*queue.get(), False)


# ============================================================
# ----------------------- main loop --------------------------
# ============================================================

def main():

    with open(INPUT_FILE) as fin, open(OUTPUT_FILE, "w", buffering=1) as fout:

        # Header WITHOUT case number
        fout.write("time,size,deg,terms\n")

        for line in fin:

            line = line.strip()
            if not line:
                continue

            left, right = line.split("|")
            R, polys = parse_ideal(right)

            t, gsize, dmax, terms, timed_out = gb_stats_timeout(polys, R)

            if timed_out:
                print(f"❌ TIMEOUT after {TIME_LIMIT}s")
                fout.write(f"TIMEOUT,{TIME_LIMIT},,\n")
                continue

            print(f"✓ {t:.3f}s  size={gsize}  deg={dmax}  terms={terms}")
            fout.write(f"{t},{gsize},{dmax},{terms}\n")


# multiprocessing safety guard (IMPORTANT)
if __name__ == "__main__":
    mp.set_start_method("fork")  # fastest on Linux/macOS
    main()
