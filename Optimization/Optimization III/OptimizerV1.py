# -*- coding: utf-8 -*-
"""
Created on Thu May  9 19:42:27 2024

@author: Sathma Goonathilaka
"""
# ------------------------------------------------------------------------- #
# This function solves a linear optimization problem under the given 
# objective function, and the 6 constraints that are subjected to 
# 5 different scenarios. 
# It then returns the FCRD-Down bidding capacities(c_D), FCRD-Up bidding capacities(c_U) 
# of the 24 hours for all 5 scenarios of a given day, a nested list (cD_clus) containing 
# 5 lists where each list contains the c_D values of the 24 hours of each scenario, 
# a nested list (cU_clus) containing 5 lists where each list contains the c_U values 
# of the 24 hours of each scenario, and the maximized income(obj) for the given day.

# The inputs to the function are:
    #1. minimum bidding capacity requirement to enter the FCRD market (c_MinBid)
    #2. baseline consumption values for the 24 hours for that given day 
    #...under 5 different scenarios (c_B)
    #3. FCRD-Down prices for the 24 hours for that given day under 5 different 
    #...scenarios (p_D)
    #4. FCRD-Up prices for the 24 hours for that given day under 5 different 
    #...scenarios (p_U)
    #5. FCRD-Up capacity reserves available for the 24 hours for that given day 
    #...under 5 different scenarios (Up_cap)
    #6. FCRD-Down capacity reserves available for the 24 hours for that given day 
    #...under 5 different scenarios (Down_cap)
    #7. Maximum consumption values for the 24 hours (P_max)
    #8. Minimum consumption values for the 24 hours for that given day under 5 
    #...different scenarios (P_min)
    #9. Weighting factors of the 5 scenarios for that given day (merged_weighted_ind)
# ------------------------------------------------------------------------- #

import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory

def Optimizer(c_MinBid, c_B, p_D, p_U, Up_cap, Down_cap, P_max, P_min, ind_W):
    model = pyo.ConcreteModel() # Creates an optimization model
    
    cD_clus = []
    cU_clus = []

    range_s = range(5) # Number of scenarios per day
    range_h = range(24) # Number of hours per day                                       
    model.c_D = pyo.Var(range_s, range_h, bounds = (0,None)) # Decision variable.
    # Creates 2-D positions for c_D of a certain day. The first dimension represents 
    # the scenarios, while the other dimension represents the hours per day.
    # c_D can only have non-negative reals.
    model.c_U = pyo.Var(range_s, range_h, bounds = (0,None)) # Decision variable.
    # Creates 2-D positions for c_U of a certain day. The first dimension represents 
    # the scenarios, while the other dimension represents the hours per day.
    # c_U can only have non-negative reals.
    
    model.zD = pyo.Var(range_s, range_h, within = Binary) # Creates the 2-D binary
    # variable zD. Here, the first dimension represents the scenarios, while the
    # other dimension represents the hours per day.
    model.zU = pyo.Var(range_s, range_h, within = Binary) # Creates the 2-D binary
    # variable zU. Here, the first dimension represents the scenarios, while the
    # other dimension represents the hours per day.
    
    c_D = model.c_D
    c_U = model.c_U
    zD = model.zD
    zU = model.zU
        
    model.C1 = pyo.ConstraintList()
    model.C2 = pyo.ConstraintList()
    model.C3 = pyo.ConstraintList()
    model.C4 = pyo.ConstraintList()
    model.C5 = pyo.ConstraintList()
    model.C6 = pyo.ConstraintList()
    
    for s in range_s: # Accessing each scenario
        for h in range_h: # Accessing each hour of the given day
            model.C1.add(expr = c_D[s,h] >= c_MinBid*zD[s,h]) # Constraint #1
            model.C2.add(expr = c_U[s,h] >= c_MinBid*zU[s,h]) # Constraint #2
            model.C3.add(expr = c_D[s,h] <= (Down_cap.iloc[s][h])*zD[s,h]) # Constraint #3
            model.C4.add(expr = c_U[s,h] <= (Up_cap.iloc[s][h])*zU[s,h]) # Constraint #4
            model.C5.add(expr = (c_B.iloc[s][h]) + c_D[s,h] <= P_max.iloc[h]['P_max']) # Constraint #5
            model.C6.add(expr = (c_B.iloc[s][h]) - c_U[s,h] >= P_min.iloc[s][h]) # Constraint #6          
    
# =============================================================================
#     # Defining the objective function:
#     income = sum(((c_D[s,h] * (p_D.iloc[s][h])) + (c_U[s,h] * (p_U.iloc[s][h])))* ind_W[s] for s in range_s for h in range_h)
#     model.obj = pyo.Objective(expr = income, sense=maximize)
# =============================================================================
    
    # Defining the objective function:
    income = sum(((c_D[s,h] * (p_D.iloc[s][h])) + (c_U[s,h] * (p_U.iloc[s][h]))) for s in range_s for h in range_h)
    model.obj = pyo.Objective(expr = income, sense=maximize)

    # Solving this linear optimization problem using the Solver: Gurobi:
    opt = SolverFactory('gurobi')
    opt.solve(model)

    model.pprint()
    
    cD_val = [pyo.value(c_D[s,h]) for s in range_s for h in range_h] # Print the
    # value of c_D for each hour in each scenario
    cU_val = [pyo.value(c_U[s,h]) for s in range_s for h in range_h] # Print the
    # value of c_U for each hour in each scenario
    zD_val = [pyo.value(zD[s,h]) for s in range_s for h in range_h] # Print the
    # value of zD for each hour in each scenario
    zU_val = [pyo.value(zU[s,h]) for s in range_s for h in range_h] # Print the
    # value of zU for each hour in each scenario
    obj_val = pyo.value(model.obj) # Print the value of the maximized income
    
    for s in range_s: # Accessing each scenario
        cD_hs = [] 
        cU_hs = [] 
        for h in range_h: # Accessing each hour of the given day
            cD_hs.append(pyo.value(c_D[s,h])) # Storing the value of c_D of 
            # the respective hour of the current scenario, in the list: 'cD_hs'
            
            cU_hs.append(pyo.value(c_U[s,h])) # Storing the value of c_U of 
            # the respective hour of the current scenario, in the list: 'cU_hs'
        
        cD_clus.append(cD_hs) # Storing the list containing the c_D values for 
        # the 24 hours of the respective scenario in another list
        cU_clus.append(cU_hs) # Storing the list containing the c_U values for 
        # the 24 hours of the respective scenario in another list
        
    return cD_val, cU_val, cD_clus, cU_clus, obj_val
        
        
 
        
        
    