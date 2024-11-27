# -*- coding: utf-8 -*-
"""
Created on Thu May  9 20:03:39 2024

@author: Sathma Goonathilaka
"""

import os
import pandas as pd
import datetime as dt
from ConsumBaselineV1 import ConsumDataDf
from OptimizerV1 import Optimizer
import matplotlib.pyplot as plt
import itertools
import seaborn as sns  

cD_week = []
cU_week = []

cD_list = []
cU_list = []

cD_hour_week = []
cU_hour_week = []

iD_hour_week = []
iU_hour_week = []

# Load:
    #1. Baseline consumption (consum_Baseline), 
    #2. Minimum consumption (P_min_consum),
    #3. FCRD-Up capacity reserves (Up_consum),
    #4. FCRD-Down capacity reserves (Down_consum),
    #5. FCRD-Down prices (Prices_FCRDwn),
    #6. FCRD-Up prices (Prices_FCRUp)
# for all 24 hours for the 5 clusters from Monday to Sunday, 
    #7. Maximum consumption (P_max) for all 24 hours which is constant for all
    # clusters and for all days of the week,
    #8. Weighting factors (Weight_ind) of the 5 clusters of each day 
    # from Monday to Sunday.
consum_Baseline, P_min_consum, P_max, Up_consum, Down_consum, Weight_ind, Prices_FCRDwn, Prices_FCRUp = ConsumDataDf() # Load weekly baseline consumption

c_MinBid = 0.1 # Minimum capacity (MW) to enter the FCRD bidding market.

for n in range(7): # To access n-th day of the week
    
    p_D = Prices_FCRDwn[n]  # Extract FCRD-Down prices for the n-th day of the week
    #p_D.columns =['Price - D']
    p_U = Prices_FCRUp[n] # Extract FCRD-Up prices for the n-th day of the week
    #p_U.columns =['Price - U']
    
    c_B = consum_Baseline[n] # Extract baseline consumption values for the n-th day of the week
    #c_B.columns =['Consumption']
    P_min = P_min_consum[n] # Extract minimum consumption values for the n-th day of the week
    #P_min.columns =['P_min']
    P_max.columns = ['P_max'] # Change the column name in the dataframe: 'P_max'
    Up_cap = Up_consum[n] # Extract FCRD-Up reserves for the n-th day of the week
    #Up_cap.columns = ['Up reserve']
    Down_cap = Down_consum[n] # Extract FCRD-Down reserves for the n-th day of the week
    #Down_cap.columns = ['Down reserve']
    ind_W = Weight_ind[n] # Extract the weighting factors of the clusters for the n-th day of the week
    
    # Calling the 'Optimizer' function to obtain:
        #1. FCRD-Down bidding capacities of the 24 hours for all 5 scenarios (cD_cap),
        #2. FCRD-Up bidding capacities of the 24 hours for all 5 scenarios (cU_cap),
        #3. a nested list (cD_day) containing 5 lists where each list contains 
        # the c_D values of the 24 hours of each scenario, 
        #4. a nested list (cU_day) containing 5 lists where each list contains 
        # the c_U values of the 24 hours of each scenario,
        #5. total income generated from selling the Up and Down capacities together (obj_val)
    # on the n-th day of the week:
    cD_cap, cU_cap, cD_day, cU_day, obj_day = Optimizer(c_MinBid, c_B, p_D, p_U, Up_cap, Down_cap, P_max, P_min, ind_W)
    
    cD_hour_list = [] # An empty list to store the hourly FCRD-Down bidding capacities  
    # after accounting for the weighting factors of each scenario of the n-th day of the
    # week
    iD_hour_list = [] # An empty list to store the hourly income made via FCRD-Down   
    # capacity sales after accounting for the weighting factors of each scenario 
    # of the n-th day of the week
    
    for h in range(24): # To access each hour
        cD_hour = 0
        iD_hour = 0
        for s in range(5): # To access each scenario
            cD_hour += cD_day[s][h] * ind_W[s] # FCRD-Down bidding capacities at hour h
            # after accounting for the weighting factors of each scenario of day n
            iD_hour += cD_day[s][h] * ind_W[s] * p_D.iloc[s][h] # Income at hour h
            # from FCRD-Down capacity sales with the weighting factors accounted for 
            # each scenario of day n
        cD_hour_list.append(cD_hour) 
        iD_hour_list.append(iD_hour)
    
    cD_hour_new = pd.DataFrame(cD_hour_list) # Convert 'cD_hour_list' to a data frame
    cD_hour_week.append(cD_hour_new) # Hourly FCRD-Down bidding capacities for 
    # all days of the week, with the weighting factors accounted 
    
    iD_hour_new = pd.DataFrame(iD_hour_list) # Convert 'iD_hour_list' to a data frame
    iD_hour_week.append(iD_hour_new) # Hourly income from FCRD-Down capacity sales for 
    # all days of the week, with the weighting factors accounted
    
    
    cU_hour_list = [] # An empty list to store the hourly FCRD-Up bidding capacities  
    # after accounting for the weighting factors of each scenario of the n-th day of the
    # week
    iU_hour_list = [] # An empty list to store the hourly income made via FCRD-Up   
    # capacity sales after accounting for the weighting factors of each scenario 
    # of the n-th day of the week
    for h in range(24): # To access each hour
        cU_hour = 0
        iU_hour = 0
        for s in range(5): # To access each scenario
            cU_hour += cU_day[s][h] * ind_W[s] # FCRD-Up bidding capacities at hour h
            # after accounting for the weighting factors of each scenario of day n
            iU_hour += cU_day[s][h] * ind_W[s] * p_U.iloc[s][h] # Income at hour h
            # from FCRD-Up capacity sales with the weighting factors accounted for 
            # each scenario of day n 
        cU_hour_list.append(cU_hour)
        iU_hour_list.append(iU_hour)
    
    cU_hour_new = pd.DataFrame(cU_hour_list) # Convert 'cU_hour_list' to a data frame
    cU_hour_week.append(cU_hour_new) # Hourly FCRD-Up bidding capacities for 
    # all days of the week, with the weighting factors accounted 
    
    iU_hour_new = pd.DataFrame(iU_hour_list) # Convert 'iU_hour_list' to a data frame
    iU_hour_week.append(iU_hour_new) # Hourly income from FCRD-Up capacity sales for 
    # all days of the week, with the weighting factors accounted


# ---------------------------- Plotting ----------------------------- #

# -------------------- Hourly plots for all 7 days of the week ----------- #

# ------- Bidding capacities --------------- #
plt.figure(figsize=(10, 6), dpi=80)
for day in range(7):
    plt.plot(cD_hour_week[day])
plt.legend( ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], loc = "upper right")
plt.xlabel("Hour of day")
plt.ylabel("Bidding capacity (MW)")
plt.title("FCRD-Down consumption bidding capacities")  
#plt.savefig("FCRDwn_Bid")

plt.figure(figsize=(10, 6), dpi=80)
for day in range(7):
    plt.plot(cU_hour_week[day])
plt.legend( ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], loc = "upper right")
plt.xlabel("Hour of day")
plt.ylabel("Bidding capacity (MW)")
plt.title("FCRD-Up consumption bidding capacities")  
#plt.savefig("FCRUp_Bid")

# ------------ Income generated ------------- #
    
plt.figure(figsize=(10, 6), dpi=80)
for day in range(7):
    plt.plot(iD_hour_week[day])
plt.legend( ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], loc = "upper right")
plt.xlabel("Hour of day")
plt.ylabel("Income (DKK)")
plt.title("FCRD-Down sales income")
#plt.savefig("FCRDwn_Income")

plt.figure(figsize=(10, 6), dpi=80)
for day in range(7):
    plt.plot(iU_hour_week[day])
plt.legend( ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], loc = "upper right")
plt.xlabel("Hour of day")
plt.ylabel("Income (DKK)")
plt.title("FCRD-Up sales income")
#plt.savefig("FCRUp_Income")
        