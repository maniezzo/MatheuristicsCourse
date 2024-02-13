import copy

import numpy as np

def solve_GAP(cap, req, c):
   n = len(req[0])
   m = len(cap)

   # Initialize the table
   ST = []  # lista degli stati per ogni stage
   FO = []  # costi dei corrispondenti stati

   s = [[0,0,0]] # lista stati k=0 (nessun assegnamento)
   f = [0]

   ST.append(s)
   FO.append(f)

   for k in range(n):
      print(f"Stage {k}")
      print(ST[k])
      nexts = []
      nextf = []
      for idx in range(len(ST[k])):
         s = ST[k][idx]
         f = FO[k][idx]
         print(f"-- {s} cost {f}")
         for i in range(m):
            sn = copy.deepcopy(s)
            fn = f
            if(sn[i]+req[i][k] <= cap[i]):
               sn[i]+= req[i][k]
               fn   += c[i][k]
            else: continue
            if(sn in nexts):
               print(f"--------------- dominance {sn} cost {fn} or {FO[k][idx]}")
               ipos = nexts.index(sn)
               minval = min(nextf[ipos],fn)
               nextf[ipos] = minval
               fn = minval
            nexts.append(sn)
            nextf.append(fn)
            print(f"{sn} fo {fn}")
         if(len(nexts)==0):
            print("NO FEASIBLE SOLUTION")
            return -1,[]
      ST.append(nexts)
      FO.append(nextf)
   optimal_cost = min(FO[n])
   print(f"optimal cost: {optimal_cost}")

   # Backtrack to find the assignment
   assignments = []
   return optimal_cost, assignments

if __name__ == "__main__":
   # Example usage:
   capacities = [5, 5, 5]
   requests = [
      [2, 2, 3, 4],
      [2, 3, 1, 2],
      [3, 1, 2, 4]
   ]
   costs = [
      [2, 1, 1, 1],
      [1, 2, 5, 9],
      [1, 1, 3, 6]
   ]

   optimal_solution, assignments = solve_GAP(capacities, requests, costs)
   print("Optimal Solution:", optimal_solution)
   print("Assignments:", assignments)
