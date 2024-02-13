# Lagrangian, RELAXING ASSIGNMENTS
import numpy as np
# -*- coding: utf-8 -*-
from pulp import *

def isFeasible(x, cost, m, n):
   z = 0
   for j in range(n):
      nassigned = 0
      for i in range(m):
         nassigned += x[i * n + j].varValue
         z = z + x[i * n + j].varValue * cost[i][j]
      if (nassigned != 1):
         z = -1
         return z
   return z

def initialize_subpr(m,n,cost,cap,req,lambdas,categ):
   # variables
   x_vars = pulp.LpVariable.dicts("x", (range(m), range(n)),
                                  lowBound=0,
                                  upBound=1,
                                  cat=categ)

   prob = LpProblem("GAP_Lagrangian_subproblem", LpMinimize)
   prob += lpSum([cost[i][j] * x_vars[i][j] for i in range(m) for j in range(n)]), "Subpr_cost"

   # capacity constraints
   for i in range(m):
      sumreq = lpSum([x_vars[i][j] * req[i][j] for j in range(n)])
      prob += (sumreq <= cap[i], "Req_to_{}".format(i))

   prob.setObjective(lpSum([(cost[i][j] - lambdas[j]) * x_vars[i][j] for i in range(m) for j in range(n)]))
   return prob, x_vars

# subgradient, relaxing assignments and MIPping knapsacks
def run_subgr(cost, req, cap, max_iterations=50, categ="Integer",zub = float('inf')):
   print("Starting subgradient")
   alpha = 4.0
   m = cost.shape[0]
   n = cost.shape[1]
   n_range = range(n)

   zlb   = 0           # overall lower bound
   lstLB = []          # list of all lower bounds
   initial_multiplier = 0
   lambdas            = [initial_multiplier] * n

   prob2, x_vars = initialize_subpr(m,n,cost,cap,req,lambdas,categ)
   eps       = 1e-6
   iteration = 0
   ziter     = 0

   # lagrangian subgradient loop
   while iteration <= max_iterations:
      iteration += 1

      # solve subproblem: sum of lambdas added later
      prob2.setObjective(lpSum([(cost[i][j] - lambdas[j]) * x_vars[i][j] for i in range(m) for j in range(n)]))
      if iteration == 1: prob2.writeLP("GAPlagrass.lp")
      status = prob2.solve(PULP_CBC_CMD(msg=False))

      if (prob2.status < 1):
         print("*** MIP fails, stopping at iteration: %d" % iteration)
         break
      elif prob2.status == 1:
         sum_penalties = sum(lambdas)
         ziter = value(prob2.objective) + sum_penalties
         if (ziter > zlb):
            zlb = ziter
         lstLB.append(ziter)

      subgrads = [0] * n
      xval = []
      for i in range(m):
         for j in range(n):
            xval.append(prob2.variables()[i * n + j].varValue)
            if prob2.variables()[i * n + j].varValue > 0: # if in solution
               subgrads[j] -= 1 # (rhs) - sum x_i
      for j in range(n):
         subgrads[j] += 1       # rhs
      sumSubGrad2 = sum(subgrads[j] * subgrads[j] for j in range(n))

      zubiter = isFeasible(prob2.variables(), cost, m, n)
      if (zubiter >= 0):
         if (zubiter < zub):
            zub = zubiter
      else:
         zubiter = float('inf')

      print('iter %d:\n\t ziter=%g, lambda=%s, subgrads=%s' % (iteration, ziter, str(lambdas), str(subgrads)))
      print('iter %d:xval=%s' % (iteration, str(xval)))

      if (zub - zlb < 1):
         print("* Optimum found, ziter={:g}, zlb={:g}, #iteratio={}".format(ziter, zlb, iteration))
         break
      else:
         # update lambdas and start loop again.
         fakeZub = min(zubiter, 1.2 * zlb + 1)
         fakeZub = zub
         step    = alpha * (fakeZub - zlb) / sumSubGrad2;
         lambdas = [(lambdas[j] + step * subgrads[j]) for j in n_range]
         if (iteration % 10 == 0):
            print('iter {0}: zlb={1:g} zub={2:g} lambda={3}'.format(iteration, zlb, zub, lambdas))

   return lstLB