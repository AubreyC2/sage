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
    return


def run_with_timeout(I, TIME_LIMIT):
    """Run gb_stopwatch with a timeout (no nested mp.Processes inside Pool)."""
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


def gen_dataset(NUM_IDEALS, ORDERING, MAX_IDEAL_SIZE, MAX_POLY_TERMS,
                MIN_COEF, MAX_COEF, MAX_DEG, TIME_LIMIT, output_file):
    st = time.time()

    order_names = [
        "lex", "degrevlex", "deglex", "neglex",
        "negdeglex", "negdegrevlex", "degneglex"
    ]

    order_name = order_names[ORDERING]
    print(f"⚙️  Worker for {order_name} started...", flush=True)

    if ORDERING == 0:
        R = PolynomialRing(QQ, 'x', n, order='lex')
    elif ORDERING == 1:
        R = PolynomialRing(QQ, 'x', n, order='degrevlex')
    elif ORDERING == 2:
        R = PolynomialRing(QQ, 'x', n, order='deglex')
    elif ORDERING == 3:
        R = PolynomialRing(QQ, 'x', n, order='neglex')
    elif ORDERING == 4:
        R = PolynomialRing(QQ, 'x', n, order='negdeglex')
    elif ORDERING == 5:
        R = PolynomialRing(QQ, 'x', n, order='negdegrevlex')
    elif ORDERING == 6:
        R = PolynomialRing(QQ, 'x', n, order='degneglex')

    for idx in range(NUM_IDEALS):
        t = time.time()
        numpolys = rand.randint(1, MAX_IDEAL_SIZE)
        polyarrays = []
        polys = []
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
        result = run_with_timeout(I, TIME_LIMIT)

        with open(output_file, 'a') as f:
            f.write(f"{str(ORDERING)} {repr(polyarrays)} {result}\n")

        print(f"✅ [{order_name}] Ideal {idx + 1}/{NUM_IDEALS} done -> {result}",
              flush=True)

    print(f"🏁 {order_name} finished in {time.time() - st:.2f}s", flush=True)


def main():
    NUM_IDEALS = 100
    MAX_DEG = 10
    MAX_IDEAL_SIZE = 5
    MAX_COEF = 10
    MIN_COEF = -10
    MAX_POLY_TERMS = 10
    TIME_LIMIT = 1500  # seconds
    OUTPUT_FILE = "data3_revised.txt"

    orderings = [6, 4, 5]  # Only 3 workers
    processes = [
        mp.Process(
            target=gen_dataset,
            args=(NUM_IDEALS, o, MAX_IDEAL_SIZE, MAX_POLY_TERMS,
                  MIN_COEF, MAX_COEF, MAX_DEG, TIME_LIMIT, OUTPUT_FILE)
        )
        for o in orderings
    ]

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    print("🎉 All 3 orderings complete! Data saved to data3_revised.txt")


if __name__ == "__main__":
    main()
