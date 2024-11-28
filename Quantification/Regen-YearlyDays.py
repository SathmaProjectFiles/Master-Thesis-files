# -*- coding: utf-8 -*-
"""
Created on Sun May  5 02:17:28 2024

@author: Sathma Goonathilaka
"""
import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns  

# ------------------------------------------------------------------------- #
# This code creates box plots to represent the total regeneration of trains in 
# Year 2022, in hourly, monthly and weekly frames. 
# Additionally, it also represents the number of active trains avaiable on 
# hourly and weekly frames.
# ------------------------------------------------------------------------- #

Months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'] 
Days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Appending the dataframes containing the total regenerative data at every hour ... 
# ... of each day of each month in year 2022 into one list: 

list_df = []

df_trains_new = []

for month in Months:
    data_path = os.path.join(os.getcwd(),'RegenData - Month' + month + '.xlsx')
    #data_path = os.path.join(os.getcwd(),'Test - Dec.xlsx')
    month_data = pd.read_excel(data_path)
    list_df.append(month_data)

df_trains = pd.concat(list_df) # Concatanating the list to obtain a single ...
# ... dataframe containing the total regenerative data of all 12 months of 2022.
df_trains['Time'] = pd.to_datetime(df_trains['Time'], dayfirst=True) # This ...
# ... is to arrange the date in the dataframe in day/month/year format.
df_trains['Time'] = df_trains['Time'].dt.tz_localize('UTC')

# Extracting the day name from each date:
df_trains['Day of week name'] = df_trains['Time'].dt.day_name(locale = 'English') 
# Extracting the month name from each date:
df_trains['Month of year name'] = df_trains['Time'].dt.month_name(locale = 'English') 

# Extracting weekdays and weekends from each date:
df_trains['Weekday-Weekend'] = df_trains["Time"].dt.weekday < 5
df_trains['Weekday-Weekend'].replace(True, 'Weekday', inplace=True)
df_trains['Weekday-Weekend'].replace(False, 'Weekend', inplace=True)

# ---------- Plotting the total regeneration--------------------------------- #
    
plt.figure(figsize=(8, 4), dpi=80)
sns.boxplot(x="hour", y="Total regeneration (MWh)", data=df_trains, palette="Set1")
plt.xlabel("Hour of day")
plt.ylabel("Total regeneration (MW)")
plt.title("Hourly regeneration data analysis - Year 2022") 
#plt.savefig("Regenbox_plot - hourly")

plt.figure(figsize=(12,10), dpi=80)
sns.boxplot(x='Month of year name', y="Total regeneration (MWh)", data=df_trains, palette="Set1")
plt.xlabel("Month of year", fontsize=13)
plt.xticks(rotation=60)
plt.ylabel("Total regeneration (MW)",fontsize=13)
plt.title("Monthly regeneration data analysis - Year 2022", fontsize=15) 
#plt.savefig("Regenbox_plot - monthly")

plt.figure(figsize=(12,6), dpi=80)
sns.boxplot(x='Day of week name', y="Total regeneration (MWh)", data=df_trains, palette="Set1")
plt.xlabel("Day of week", fontsize=13)
#plt.xticks(rotation=90)
plt.ylabel("Total regeneration (MW)",fontsize=13)
plt.title("Weekly regeneration data analysis - Year 2022", fontsize=15) 
#plt.savefig("Regenbox_plot - weekly")

# =============================================================================
# plt.figure(figsize=(8, 4), dpi=80)
# sns.boxplot(x="day", y="Total consumption (MWh)", data=df_trains, palette="Set1")
# plt.xlabel("Day of month")
# plt.ylabel("Total consumption (MW)")
# plt.title("Daily consumption data analysis - Year 2022") 
# #plt.savefig("box_plot - daily")
# 
# =============================================================================

plt.figure(figsize=(10, 6), dpi=80)
sns.boxplot(x='Weekday-Weekend', y="Total regeneration (MWh)", data=df_trains, palette="Set1")
plt.xlabel("Weekday and Weekend")
#plt.xticks(rotation=90)
plt.ylabel("Total regeneration (MW)")
plt.title("Regeneration data analysis based on weekdays and weekends - Year 2022", fontsize=15) 
#plt.savefig("Regenbox_plot - wkd_wend")
    
# ----------------- Plotting the number of active trains available ------------ #
plt.figure(figsize=(8, 4), dpi=80)
sns.boxplot(x="hour", y="Number of trains available", data=df_trains, palette="Set1")
plt.xlabel("Hour of day")
plt.ylabel("Number of active trains available")
plt.title("Hourly active train analysis - Year 2022") 
#plt.savefig("Regenbox_plot - Trainshourly")

plt.figure(figsize=(12,6), dpi=80)
sns.boxplot(x='Day of week name', y="Number of trains available", data=df_trains, palette="Set1")
plt.xlabel("Day of week", fontsize=13)
#plt.xticks(rotation=90)
plt.ylabel("Number of active trains available",fontsize=13)
plt.title("Weekly active train analysis - Year 2022", fontsize=15) 
#plt.savefig("Regenbox_plot - Trainsweekly")