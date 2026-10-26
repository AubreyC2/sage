import random as rand
import multiprocessing as mp
from sage.rings.polynomial.toy_buchberger import *
import time
import os
from sage.all import *

n = 3
var(['x' + str(i) for i in range(n)])

def gb_stopwatch(F, term_bound, ans):
    t = time.time()
    G = set(F.gens())
    B = set((g1, g2) for g1 in G for g2 in G if g1 != g2)

    m = max([p.number_of_terms() for p in G]) # max or sum?

    while m < term_bound and B:
        g1, g2 = select(B)
        B.remove((g1, g2))
        #print(maxcoef)
        h = spol(g1, g2).reduce(G)

        if h != 0:
            B = B.union((g, h) for g in G)
            G.add(h)
        #print(G, divisions)

        m = max([p.number_of_terms() for p in G]) # max or sum?
        #print(f"numterms {[p.number_of_terms() for p in G]}")
        #print(f"degs {[p.degrees() for p in G]}")
    print(f"{time.time()-t} seconds elapsed")
    #print(f"{m} max num terms")
    ans.value = m
    return
    # largest coefficient seems like a decent-ish predictor idk
                   # we can track more info later

def gen_dataset(OP_LIMIT, NUM_IDEALS, ORDERING, MAX_IDEAL_SIZE, MAX_POLY_TERMS,
                MIN_COEF, MAX_COEF, MAX_DEG, TIME_LIMIT):
    st = time.time()
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

    #rand.seed(int(0)) # needed to ensure that each ideal is used with each ordering

    for _ in range(NUM_IDEALS):
        t = time.time()
        with open('data.txt', 'a') as f:
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
            ans = mp.Value('i',0)
            pr = mp.Process(target=gb_stopwatch, args=(I,OP_LIMIT,ans))
            pr.start()
            result = 0
            print(pr.pid)
            while time.time() - t < TIME_LIMIT and pr.is_alive():
                pass
            if time.time() - t >= TIME_LIMIT:
                os.kill(pr.pid, int(9))
                print("cooked")
                print(f"----{_}")
                result = -1
            else:
                print(ans.value)
                print(f"----{_}")
                result = ans.value

            # for poly in polys:
            #     print(poly)
            #print(polyarrays)
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
            f.write(f"{str(ORDERING)} {repr(polyarrays)} {result}\n")
    print(f"{time.time()-st} seconds elapsed for the whole thing")

def main():
    OP_LIMIT = 800
    NUM_IDEALS = 100
    MAX_DEG = 10
    MAX_IDEAL_SIZE = 5
    MAX_COEF = 10
    MIN_COEF = -10
    MAX_POLY_TERMS = 10
    TIME_LIMIT = 900 # in seconds

    # gen_dataset(OP_LIMIT,
    #             10,
    #             0,
    #             MAX_IDEAL_SIZE,
    #             MAX_POLY_TERMS,
    #             MIN_COEF,
    #             MAX_COEF,
    #             MAX_DEG)

    processes = [mp.Process(target=gen_dataset,
                            args=(OP_LIMIT,
                                  NUM_IDEALS,
                                  _,
                                  MAX_IDEAL_SIZE,
                                  MAX_POLY_TERMS,
                                  MIN_COEF,
                                  MAX_COEF,
                                  MAX_DEG,
                                  TIME_LIMIT)
                            )
                 for _ in range(7)]
    for p in processes:
        p.start()

main()

if __name__ == "__main__":
    main()
