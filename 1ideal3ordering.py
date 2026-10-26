import random as rand
import multiprocessing as mp
import time
import os
from sage.rings.polynomial.toy_buchberger import *
from sage.all import *

n = 3
var(['x' + str(i) for i in range(n)])


def gb_stopwatch(F, ans):
    t = time.time()
    G = set(F.gens())
    B = set((g1, g2) for g1 in G for g2 in G if g1 != g2)

    m = max([p.number_of_terms() for p in G])
    divisions = 0

    while B:
        g1, g2 = select(B)
        B.remove((g1, g2))
        h = spol(g1, g2).reduce(G)
        if h != 0:
            B = B.union((g, h) for g in G)
            G.add(h)
        m = max(m, max([p.number_of_terms() for p in G]))
        divisions += 1

    elapsed = time.time() - t
    ans[0] = m
    ans[1] = divisions
    ans[2] = elapsed


def run_with_timeout(I, TIME_LIMIT):
    """Run gb_stopwatch with a timeout."""
    ans = mp.Array('d', 10)
    pr = mp.Process(target=gb_stopwatch, args=(I, ans))
    pr.start()
    pr.join(TIME_LIMIT)
    if pr.is_alive():
        os.kill(pr.pid, 9)
        pr.join()
        return "-1 -1 -1"
    else:
        a = [int(ans[0]), int(ans[1])] + [ans[j + 2] for j in range(len(ans) - 2)]
        return f"{a[0]} {a[1]} {a[2]}"


def make_random_ideal_data(R, MAX_IDEAL_SIZE, MAX_POLY_TERMS, MIN_COEF, MAX_COEF, MAX_DEG):
    """Generate one random ideal and return its data representation + actual ideal."""
    numpolys = rand.randint(1, MAX_IDEAL_SIZE)
    polys = []
    polyarrays = []
    for _ in range(numpolys):
        curpol = 0
        curpolarray = []
        numterms = rand.randint(1, MAX_POLY_TERMS)
        for __ in range(numterms):
            coef = rand.randint(MIN_COEF, MAX_COEF)
            deg = [rand.randint(0, MAX_DEG) for _ in range(n)]
            curpolarray.append([coef, deg])
            term = coef
            for i in range(n):
                term *= R.gens()[i] ** deg[i]
            curpol += term
        if curpol != 0:
            polys.append(curpol)
        polyarrays.append(curpolarray)
    I = R.ideal(polys)
    return polyarrays, polys, I


def get_ring(ordering):
    """Return polynomial ring for given ordering index."""
    order_names = [
        "lex", "degrevlex", "deglex", "neglex",
        "negdeglex", "negdegrevlex", "degneglex"
    ]
    R = PolynomialRing(QQ, 'x', n, order=order_names[ordering])
    return R, order_names[ordering]


def process_ordering(shared_ideals, ordering, TIME_LIMIT, output_file):
    """Run all stored ideals for one specific ordering."""
    R, order_name = get_ring(ordering)
    print(f"⚙️  Worker for {order_name} started...", flush=True)
    st = time.time()

    for idx, polyarrays in enumerate(shared_ideals):
        polys = []
        for curpolarray in polyarrays:
            curpol = sum(
                coef * prod(R.gens()[i] ** deg[i] for i in range(n))
                for coef, deg in curpolarray
            )
            if curpol != 0:
                polys.append(curpol)
        I = R.ideal(polys)
        result = run_with_timeout(I, TIME_LIMIT)
        with open(output_file, 'a') as f:
            f.write(f"{ordering} {repr(polyarrays)} {result}\n")
        print(f"✅ [{order_name}] Ideal {idx + 1}/{len(shared_ideals)} done -> {result}", flush=True)

    print(f"🏁 {order_name} finished in {time.time() - st:.2f}s", flush=True)


def main():
    NUM_IDEALS = 100
    MAX_DEG = 10
    MAX_IDEAL_SIZE = 5
    MAX_COEF = 10
    MIN_COEF = -10
    MAX_POLY_TERMS = 10
    TIME_LIMIT = 1200  # seconds
    OUTPUT_FILE = "data3_revised_sameideal.txt"
    ORDERINGS = [6, 4, 5]  # Only 3 orderings

    # Base ring just for generating random polynomial shapes
    R_base = PolynomialRing(QQ, 'x', n, order='lex')

    # Generate all random ideals ONCE
    shared_ideals = []
    for _ in range(NUM_IDEALS):
        polyarrays, _, _ = make_random_ideal_data(
            R_base, MAX_IDEAL_SIZE, MAX_POLY_TERMS, MIN_COEF, MAX_COEF, MAX_DEG
        )
        shared_ideals.append(polyarrays)

    # Spawn one process per ordering (each uses the same shared_ideals list)
    processes = [
        mp.Process(target=process_ordering,
                   args=(shared_ideals, o, TIME_LIMIT, OUTPUT_FILE))
        for o in ORDERINGS
    ]

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    print("🎉 All 3 orderings complete! Data saved to data3_revised.txt")


if __name__ == "__main__":
    main()
