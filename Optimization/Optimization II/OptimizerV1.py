# -*- coding: utf-8 -*-
"""
Created on Tue May  7 00:25:31 2024

@author: Sathma Goonathilaka
"""
# ------------------------------------------------------------------------- #
# This function solves a linear optimization problem under the given 
# objective function, and the 6 constraints that are subjected to 
# 5 different scenarios. 
# It then returns the FCRD-Down bidding capacities(c_D), FCRD-Up bidding capacities(c_U) 
# for 24 hours of a given day, and the maximized income(obj) for the given day.

# The inputs to the function are:
    #1. minimum bidding capacity requirement to enter the FCRD market (c_MinBid)
    #2. baseline consumption values for the 24 hours for that given day 
    #...under 5 different scenarios (c_B)
    #3. FCRD-Down marginal prices for the 24 hours for that given day (p_D)
    #4. FCRD-Up marginal prices for the 24 hours for that given day (p_U)
    #5. FCRD-Up capacity reserves available for the 24 hours for that given day 
    #...under 5 different scenarios (Up_cap)
    #6. FCRD-Down capacity reserves available for the 24 hours for that given day 
    #...under 5 different scenarios (Down_cap)
    #7. Maximum consumption values for the 24 hours (P_max)
    #8. Minimum consumption values for the 24 hours for that given day under 5 
    #...different scenarios (P_min)
# ------------------------------------------------------------------------- #

import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory

def Optimizer(c_MinBid, c_B, p_D, p_U, Up_cap, Down_cap, P_max, P_min):
    model = pyo.ConcreteModel() # Creates an optimization model
    
    range_s = range(5) # Number of scenarios per day
    range_h = range(24) # Number of hours per day                                            
    model.c_D = pyo.Var(range_h, bounds = (0,None)) # Decision variable. 
    # Creates 24 positions for c_D of a certain day. c_D can only have non-negative reals. 
    model.c_U = pyo.Var(range_h, bounds = (0,None)) # Decision variable.
    # Creates 24 positions for c_U of a certain day. c_U can only have non-negative reals.
    
    model.zD = pyo.Var(range_h, within = Binary) # Creates 24 positions for the 
    # binary variable zD
    model.zU = pyo.Var(range_h, within = Binary) # Creates 24 positions for the 
    # binary variable zU
    
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
            model.C1.add(expr = c_D[h] >= c_MinBid*zD[h]) # Constraint #1
            model.C2.add(expr = c_U[h] >= c_MinBid*zU[h]) # Constraint #2
            model.C3.add(expr = c_D[h] <= (Down_cap.iloc[s][h])*zD[h]) # Constraint #3
            model.C4.add(expr = c_U[h] <= (Up_cap.iloc[s][h])*zU[h]) # Constraint #4
            model.C5.add(expr = (c_B.iloc[s][h]) + c_D[h] <= P_max.iloc[h]['P_max']) # Constraint #5
            model.C6.add(expr = (c_B.iloc[s][h]) - c_U[h] >= P_min.iloc[s][h]) # Constraint #6
            
    # Defining the objective function:
    income = sum((c_D[h] * (p_D.iloc[h]['Price - D'])) + (c_U[h] * (p_U.iloc[h]['Price - U'])) for h in range_h)
    model.obj = pyo.Objective(expr = income, sense=maximize)
    
    # Solving this linear optimization problem using the Solver: Gurobi:
    opt = SolverFactory('gurobi')
    opt.solve(model)
    
    model.pprint()
    
    cD_val = [pyo.value(c_D[h]) for h in range_h] # Print the value of c_D for each hour
    cU_val = [pyo.value(c_U[h]) for h in range_h] # Print the value of c_U for each hour
    obj_val = pyo.value(model.obj) # Print the value of the maximized income
        
    return cD_val, cU_val, obj_val
        
