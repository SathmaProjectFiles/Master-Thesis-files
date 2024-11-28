# -*- coding: utf-8 -*-
"""
Created on Tue May  7 00:32:49 2024

@author: Sathma Goonathilaka
"""

import os
import pandas as pd
import datetime as dt
from CreateFCRDwnPricesDf import CreateFCRDwnPricesDf
from CreateFCRUpPricesDf import CreateFCRUpPricesDf
from ConsumBaselineV1 import ConsumDataDf
from OptimizerV1 import Optimizer
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns  
from itertools import cycle, islice

cD_list = []
cU_list = []

Prices_FCRDwn = CreateFCRDwnPricesDf() # Load FCRD-Down prices (DKK/MW) for all
# hours from Monday to Sunday. 
Prices_FCRUp = CreateFCRUpPricesDf() # Load FCRD-Up prices (DKK/MW) for all
# hours from Monday to Sunday. 

# Load:
    #1. Baseline consumption (consum_Baseline), 
    #2. Minimum consumption (P_min_consum),
    #3. FCRD-Up capacity reserves (Up_consum),
    #4. FCRD-Down capacity reserves (Down_consum)   
# for all 24 hours for the 5 clusters from Monday to Sunday, and 
    #5. Maximum consumption (P_max) for all 24 hours which is constant for all
    # clusters and all days of the week.
consum_Baseline, P_min_consum, P_max, Up_consum, Down_consum = ConsumDataDf() 


c_MinBid = 0.1 # Minimum capacity (MW) to enter the FCRD bidding market.

for n in range(7): # To access n-th day of the week
    p_D = Prices_FCRDwn[n] # Extract FCRD-Down prices for the n-th day of the week
    p_D.columns =['Price - D'] # Change the column name in the dataframe: 'p_D'
    p_U = Prices_FCRUp[n] # Extract FCRD-Up prices for the n-th day of the week
    p_U.columns =['Price - U'] # Change the column name in the dataframe: 'p_U'
    
    c_B = consum_Baseline[n] # Extract baseline consumption values for the n-th day of the week
    #c_B.columns =['Consumption']
    P_min = P_min_consum[n] # Extract minimum consumption values for the n-th day of the week
    #P_min.columns =['P_min']
    P_max.columns = ['P_max'] # Change the column name in the dataframe: 'P_max'
    Up_cap = Up_consum[n] # Extract FCRD-Up reserves for the n-th day of the week
    #Up_cap.columns = ['Up reserve']
    Down_cap = Down_consum[n] # Extract FCRD-Down reserves for the n-th day of the week
    #Down_cap.columns = ['Down reserve']
    
    # Calling the 'Optimizer' function to obtain:
        #1. FCRD-Down bidding capacities of the 24 hours (cD_val),
        #2. FCRD-Up bidding capacities of the 24 hours (cU_val),
        #3. Total income generated from selling the Up and Down capacities together (obj_val)
    # on the n-th day of the week:
    cD_val, cU_val, obj_val = Optimizer(c_MinBid, c_B, p_D, p_U, Up_cap, Down_cap, P_max, P_min)
    
    cD_new = pd.DataFrame(cD_val) # Convert 'cD_val' to a dataframe
    cU_new = pd.DataFrame(cU_val) # Convert 'cU_val' to a dataframe
    
    cD_list.append(cD_new) # Storing the FCRD-Down bidding capacities of the n-th day
    # of the week in a list
    cU_list.append(cU_new) # Storing the FCRD-Up bidding capacities of the n-th day
    # of the week in a list

merged_cD = pd.concat(cD_list) # Have the FCRD-Down bidding capacities of the 24 hours 
# for the 7 days of the week in a single dataframe
merged_cU = pd.concat(cU_list) # Have the FCRD-Up bidding capacities of the 24 hours 
# for the 7 days of the week in a single dataframe

merged_pD = pd.concat(Prices_FCRDwn) # Have the FCRD-Down prices of the 24 hours 
# for the 7 days of the week in a single dataframe
merged_pU = pd.concat(Prices_FCRUp) # Have the FCRD-Up prices of the 24 hours 
# for the 7 days of the week in a single dataframe

merged_cD.columns = ['c_D values'] # Change the column name in the dataframe: 'merged_cD'
merged_cD = merged_cD.reset_index() # Resetting the indicies of the dataframe 
# to start from 0.

merged_cU.columns = ['c_U values'] # Change the column name in the dataframe: 'merged_cU'
merged_cU = merged_cU.reset_index() # Resetting the indicies of the dataframe 
# to start from 0. 

merged_pD.columns = ['p_D values']  # Change the column name in the dataframe: 'merged_pD'
merged_pD = merged_pD.reset_index() # Resetting the indicies of the dataframe 
# to start from 0.

merged_pU.columns = ['p_U values'] # Change the column name in the dataframe: 'merged_pU'
merged_pU = merged_pU.reset_index() # Resetting the indicies of the dataframe 
# to start from 0. 

# Creating a dataframe with a time column that has the dates for the first 
# week of August in year 2022 with hourly timestamps. The purpose of this is to have a dataframe with
# a 'Time' column that represents all hours of seven days of the week to extract 
# the 'hour', 'Day of week name', and 'Weekday-Weekend' attributes in order 
# to generate the box plots.
dates = []
#days = range(1,day_end)
months = range(8,9)
hours = range(0,24)
min_s = [0,5,10,15,20,25,30,35,40,45,50,55]

for month in months:   
    days = range(1, 8)
    for day in days:
        for hour in hours:
            date = dt.datetime(2022, month, day, hour, 0, 0)
            dates.append(date)
        

df_new = pd.DataFrame(dates)
df_new.columns = ['Time']

# Merging the dataframe with 'Time' column with the dataframes containing the 24 hour
# data of FCRD-Up and FCRD-Down bidding capacities, and FCRD-Up and FCRD-Down prices
# for all 7 days of the week:
df_new_hourly = pd.concat([df_new, merged_cD, merged_cU, merged_pD, merged_pU], axis=1)
#df_new_hourly = df_new_hourly.drop("index")

df_new_hourly["Hour"] =df_new_hourly['Time'].dt.hour # Extracting the hour of the day

# Extracting the day name from each date:
df_new_hourly['Day of week name'] = df_new_hourly['Time'].dt.day_name(locale = 'English') 

# Calculating the income generated by selling energy in the FCRD-Down market:
df_new_hourly["FCRD-Down Sales Income"] = df_new_hourly['c_D values']*df_new_hourly['p_D values']
# Calculating the income generated by selling energy in the FCRD-Up market:
df_new_hourly["FCRD-Up Sales Income"] = df_new_hourly['c_U values']*df_new_hourly['p_U values']

# ---------------------------- Plotting ----------------------------- #

# ------------------ Plotting the bidding capacities --------------------------- #
plt.figure(figsize=(8, 4), dpi=80)
sns.boxplot(x="Hour", y='c_D values', data=df_new_hourly, palette="Set1")
plt.xlabel("Hour of day")
plt.ylabel("Bidding capacity (MW)")
plt.title("FCRD-Down consumption bidding capacities - grouped hourly") 
#plt.savefig("box_plot - cDhourly")

plt.figure(figsize=(8, 4), dpi=80)
sns.boxplot(x="Hour", y='c_U values', data=df_new_hourly, palette="Set1")
plt.xlabel("Hour of day")
plt.ylabel("Bidding capacity (MW)")
plt.title("FCRD-Up consumption bidding capacities - grouped hourly") 
#plt.savefig("box_plot - cUhourly")

# --------------- Plotting the income created ------------------------------------ #
# ----------- On an hourly basis  -------------#
plt.figure(figsize=(8, 4), dpi=80)
sns.boxplot(x="Hour", y='FCRD-Down Sales Income', data=df_new_hourly, palette="Set1")
plt.xlabel("Hour of day")
plt.ylabel("Income (DKK/hour)")
plt.title("FCRD-Down sales income - grouped hourly") 
#plt.savefig("IncomeD_Hourly")

plt.figure(figsize=(8, 4), dpi=80)
sns.boxplot(x="Hour", y='FCRD-Up Sales Income', data=df_new_hourly, palette="Set1")
plt.xlabel("Hour of day")
plt.ylabel("Income (DKK/hour)")
plt.title("FCRD-Up sales income - grouped hourly") 
#plt.savefig("IncomeU_Hourly")

# ----------- On a weekly basis -------------#
plt.figure(figsize=(12,6), dpi=80)
sns.boxplot(x='Day of week name', y='FCRD-Down Sales Income', data=df_new_hourly, palette="Set1")
plt.xlabel("Day of week", fontsize=13)
#plt.xticks(rotation=90)
plt.ylabel("Income (DKK/hour)",fontsize=13)
plt.title("FCRD-Down sales income - grouped weekly", fontsize=15) 
#plt.savefig("IncomeD_Weekly")

plt.figure(figsize=(12,6), dpi=80)
sns.boxplot(x='Day of week name', y='FCRD-Up Sales Income', data=df_new_hourly, palette="Set1")
plt.xlabel("Day of week", fontsize=13)
#plt.xticks(rotation=90)
plt.ylabel("Income (DKK/hour)",fontsize=13)
plt.title("FCRD-Up sales income - grouped weekly", fontsize=15) 
#plt.savefig("IncomeU_Weekly")

# -------------------- Hourly plots for all 7 days of the week ----------- #

# ------- Bidding capacities --------------- #
plt.figure(figsize=(10, 6), dpi=80)
for day in range(7):
    plt.plot(cD_list[day])
plt.legend( ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], loc = "upper right")
plt.xlabel("Hour of day")
plt.ylabel("Bidding capacity (MW)")
plt.title("FCRD-Down consumption bidding capacities")  
#plt.savefig("FCRDwn_Bid")

plt.figure(figsize=(10, 6), dpi=80)
for day in range(7):
    plt.plot(cU_list[day])
plt.legend( ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], loc = "upper right")
plt.xlabel("Hour of day")
plt.ylabel("Bidding capacity (MW)")
plt.title("FCRD-Up consumption bidding capacities")  
#plt.savefig("FCRUp_Bid")

# ------------ Income generated ------------- #
merged_FCRDwnIncome = []
merged_FCRUpIncome = [] 
for day in range(7):
    incomeD = []
    incomeU = []
    for h in range(24):
        cD_day = cD_list[day]
        cD_day.columns = ['c_D values']
        priceD_day = Prices_FCRDwn[day]
        priceD_day.columns = ['Price - D']
        
        cU_day = cU_list[day]
        cU_day.columns = ['c_U values']
        priceU_day = Prices_FCRUp[day]
        priceU_day.columns = ['Price - U']
        
        cD_income = cD_day.iloc[h]['c_D values'] * priceD_day.iloc[h]['Price - D']
        incomeD.append(cD_income)
        
        cU_income = cU_day.iloc[h]['c_U values'] * priceU_day.iloc[h]['Price - U']
        incomeU.append(cU_income)
        
    merged_FCRDwnIncome.append(incomeD)
    merged_FCRUpIncome.append(incomeU)
     
plt.figure(figsize=(10, 6), dpi=80)
for day in range(7):
    plt.plot(merged_FCRDwnIncome[day])
plt.legend( ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], loc = "upper right")
plt.xlabel("Hour of day")
plt.ylabel("Income (DKK)")
plt.title("FCRD-Down sales income")
#plt.savefig("FCRDwn_Income")

plt.figure(figsize=(10, 6), dpi=80)
for day in range(7):
    plt.plot(merged_FCRUpIncome[day])
plt.legend( ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], loc = "upper right")
plt.xlabel("Hour of day")
plt.ylabel("Income (DKK)")
plt.title("FCRD-Up sales income")
#plt.savefig("FCRUp_Income")
  
# -------------- Capacity reserves ------------------ #
      
fig, axs = plt.subplots(5, ncols=1, figsize=(10, 12))
range_s = range(5)
range_h = range(24)
  
for s in range_s:
    #plt.figure(figsize=(10, 6), dpi=80)
    for day in range(7): 
        reserveD_day = Down_consum[day]
        reserveD_s = reserveD_day.iloc[s]
        axs[s].plot(reserveD_s)
    axs[s].legend( ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], loc = "upper right")
fig.suptitle("Available FCRD-Down Reserves", fontsize=18)
fig.supxlabel("Hour of day", fontsize=14)
fig.supylabel("Capacity reserves (MW)", fontsize=14)
#plt.savefig("FCRDwn_Res")

fig, axs = plt.subplots(5, ncols=1, figsize=(10, 12))
range_s = range(5)
range_h = range(24)
  
for s in range_s:
    #plt.figure(figsize=(10, 6), dpi=80)
    for day in range(7): 
        reserveU_day = Up_consum[day]
        reserveU_s = reserveU_day.iloc[s]
        axs[s].plot(reserveU_s)
    axs[s].legend( ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], loc = "upper right")
fig.suptitle("Available FCRD-Up Reserves", fontsize=18)
fig.supxlabel("Hour of day", fontsize=14)
fig.supylabel("Capacity reserves (MW)", fontsize=14)
#plt.savefig("FCRUp_Res")
