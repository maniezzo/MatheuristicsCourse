import copy

import numpy as np
import pulp

class MIPprob:
   def __init__(self,name,type,cost,tbl,rhs,sense):
      self.name = name
      self.type = type
      self.rhs = rhs
      self.tbl = tbl  # coefficients of the tableau
      self.c = cost
      self.nvar = len(cost)

      self.prob = pulp.LpProblem(name, pulp.LpMinimize)
      # Create the variables
      self.x = [pulp.LpVariable(f"x{i:04d}", lowBound=0, upBound=1, cat=type) for i in range(self.nvar)]
      #print(f"{name}: number of variables =", self.nvar)

      # Create the objective function
      self.c = self.c.flatten()
      self.prob += pulp.lpSum([self.x[j] * self.c.flatten()[j] for j in range(self.nvar)]), "cost"

      self.constraints = []
      for i in range(len(rhs)):
         sumreq = pulp.lpSum([self.x[j]*self.tbl[i][j] for j in range(self.nvar)])
         if (sense[i] < 0):
            self.prob += (sumreq <= rhs[i], f"c{i}")
         elif (sense[i] == 0):
            self.prob += (sumreq == rhs[i], f"c{i}")
         elif (sense[i] > 0):
            self.prob += (sumreq >= rhs[i], f"c{i}")
         #print(f"Constr {i}")
      if (name=="master" and self.nvar < 30):
         self.prob.writeLP("DWmaster.lp")
      if (name=="subpr" and self.nvar < 30):
         self.prob.writeLP("DWsubpr.lp")

   def solve(self):
      # prob.solve() # let pulp decide the solver
      solver = pulp.getSolver('CPLEX_CMD', timeLimit=5000, msg=False)

      self.prob.solve(solver)
      # The status of the solution
      #print("Status:", pulp.LpStatus[self.prob.status])
      if(pulp.LpStatus[self.prob.status] != "Optimal"): exit()
      # The optimal objective function value
      opt = pulp.value(self.prob.objective)
      print("Total cost = ", opt)
      # Primal and dual variables optimal values
      xopt = []
      zcheck = 0
      k = 0
      for v in self.prob.variables():
         xopt.append(v.varValue)
         zcheck += v.varValue*self.c[k]
         k+=1
         #print(v.name, "=", v.varValue)
      if(zcheck != opt):
         print(f"Ooops {zcheck} {opt}")
         exit(1)

      duals = []
      for name, c in list(self.prob.constraints.items()):
         duals.append(c.pi)
         #print(name, ":", c, "\t dual", c.pi, "\tslack", c.slack)
      return opt, xopt, duals

def run_dw(cap,req,c):
   solver_list = pulp.listSolvers(onlyAvailable=True)
   print(f"Pulp: available solvers: {solver_list}")
   m = c.shape[0]
   n = c.shape[1]
   nvarSub = n*m

   # Create the problems, initializations
   cMast = np.array([1000000])
   tblMast = np.ones(n+m).reshape(n+m,1)
   rhsMast = np.ones(n+m)
   snsMast = np.zeros(n+m)  # constraint sense: -1 <=, 0 =, +1 >=

   tblSubp = []
   for i in range(m):
      coeff = np.zeros(nvarSub)
      for j in range(n):
         coeff[i * n + j] = req[i,j]
      tblSubp.append(coeff)
   tblSubp = np.array(tblSubp)
   rhsSubp = cap
   snsSubp = np.full(m,-1)

   cont  = 0
   fCont = True
   while (cont < 50 and fCont):
      cont += 1
      # master
      MSTP= MIPprob("master","Continuous",cMast,tblMast,rhsMast,snsMast)
      opt, xopt, duals = MSTP.solve()
      idOpt = []
      for i in range(len(xopt)):
         if(xopt[i]>0):
            idOpt.append(i)
            print(f"col {i} - {[tblMast[j][i] for j in range(n+m)]}")
      print(f"MASTER sol {idOpt}")
      v = duals[:n]
      u = duals[n:]

      # subproblem
      nImprove = 0
      for i in range(m):
         cSubp = copy.deepcopy(c)
         cSubp[i] = [c[i][j]-v[j] for j in range(n)]
         cSubp = cSubp.flatten()
         SUBP = MIPprob("subpr","Integer",cSubp,[tblSubp[i]],[rhsSubp[i]],[snsSubp[i]])
         opt, xopt, duals = SUBP.solve()
         redcost = opt - u[i]
         if(redcost<0):
            nImprove  += 1
            cMastCol   = 0
            tblMastCol = np.zeros(n+m)
            for k in range(nvarSub):
               if(xopt[k] > 0):
                  j = k%n
                  #print(f"Insol: redcost {redcost} server {i} cli {j} var {k} check {n*i+j}")
                  cMastCol += c[i][j]
                  tblMastCol[j]   = 1  # clients first
                  tblMastCol[n+i] = 1  # server the client is assigned to
            cMast = np.append(cMast,cMastCol)
            tblMast = np.c_[tblMast,tblMastCol]
            print(f"subpr: new col {tblMastCol}")
      if(nImprove==0):
         fCont = False
         print("Optimum found")

   return

if __name__ == "__main__":
   # Example usage:
   cap = [5, 5, 5]
   req = [
      [2, 2, 3, 4],
      [2, 3, 1, 2],
      [3, 1, 2, 4]
   ]
   cost = [
      [1, 5, 4, 7],
      [2, 3, 5, 9],
      [3, 4, 5, 6]
   ]

   run_dw(np.array(cap),np.array(req),np.array(cost))
   exit()