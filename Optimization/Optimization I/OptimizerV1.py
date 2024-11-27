# -*- coding: utf-8 -*-
"""
Created on Mon May  6 22:40:43 2024

@author: Sathma Goonathilaka
"""
# ------------------------------------------------------------------------- #
# This function solves a linear optimization problem under the given 
# objective function and the 6 constraints. It then returns the FCRD-Down bidding 
# capacities(c_D), FCRD-Up bidding capacities(c_U) for the 24 hours of a given day, and 
# the maximized income(obj) for the given day.

# The inputs to the function are:
    #1. minimum bidding capacity requirement to enter the FCRD market (c_MinBid)
    #2. baseline consumption values for the 24 hours for that given day (c_B)
    #3. FCRD-Down marginal prices for the 24 hours for that given day (p_D)
    #4. FCRD-Up marginal prices for the 24 hours for that given day (p_U)
    #5. FCRD-Up capacity reserves available for the 24 hours for that given day (Up_cap)
    #6. FCRD-Down capacity reserves available for the 24 hours for that given day (Down_cap)
    #7. Maximum consumption values for the 24 hours (P_max)
    #8. Minimum consumption values for the 24 hours for that given day (P_min)
# ------------------------------------------------------------------------- #

import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory

def Optimizer(c_MinBid, c_B, p_D, p_U, Up_cap, Down_cap, P_max, P_min):
    model = pyo.ConcreteModel() # Creates an optimization model
    
    range_i = range(24) # Number of hours per day                                            
    model.c_D = pyo.Var(range_i, bounds = (0,None)) # Decision variable. 
    # Creates 24 positions for c_D of a certain day. c_D can only have non-negative reals. 
    model.c_U = pyo.Var(range_i, bounds = (0,None)) # Decision variable.
    # Creates 24 positions for c_U of a certain day. c_U can only have non-negative reals.
    
    model.zD = pyo.Var(range_i, within = Binary) # Creates 24 positions for the 
    # binary variable zD
    model.zU = pyo.Var(range_i, within = Binary) # Creates 24 positions for the 
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
    
    for i in range_i: # Accessing each hour of the given day
        model.C1.add(expr = c_D[i] >= c_MinBid*zD[i]) # Constraint #1
        model.C2.add(expr = c_U[i] >= c_MinBid*zU[i]) # Constraint #2
        model.C3.add(expr = c_D[i] <= (Down_cap.iloc[i]['Down reserve'])*zD[i]) # Constraint #3
        model.C4.add(expr = c_U[i] <= (Up_cap.iloc[i]['Up reserve'])*zU[i]) # Constraint #4
        model.C5.add(expr = (c_B.iloc[i]['Consumption']) + c_D[i] <= P_max.iloc[i]['P_max']) # Constraint #5
        model.C6.add(expr = (c_B.iloc[i]['Consumption']) - c_U[i] >= (P_min.iloc[i]['P_min'])) # Constraint #6        
    
    # Defining the objective function:
    income = sum((c_D[i] * (p_D.iloc[i]['Price - D'])) + (c_U[i] * (p_U.iloc[i]['Price - U'])) for i in range_i)
    model.obj = pyo.Objective(expr = income, sense=maximize)

    # Solving this linear optimization problem using the Solver: Gurobi:
    opt = SolverFactory('gurobi')
    opt.solve(model)

    model.pprint()
    
    cD_val = [pyo.value(c_D[i]) for i in range_i] # Print the value of c_D for each hour
    cU_val = [pyo.value(c_U[i]) for i in range_i] # Print the value of c_U for each hour
    zD_val = [pyo.value(zD[i]) for i in range_i] # Print the value of zD for each hour
    zU_val = [pyo.value(zU[i]) for i in range_i] # Print the value of zU for each hour
    obj_val = pyo.value(model.obj) # Print the value of the maximized income
        
    return cD_val, cU_val, obj_val
        
        
 
        
        
    