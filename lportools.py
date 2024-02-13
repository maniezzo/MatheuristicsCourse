import numpy as np
from ortools.linear_solver import pywraplp

def run_ortools(c,cap,req):
   m = c.shape[0]
   n = c.shape[1]
   nvar=n*m

   # Create the linear solver
   solver = pywraplp.Solver.CreateSolver("SCIP")
   if not solver: return
   # Create the variables
   x = {}
   for j in range(nvar):
      x[j] = solver.NumVar(0, 1, "x[%i]" % j)
   print("LP: number of variables =", solver.NumVariables())

   # Create the objective function
   objective = solver.Objective()
   c = c.flatten()
   c = c.astype(float)
   for j in range(nvar):
      objective.SetCoefficient(x[j], c[j])
   objective.SetMinimization()

   constraints = []
   cap = cap.flatten()
   cap = cap.astype(float)
   # The knapsack constraints
   for i in range(m):
      constraints.append(solver.Constraint(0, cap[i],f"Ckn{i}")) # min max values
      for j in range(n):
         constraints[i].SetCoefficient(x[i * n + j], req[i,j].astype(float))
      print(f"Constr knap{i}")

   # The assignment constraints
   for j in range(n):
      constraints.append(solver.Constraint(1,1,f"Cas{j}")) # min max values
      for i in range(m):
         constraints[m+j].SetCoefficient(x[i * n + j], 1.)
      print(f"Constr assgn{j}")

   if(nvar < 50):
      with open("GAP_ORTOOLS.lp", "w") as fout:
         s = solver.ExportModelAsLpFormat(False)
         fout.write(s)

   status = solver.Solve()
   if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
      print(f"obj = {solver.Objective().Value()}")
      for j in range(len(x)):
         if(x[j].solution_value()>0.001):
            print(f"x{j} = {x[j].solution_value()}, reduced cost = {x[j].reduced_cost()}")
      for i in range(len(constraints)):
         print(f"constr dual value = {constraints[i].dual_value()}")

   # ---------------------------------- integer solution
   for i in range(len(x)):
      x[i].SetInteger(True)

   # Display output
   solver.EnableOutput()
   status = solver.Solve()
   if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
      print(f"obj = {solver.Objective().Value()}")
      for j in range(solver.NumVariables()):
         if(x[j].solution_value()>0.001):
            print(f"x{j} = {x[j].solution_value()}")
      print("Problem solved in %f milliseconds" % solver.wall_time())
      print("Problem solved in %d iterations" % solver.iterations())
      print("Problem solved in %d branch-and-bound nodes" % solver.nodes())

   return