"""
DOES NOT WORK. FOR SOME REASON I CANNOT GET CORRECT DUAL VARABLES
IT AUTONOMOUSLY CONVERTS THE MASTER INTO INTEGER
"""
import numpy as np
from ortools.linear_solver import pywraplp

class MIPprob:
   def __init__(self,name,type,solver,m,n,nvar,cap,req,cost):
      self.name = name
      self.type = type
      self.m=m
      self.n=n
      self.nvar = nvar
      self.solver=solver

      # Create the variables
      self.x = {}
      for j in range(self.nvar):
         self.x[j] = self.solver.NumVar(0.0, solver.infinity(), f"x{j}")
         #if(type=="int"):
         #   self.x[j].SetInteger(True)
      print(f"{name}: number of variables =", self.solver.NumVariables())

      # Create the objective function
      self.objective = self.solver.Objective()
      self.c = cost.flatten()
      self.c = self.c.astype(float)
      for j in range(self.nvar):
         self.objective.SetCoefficient(self.x[j], self.c[j])
      self.objective.SetMinimization()

      self.constraints = []
      self.cap = cap.flatten()
      self.cap = self.cap.astype(float)
      if(name=="master"):
         for j in range(self.n):
            self.constraints.append(self.solver.Constraint(1,1,f"cli{j}")) # min max values
            self.constraints[j].SetCoefficient(self.x[0], 1.)
            print(f"{self.name} Constr client{j}")
         for i in range(self.m):
            self.constraints.append(self.solver.Constraint(1, 1, f"ser{i}"))  # min max values
            self.constraints[n+i].SetCoefficient(self.x[0], 1.0)
            print(f"{self.name} Constr server{i}")
         with open("DWmaster.lp", "w") as fout:
            s = self.solver.ExportModelAsLpFormat(False)
            fout.write(s)
      elif(name=="subpr"):
         # The knapsack constraints
         for i in range(m):
            self.constraints.append(self.solver.Constraint(0, self.cap[i], f"Ckn{i}"))  # min max values
            for j in range(n):
               self.constraints[i].SetCoefficient(self.x[i * n + j], req[i, j].astype(float))
            print(f"Constr knap{i}")
            with open("DWsubpr.lp", "w") as fout:
               s = solver.ExportModelAsLpFormat(False)
               fout.write(s)
         return

   def solve(self):
      self.solver.EnableOutput()
      status = self.solver.Solve()
      if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
         print(f"{self.name} obj = {self.solver.Objective().Value()}")
         for j in range(len(self.x)):
            if(self.x[j].solution_value()>0.001):
               print(f"{self.name} x{j} = {self.x[j].solution_value()}")

         duals = []
         for i in range(len(self.constraints)):
            print(f"{self.name} constr {i} dual value = {self.constraints[i].dual_value()}")
            duals.append(self.constraints[i].dual_value())

         if(self.type != "int"):
            for j in range(len(self.x)):
               #if (self.x[j].solution_value() > 0.001):
                  print(f"{self.name} {j} reduced cost = {self.x[j].reduced_cost()}")
         else:
            print("Problem solved in %f milliseconds" % self.solver.wall_time())
            print("Problem solved in %d iterations" % self.solver.iterations())
            print("Problem solved in %d branch-and-bound nodes" % self.solver.nodes())

         return duals

   def addcolumn(selfself):
      return

def run_dw(cap,req,c):
   m = c.shape[0]
   n = c.shape[1]
   nvar=n*m

   # Create the master problem
   msolver = pywraplp.Solver.CreateSolver("SCIP")
   if not msolver: return

   MSTP= MIPprob("master","lp",msolver,m,n,1,cap,req,np.array([1000000]))
   duals = MSTP.solve()
   v = duals[:n]
   u = duals[n:]

   # Create the subproblem
   subsolver = pywraplp.Solver.CreateSolver("SCIP")
   if not subsolver: return
   SUBP = MIPprob("subpr","lp",subsolver,m,n,nvar,cap,req,c)

   for i in range(m):
      ci = c[i]
      ci = [ci[j]-v[j] for j in range(n)]
   duals = SUBP.solve()

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