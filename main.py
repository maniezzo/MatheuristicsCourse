import numpy as np, pandas as pd
import json
import lppulp
import lportools
import lagrass
import lagrcap
import dynprogr
import dantzigwolfePULP as DW
import bendersPULP as BP

def main():
    fFromURL = False
    if(fFromURL): df = pd.read_json("http://astarte.csr.unibo.it/gapdata/homemade/example8x3.json")
    else:         df = pd.read_json("example8x3.json")
    c   = np.stack( df.cost.values ) # not a series of lists but an array
    req = np.stack( df.req.values )
    cap = df.cap.values

    idmethod = 6
    if(idmethod == 0):    lppulp.run_pulp(c,cap,req)
    elif(idmethod == 1):  lportools.run_ortools(c,cap,req)
    elif(idmethod == 2):  lagrass.run_subgr(c,req,cap, max_iterations=10,zub=326)
    elif(idmethod == 3):  lagrcap.run_subgr(c,req,cap, max_iterations=10,zub=326)
    elif(idmethod == 4):  dynprogr.solve_GAP(cap,req,c)
    elif(idmethod == 5):  DW.run_dw(cap,req,c)
    elif(idmethod == 6):  BP.run_benders(cap, req, c)

    return

if __name__ == "__main__":
    main()