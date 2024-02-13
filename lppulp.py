import pulp
import numpy as np

def run_pulp(c,cap,req):
   m = c.shape[0]
   n = c.shape[1]
   numvar=n*m

   # Create the 'prob' variable to contain the problem data
   prob = pulp.LpProblem("GAP-pulp", pulp.LpMinimize)

   # Decision variables
   x = pulp.LpVariable.dicts('x', range(numvar), lowBound=0, upBound=1, cat="Continuous")

   # The objective function
   c = c.flatten()
   prob += pulp.lpSum([x[j]*c.flatten()[j] for j in range(numvar)]), "cost"

   # The knapsack constraints
   for i in range(m):
      coeff = np.zeros(numvar)
      for j in range(n):
            coeff[i*n+j]=req[i,j]
      sumreq = pulp.lpSum([x[j] * coeff[j] for j in range(numvar)])
      prob += (sumreq <= cap[i], "Ckn{}".format(i))
      print(f"Constr knap{i}")

   # The assignment constraints
   for j in range(n):
      coeff = np.zeros(numvar)
      for i in range(m):
            coeff[i*n+j]=1
      sumreq = pulp.lpSum([x[j] * coeff[j] for j in range(numvar)])
      prob += (sumreq == 1, "Cas{}".format(j))
      print(f"Constr assgn{j}")

   # The problem data is written to an .lp file
   if(numvar<50):
      prob.writeLP("GAP_PULP.lp")

   # prob.solve() # let pulp decide the solver
   solver = pulp.getSolver('CPLEX_CMD', timeLimit=500)
   prob.solve(solver)

   # The status of the solution
   print("Status:", pulp.LpStatus[prob.status])
   # The optimal objective function value
   print("Total cost = ", pulp.value(prob.objective))
   # Primal and dual variables optimal value
   for v in prob.variables():
      print(v.name, "=", v.varValue)
   for name, c in list(prob.constraints.items()):
      print(name, ":", c, "\t dual", c.pi, "\tslack", c.slack)

   # ---------------------------------- integer solution
   for i in range(len(x)):
      x[i].cat = "Integer"

   prob.solve(solver)
   # The status of the solution
   print("Status:", pulp.LpStatus[prob.status])
   # The optimal objective function value
   print("Total cost = ", pulp.value(prob.objective))
   # Primal and dual variables optimal value
   for v in prob.variables():
      if(v.varValue > 0):
         print(v.name, "=", v.varValue)

   return