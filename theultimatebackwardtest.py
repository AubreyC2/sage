# ============================================================
# Combined generator + Groebner complexity evaluator
# SAFE for Sage (no namespace collisions)
# Line-by-line processing (NO batching)
# ============================================================

import os
import time
import multiprocessing as mp
import random as pyrandom

from sage.all import PolynomialRing, QQ

# ============================================================
# ================= USER PARAMETERS ==========================
# ============================================================

NUM_VARIABLES = 5
DATASET_SIZE = 50

# Manually control invertible step range HERE
INVERTIBLE_STEPS_RANGE = range(1, 21)

COEFF_RANGE = (-5, 5)
MAX_DEG = 4
P_DEG = 5

TIME_LIMIT = 5   # seconds per Groebner computation

# ============================================================
# ================= OUTPUT DIRECTORY =========================
# ============================================================

BASE_DIR = "/home/aubrey/PycharmProjects/PythonProject/back_ward_test_data"

DATASET_PREFIX = "dataset_steps_"
RESULTS_PREFIX = "results_steps_"

os.makedirs(BASE_DIR, exist_ok=True)

# ============================================================
# =============== POLYNOMIAL UTILITIES ======================
# ============================================================

def rand_coeff():
    c = 0
    while c == 0:
        c = pyrandom.randint(*COEFF_RANGE)
    return c


def random_monomial(n, max_deg):
    exps = [0] * n
    var = pyrandom.randrange(n)
    exps[var] = pyrandom.randint(0, max_deg)
    return exps


def poly_add(p, q):
    r = p.copy()
    for m, c in q.items():
        r[m] = r.get(m, 0) + c
        if r[m] == 0:
            del r[m]
    return r


def poly_mul(p, q):
    r = {}
    for m1, c1 in p.items():
        for m2, c2 in q.items():
            m = tuple(a + b for a, b in zip(m1, m2))
            r[m] = r.get(m, 0) + c1 * c2
    return r


def random_multiplier(n):
    p = {}
    for _ in range(pyrandom.randint(1, 3)):
        exp = tuple(random_monomial(n, P_DEG))
        p[exp] = rand_coeff()
    return p

# ============================================================
# ============== SHAPE POSITION GENERATOR ===================
# ============================================================

def shape_position_ideal(n):
    polys = []

    # f1(x1)
    f1 = {}
    for d in range(MAX_DEG + 1):
        if pyrandom.random() < 0.7:
            exp = [0] * n
            exp[0] = d
            f1[tuple(exp)] = rand_coeff()
    polys.append(f1)

    # xi - gi(x1)
    for i in range(1, n):
        poly = {}

        exp = [0] * n
        exp[i] = 1
        poly[tuple(exp)] = 1

        for d in range(pyrandom.randint(0, MAX_DEG)):
            exp = [0] * n
            exp[0] = d
            poly[tuple(exp)] = poly.get(tuple(exp), 0) + rand_coeff()

        polys.append(poly)

    return polys

# ============================================================
# ============== INVERTIBLE OPERATIONS ======================
# ============================================================

def mess_up(polys, steps, n):
    polys = [p.copy() for p in polys]

    for _ in range(steps):
        i, j = pyrandom.sample(range(len(polys)), 2)
        polys[i] = poly_add(
            polys[i],
            poly_mul(polys[j], random_multiplier(n))
        )

    return polys

# ============================================================
# ================= STRING FORMAT ===========================
# ============================================================

def format_poly(poly):
    return ",".join(
        f"({c},({','.join(map(str, m))}))"
        for m, c in sorted(poly.items())
    )


def format_ideal(polys):
    return ";".join(format_poly(p) for p in polys)

# ============================================================
# ================== PARSING UTILITIES ======================
# ============================================================

def parse_poly(poly_str, R, gens):
    f = R(0)

    for t in poly_str.split("),("):
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
    n = len(polys_str[0].split(",")[1].strip("()").split(","))
    R = PolynomialRing(QQ, n, "x")
    gens = R.gens()
    return R, [parse_poly(p, R, gens) for p in polys_str]

# ============================================================
# ================= GROBNER WORKER ==========================
# ============================================================

def gb_worker(polys, R, queue):
    start = time.time()
    G = R.ideal(polys).groebner_basis()
    elapsed = time.time() - start

    queue.put((
        elapsed,
        len(G),
        max(g.total_degree() for g in G),
        sum(len(g.monomials()) for g in G)
    ))


def gb_stats_timeout(polys, R):
    queue = mp.Queue()
    p = mp.Process(target=gb_worker, args=(polys, R, queue))

    p.start()
    p.join(TIME_LIMIT)

    if p.is_alive():
        p.terminate()
        p.join()
        return None, None, None, None, True

    return (*queue.get(), False)

# ============================================================
# ======================== MAIN =============================
# ============================================================

def main():

    for steps in INVERTIBLE_STEPS_RANGE:

        dataset_file = os.path.join(
            BASE_DIR, f"{DATASET_PREFIX}{steps}.txt"
        )
        results_file = os.path.join(
            BASE_DIR, f"{RESULTS_PREFIX}{steps}.txt"
        )

        with open(dataset_file, "w") as dset, \
             open(results_file, "w", buffering=1) as res:

            res.write("time,size,deg,terms\n")

            for _ in range(DATASET_SIZE):

                original = shape_position_ideal(NUM_VARIABLES)
                messed = mess_up(original, steps, NUM_VARIABLES)

                dset.write(
                    format_ideal(original) + " | " +
                    format_ideal(messed) + "\n"
                )

                R, polys = parse_ideal(format_ideal(messed))
                t, s, d, terms, timeout = gb_stats_timeout(polys, R)

                if timeout:
                    res.write(f"TIMEOUT,{TIME_LIMIT},,\n")
                else:
                    res.write(f"{t},{s},{d},{terms}\n")

        print(f"✓ Finished invertible steps = {steps}")

# ============================================================
# ===================== ENTRY POINT ==========================
# ============================================================

if __name__ == "__main__":
    mp.set_start_method("fork")
    main()
