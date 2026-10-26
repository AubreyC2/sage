import random as rand
import multiprocessing as mp
from sage.rings.polynomial.toy_buchberger import *
import time
import os
import gc
from sage.all import *

# ======= CONFIG =======
DATA_FILE = "/home/aubrey/PycharmProjects/PythonProject/data_cleanedup.txt"
COOKED_FILE = "/home/aubrey/PycharmProjects/PythonProject/cooked.txt"
n = 3
var(['x' + str(i) for i in range(n)])
# ======================


def gb_stopwatch(F, ans):
    """Compute a Groebner basis and store stats in shared array."""
    t = time.time()
    try:
        G = set(F.gens())
        B = set((g1, g2) for g1 in G for g2 in G if g1 != g2)

        m = max([p.number_of_terms() for p in G]) if G else 0
        divisions = 0
        ans[0] = m
        ans[1] = divisions
        ans[2] = 0.0

        if not B:
            ans[2] = time.time() - t
            return

        while B:
            g1, g2 = select(B)
            B.remove((g1, g2))
            h = spol(g1, g2).reduce(G)

            if h != 0:
                B |= {(g, h) for g in G}
                G.add(h)

            m = max(m, max([p.number_of_terms() for p in G]))
            divisions += 1
            ans[0] = m
            ans[1] = divisions

        ans[2] = time.time() - t

    except Exception as e:
        print(f"[ERROR] gb_stopwatch failed: {e}")
        ans[0] = ans[0] if ans[0] > 0 else -1
        ans[1] = -1
        ans[2] = time.time() - t


def gen_dataset(NUM_IDEALS, MAX_IDEAL_SIZE, MAX_POLY_TERMS,
                MIN_COEF, MAX_COEF, MAX_DEG, TIME_LIMIT):

    st = time.time()
    ORDERINGS = ['lex', 'degrevlex', 'deglex',
                 'neglex', 'negdeglex', 'negdegrevlex', 'degneglex']

    # Dynamically choose how many to run in parallel based on CPU
    MAX_PARALLEL = min(os.cpu_count(), 6)  # 6 fits i7-12700H P-cores well
    print(f"[INFO] Using up to {MAX_PARALLEL} parallel processes.\n")

    for idx in range(NUM_IDEALS):
        # ---------- Generate one random ideal ----------
        R_base = PolynomialRing(QQ, 'x', n, order='lex')
        numpolys = rand.randint(1, MAX_IDEAL_SIZE)
        polyarrays = []
        polys = []

        for _ in range(numpolys):
            curpol = 0
            curpolarray = []
            numterms = rand.randint(1, MAX_POLY_TERMS)

            for __ in range(numterms):
                coef = rand.randint(MIN_COEF, MAX_COEF)
                deg = [rand.randint(0, MAX_DEG) for ___ in range(n)]
                curpolarray.append([coef, deg])

                term = coef
                for i in range(n):
                    term *= R_base.gens()[i] ** deg[i]
                curpol += term

            if curpol != 0:
                polys.append(curpol)
            polyarrays.append(curpolarray)

        if len(polys) == 0:
            continue

        print(f"\nIdeal {idx + 1}/{NUM_IDEALS}")

        # Split orderings into manageable batches
        for batch_start in range(0, len(ORDERINGS), MAX_PARALLEL):
            batch = ORDERINGS[batch_start:batch_start + MAX_PARALLEL]
            print(f"=== Running batch {batch_start // MAX_PARALLEL + 1} "
                  f"({len(batch)} orderings: {batch}) ===")

            processes = []
            for order_name in batch:
                R = PolynomialRing(QQ, 'x', n, order=order_name)
                polys_in_R = [R(p) for p in polys]
                I = R.ideal(polys_in_R)

                ans = mp.Array('d', 10)
                pr = mp.Process(target=gb_stopwatch, args=(I, ans))
                processes.append((order_name, pr, ans))
                pr.start()

            # Monitor batch
            t0 = time.time()
            while time.time() - t0 < TIME_LIMIT and any(p.is_alive() for _, p, _ in processes):
                time.sleep(0.1)

            # Collect results
            for order_name, pr, ans in processes:
                if pr.is_alive():
                    os.kill(pr.pid, 9)
                    result = "-1 -1 -1"
                    out_path = COOKED_FILE
                    print(f"  | {order_name:<12} timed out after {TIME_LIMIT}s")
                else:
                    a = [int(ans[0]), int(ans[1]), ans[2]]
                    result = f"{a[0]} {a[1]} {a[2]}"
                    out_path = DATA_FILE
                    print(f"  | {order_name:<12} done → "
                          f"MaxTerms={a[0]}, S-Polys={a[1]}, Time={a[2]:.2f}s")

                with open(out_path, 'a') as f:
                    f.write(f"{order_name} {repr(polyarrays)} {result}\n")

                gc.collect()

            # Give OS time to reclaim memory between batches
            time.sleep(1)

    total_time = time.time() - st
    print(f"\n[FINISHED] Processed {NUM_IDEALS} ideals across all 7 orderings in {total_time:.2f}s\n")


def main():
    NUM_IDEALS = 100
    MAX_DEG = 10
    MAX_IDEAL_SIZE = 5
    MAX_COEF = 10
    MIN_COEF = -10
    MAX_POLY_TERMS = 10
    TIME_LIMIT = 600  # seconds

    gen_dataset(NUM_IDEALS, MAX_IDEAL_SIZE, MAX_POLY_TERMS,
                MIN_COEF, MAX_COEF, MAX_DEG, TIME_LIMIT)


if __name__ == "__main__":
    main()
