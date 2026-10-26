import random as rand
import multiprocessing as mp
from sage.rings.polynomial.toy_buchberger import *
import time
from sage.all import *
n = 3
var(['x' + str(i) for i in range(n)])

def gb_stopwatch(F, op_limit, t, term_limit=1000    ):
    G = set(F.gens())
    B = set((g1, g2) for g1 in G for g2 in G if g1 != g2)

    divisions = 0

    while divisions < op_limit and B:
        g1, g2 = select(B)
        B.remove((g1, g2))
        h = spol(g1, g2).reduce(G)

        if h != 0:
            # Check if new polynomial is "too big"
            if h.number_of_terms() > term_limit:
                print(f"Aborting: polynomial exceeded {term_limit} terms")
                break
            B = B.union((g, h) for g in G)
            G.add(h)

        divisions += 1

        # Just for light progress monitoring (optional)
        if divisions % 10 == 0:
            elapsed = time.time() - t
            print(f"[step {divisions}] elapsed {elapsed:.2f}s, "
                  f"basis size {len(G)}, "
                  f"max terms {max(p.number_of_terms() for p in G)}")

    return divisions

def gen_dataset(OP_LIMIT, NUM_IDEALS, ORDERING, MAX_IDEAL_SIZE, MAX_POLY_TERMS,
                MIN_COEF, MAX_COEF, MAX_DEG):
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

    rand.seed(int(0)) # needed to ensure that each ideal is used with each ordering

    t = time.time()
    with open('data.txt', 'a') as f:
        for _ in range(NUM_IDEALS):
            numpolys = rand.randint(1,MAX_IDEAL_SIZE)
        polyarrays = []
        polys = []
        for i in range(numpolys):
            curpol = 0
            curpolarray = []
            numterms = rand.randint(1,MAX_POLY_TERMS)
            for j in range(numterms):
                coef = rand.randint(MIN_COEF, MAX_COEF)
                deg = [rand.randint(0,MAX_DEG) for __ in range(n)]
                curpolarray.append([coef, deg])
                term = coef
                for i in range(n):
                    term *= R.gens()[i]**deg[i]
                curpol += term
            if curpol != 0: polys.append(curpol)
            polyarrays.append(curpolarray)
        for i in range(5-numpolys):
            break
        # TODO append array representing zero array to polys
            # can be done post dataset generation

        I = R.ideal(polys)
        result = gb_stopwatch(I, OP_LIMIT, t)

        for poly in polys:
            print(poly)
        print(polyarrays)
        print(f"{result} polys computed")
        # totaltime += result
        # print(f'run number {i}: The current runtime is {totaltime} seconds.', end=' ')
        # if result == TIME_LIMIT:
        #     print('The previous computation timed out.')
        # else:
        #     print(f'The previous computation took {result} seconds.')
        # print(f'ETA: {totaltime/(i+1) * (NUM_SAMPLES - i)} seconds')

        # to_write = ""
        # for B in A:
        #     for j in B:
        #         to_write += str(j) + " "
        # to_write += str(result)
        # to_write += "\n"
        # f.write(to_write)
    print(f"{time.time()-t} seconds elapsed")

def main():
    OP_LIMIT = 1000
    NUM_IDEALS = 10
    MAX_DEG = 10
    MAX_IDEAL_SIZE = 6
    MAX_COEF = 10
    MIN_COEF = -10
    MAX_POLY_TERMS = 10

    gen_dataset(100,
                1,
                0,
                MAX_IDEAL_SIZE,
                MAX_POLY_TERMS,
                MIN_COEF,
                MAX_COEF,
                MAX_DEG)

    # processes = [mp.Process(target=gen_dataset,
    #                         args=(OP_LIMIT,
    #                               NUM_IDEALS,
    #                               _,
    #                               MAX_IDEAL_SIZE,
    #                               MAX_POLY_TERMS,
    #                               MIN_COEF,
    #                               MAX_COEF,
    #                               MAX_DEG)
    #                         )
    #              for _ in range(7)]
    # for p in processes:
    #     p.start()

main()

if __name__ == "__main__":
    main()
