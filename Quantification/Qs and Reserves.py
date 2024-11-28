# -*- coding: utf-8 -*-
"""
Created on Mon May  6 20:22:28 2024

@author: Sathma Goonathilaka
"""
# ------------------------------------------------------------------------- #
# This code calculates the 10th, 50th and 90th percentiles of the consumption
# data, and thereby calculates the reserves available for FCRD-Up and 
# FCRD-Down services for each hour of each day of Year 2022, in a weekly frame.
# Additionally, it also generates box plots for this data regarding percentiles
# and reserves available, at hourly and weekly frames. 
# ------------------------------------------------------------------------- #

import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns  
from itertools import cycle, islice

Months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'] 
Days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

list_df = []

df_trains_new = []

df_consum_pivot = []
df_mean = []
df_Pmin = []
df_quantile_10 = []
df_quantile_50 = []
df_quantile_90 = []
df_FCRUp = []
df_FCRDown = []

df_train_pivot = []
df_mean_T = []

tot_merged_pivot = []
q90_series = []

# Appending the dataframes containing the total consumption data at every hour ... 
# ... of each day of each month in year 2022 into one list: 
for month in Months:
    data_path = os.path.join(os.getcwd(),'Data - Month' + month + '.xlsx')
    #data_path = os.path.join(os.getcwd(),'Test - Dec.xlsx')
    month_data = pd.read_excel(data_path)
    list_df.append(month_data) # Having a list containing 12 seperate dataframes...
    # ... of the hourly consumption data for all days of each month.

df_trains = pd.concat(list_df) # Concatenating the list to obtain a single ...
# ... dataframe containing the total consumption data of all 12 months of 2022. 
df_trains['Time'] = pd.to_datetime(df_trains['Time'], dayfirst=True) # This ...
# ... is to arrange the date in the dataframe in day/month/year format.
df_trains['Time'] = df_trains['Time'].dt.tz_localize('UTC')

# Extracting the 'Day of Year' of each day for Year 2022:
df_trains['Day of year'] = df_trains['Time'].dt.dayofyear

# =============================================================================
# #P_max_consum = df_trains['Total consumption (MWh)'].max()
# P_max_consum = 3.2281 # Maximum consumption value (Extracted from the 
# # 5minute data extraction code)
# max_Val_Arr = np.ones(24, dtype = int) * P_max_consum  # Returns an array having
# # a shape of 24 with each element's value being equal to 'P_max_consum'.
# df_Pmax = pd.DataFrame(max_Val_Arr) # Converts 'max_Val_Arr' into a dataframe.
# =============================================================================

for d in range(7): # To access each day of the week
    df_train_day = df_trains.loc[df_trains["day of week"] == d] # Filtering 
    # the dataframe 'df_trains' based on the condition that the day of week for
    # each day of 2022 being equal to d. 
    
    df_hourly = df_train_day.resample('H', on='Time').mean() # Resampling the 
    # the consumption data in the dataframe to hourly values.
    df_hourly = df_hourly.reset_index() # Resetting the indicies of the
    # dataframe to start from 0.
    
    
    # Creating a table with 'Total consumption values' of each 'Day of year' (row-wise)
    # at each hour (column-wise):
    df_pivot = pd.pivot_table(df_hourly, values='Total consumption (MWh)', index='Day of year', columns='hour')
    df_consum_pivot.append(df_pivot) # Appending 'df_pivot' into a list.
    merged_pivot = pd.concat(df_consum_pivot) # Converting that list to a dataframe.
    merged_pivot = merged_pivot.reset_index(drop=True) # Resetting the indicies
    # of the dataframe to start from 0.
   
    mean_consum = merged_pivot.mean() # Returns a series containing the mean value
    # of the consumption values at each hour in the dataframe: 'merged_pivot'
    df_m = mean_consum.to_frame() # Converting the series into a dataframe
    df_mean.append(df_m) # Appending 'df_m' into the list: 'df_mean'
    
    P_min_consum = 0.2 * mean_consum # Returns a series that has the minimum
    # consumption at each hour. This was introduced as an assumption considering
    # the train operator's point of view. 
    df_Pmin_consum = P_min_consum.to_frame() # Converting the series into a dataframe
    df_Pmin.append(df_Pmin_consum) # Appending 'df_Pmin_consum' into the list:'df_Pmin'
    
    quantile_10 = merged_pivot.quantile(.1, axis = 0) # Returns a series containing 
    # the 10th percentile of the consumption values at each hour
    df_q10 = quantile_10.to_frame() # Converting the series into a dataframe
    df_quantile_10.append(df_q10) # Storing that dataframe in a list
    
    quantile_50 = merged_pivot.quantile(.5, axis = 0) # Returns a series containing 
    # the 50th percentile of the consumption values at each hour
    df_q50 = quantile_50.to_frame()  # Converting the series into a dataframe
    df_quantile_50.append(df_q50) # Storing that dataframe in a list
    
    quantile_90 = merged_pivot.quantile(.9, axis = 0) # Returns a series containing 
    # the 90th percentile of the consumption values at each hour
    q90_series.append(quantile_90)
    df_q90 = quantile_90.to_frame() # Converting the series into a dataframe
    df_quantile_90.append(df_q90) # Storing that dataframe in a list
    

    # FCRD-Up capacity reserves
    c_Up = quantile_10 - P_min_consum # Calculating the capacity reserves at 
    # each hour for FCRD-Up services
    df_cUp = c_Up.to_frame() # Converting the series into a dataframe
    df_FCRUp.append(df_cUp) # Storing that dataframe in a list
    
    
    tot_merged_pivot.append(merged_pivot) # Storing the 'merged_pivot' dataframe
    # in the list 'tot_merged_pivot'
    df_consum_pivot = [] # Emptying the list: 'df_consum_pivot', so that it 
    # could store the data of the next day of the week
    
# FCRD-Down capacity reserves
df_tot_pivot = pd.concat(tot_merged_pivot) # Gives a data frame containing the
# total consumption of each hour for the 365 days of year 2022. 
P_max_consum = df_tot_pivot.max() # Outputs a series containing the maximum
# consumption value at each hour. 
df_Pmax = P_max_consum.to_frame() # Converts 'P_max_consum' into a data frame.


for d in range(7):
    c_Down = P_max_consum - q90_series[d] # Calculating the capacity reserves for 
    # FCRD-Down services
    df_cDown = c_Down.to_frame() # Converting the series into a dataframe
    df_FCRDown.append(df_cDown) # Storing that dataframe in a list


merged_q10 = pd.concat(df_quantile_10) # Concatenating the hourly 10th percentile 
# data for each day of the week
merged_q50 = pd.concat(df_quantile_50) # Concatenating the hourly 50th percentile 
# data for each day of the week
merged_q90 = pd.concat(df_quantile_90) # Concatenating the hourly 90th percentile 
# data for each day of the week
merged_FCRUp = pd.concat(df_FCRUp) # Concatenating the hourly data for FCRD-Up reserves
# for each day of the week
merged_FCRDwn = pd.concat(df_FCRDown) # Concatenating the hourly data for FCRD-Down reserves
# for each day of the week

# Re-naming the columns:
merged_q10.columns = ['Q10 values']
merged_q10 = merged_q10.reset_index()

merged_q50.columns = ['Q50 values']
merged_q50 = merged_q50.reset_index()

merged_q90.columns = ['Q90 values']
merged_q90 = merged_q90.reset_index()

merged_FCRUp.columns = ['FCRUp values']
merged_FCRUp = merged_FCRUp.reset_index()

merged_FCRDwn.columns = ['FCRDown values']
merged_FCRDwn = merged_FCRDwn.reset_index()

month_31 = [1, 3, 5, 7, 8, 10, 12] # Months having 31 days.
month_30 = [4, 6, 9, 11] # Months having 30 days.

# Creating a dataframe with a time column that has the dates for the first 
# week of August with hourly timestamps. The purpose of this is to have a dataframe with
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
# data of 10th, 50th and 90th percentiles, and FCRD-Up and FCRD-Down capacity reserves
# for all days of the week:
df_new_hourly = pd.concat([df_new, merged_q10, merged_q50, merged_q90, merged_FCRUp, merged_FCRDwn], axis=1)
#df_new_hourly = df_new_hourly.drop("index")

df_new_hourly["Hour"] =df_new_hourly['Time'].dt.hour # Extracting the hour of the day

# Extracting the day name from each date:
df_new_hourly['Day of week name'] = df_new_hourly['Time'].dt.day_name(locale = 'English') 

# Extracting weekdays and weekends from each date:
df_new_hourly['Weekday-Weekend'] = df_new_hourly["Time"].dt.weekday < 5
df_new_hourly['Weekday-Weekend'].replace(True, 'Weekday', inplace=True)
df_new_hourly['Weekday-Weekend'].replace(False, 'Weekend', inplace=True)

# ---------------------------- Plotting ----------------------------- #

# ------------ Plotting the percentiles -------------- #

plt.figure(figsize=(8, 4), dpi=80)
sns.boxplot(x="Hour", y='Q10 values', data=df_new_hourly, palette="Set1")
plt.xlabel("Hour of day")
plt.ylabel("Total consumption (MW)")
plt.title("10th percentile of consumption data - grouped hourly") 
#plt.savefig("box_plot - Q10hourly")

plt.figure(figsize=(12,6), dpi=80)
sns.boxplot(x='Day of week name', y='Q10 values', data=df_new_hourly, palette="Set1")
plt.xlabel("Day of week", fontsize=13)
#plt.xticks(rotation=90)
plt.ylabel("Total consumption (MW)",fontsize=13)
plt.title("10th percentile of consumption data - grouped weekly", fontsize=15) 
#plt.savefig("box_plot - Q10weekly")

plt.figure(figsize=(8, 4), dpi=80)
sns.boxplot(x="Hour", y='Q50 values', data=df_new_hourly, palette="Set1")
plt.xlabel("Hour of day")
plt.ylabel("Total consumption (MW)")
plt.title("50th percentile of consumption data - grouped hourly") 
#plt.savefig("box_plot - Q50hourly")

plt.figure(figsize=(12,6), dpi=80)
sns.boxplot(x='Day of week name', y='Q50 values', data=df_new_hourly, palette="Set1")
plt.xlabel("Day of week", fontsize=13)
#plt.xticks(rotation=90)
plt.ylabel("Total consumption (MW)",fontsize=13)
plt.title("50th percentile of consumption data - grouped weekly", fontsize=15) 
#plt.savefig("box_plot - Q50weekly")

plt.figure(figsize=(8, 4), dpi=80)
sns.boxplot(x="Hour", y='Q90 values', data=df_new_hourly, palette="Set1")
plt.xlabel("Hour of day")
plt.ylabel("Total consumption (MW)")
plt.title("90th percentile of consumption data - grouped hourly") 
#plt.savefig("box_plot - Q90hourly")

plt.figure(figsize=(12,6), dpi=80)
sns.boxplot(x='Day of week name', y='Q90 values', data=df_new_hourly, palette="Set1")
plt.xlabel("Day of week", fontsize=13)
#plt.xticks(rotation=90)
plt.ylabel("Total consumption (MW)",fontsize=13)
plt.title("90th percentile of consumption data - grouped weekly", fontsize=15) 
#plt.savefig("box_plot - Q90weekly")

# ----------------- Plotting the reserves -------------- #
# ------- FCRD-Up ----------------#
plt.figure(figsize=(8, 4), dpi=80)
sns.boxplot(x="Hour", y='FCRUp values', data=df_new_hourly, palette="Set1")
plt.xlabel("Hour of day")
plt.ylabel("Total consumption (MW)")
plt.title("Hourly FCRD-Up reserves of consumption data") 
#plt.savefig("box_plot - Uphourly")

plt.figure(figsize=(12,6), dpi=80)
sns.boxplot(x='Day of week name', y='FCRUp values', data=df_new_hourly, palette="Set1")
plt.xlabel("Day of week", fontsize=13)
#plt.xticks(rotation=90)
plt.ylabel("Total consumption (MW)",fontsize=13)
plt.title("Weekly FCRD-Up reserves of consumption data", fontsize=15) 
#plt.savefig("box_plot - Upweekly")

plt.figure(figsize=(10, 6), dpi=80)
sns.boxplot(x='Weekday-Weekend', y='FCRUp values', data=df_new_hourly, palette="Set1")
plt.xlabel("Weekday and Weekend")
#plt.xticks(rotation=90)
plt.ylabel("Total consumption (MW)")
plt.title("FCRD-Up reserves based on weekdays and weekends", fontsize=15) 
#plt.savefig("box_plot - Upwkd_wend")

# ------- FCRD-Down ----------------#
plt.figure(figsize=(8, 4), dpi=80)
sns.boxplot(x="Hour", y='FCRDown values', data=df_new_hourly, palette="Set1")
plt.xlabel("Hour of day")
plt.ylabel("Total consumption (MW)")
plt.title("Hourly FCRD-Down reserves of consumption data") 
#plt.savefig("box_plot - Dwnhourly")

plt.figure(figsize=(12,6), dpi=80)
sns.boxplot(x='Day of week name', y='FCRDown values', data=df_new_hourly, palette="Set1")
plt.xlabel("Day of week", fontsize=13)
#plt.xticks(rotation=90)
plt.ylabel("Total consumption (MW)",fontsize=13)
plt.title("Weekly FCRD-Down reserves of consumption data", fontsize=15) 
#plt.savefig("box_plot - Dwnweekly")

plt.figure(figsize=(10, 6), dpi=80)
sns.boxplot(x='Weekday-Weekend', y='FCRDown values', data=df_new_hourly, palette="Set1")
plt.xlabel("Weekday and Weekend")
#plt.xticks(rotation=90)
plt.ylabel("Total consumption (MW)")
plt.title("FCRD-Down reserves based on weekdays and weekends", fontsize=15) 
#plt.savefig("box_plot - Dwnwkd_wend")

# -------------------- Hourly plots for all 7 days of the week ----------- #

# ------- Capacity reserves --------------- #
plt.figure(figsize=(10, 6), dpi=80)
for d in range(7):
    plt.plot(df_FCRDown[d])
plt.legend( ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], loc = "upper right")
plt.xlabel("Hour of day")
plt.ylabel("Capacity reserve (MW)")
plt.title("Available FCRD-Down Reserves")  
#plt.savefig("FCRDwn_Res_Weekly")

plt.figure(figsize=(10, 6), dpi=80)
for d in range(7):
    plt.plot(df_FCRUp[d])
plt.legend( ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], loc = "upper right")
plt.xlabel("Hour of day")
plt.ylabel("Capacity reserve (MW)")
plt.title("Available FCRD-Up Reserves")  
#plt.savefig("FCRUp_Res_Weekly")