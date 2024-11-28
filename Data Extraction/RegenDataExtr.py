# -*- coding: utf-8 -*-
"""
Created on Sun May  5 01:26:15 2024

@author: Sathma Goonathilaka
"""
# ------------------------------------------------------------------------- #
# This code calculates the total regeneration of all active trains within each 
# hourly timestamp for an entire month, and converts that to an excel file.
# ------------------------------------------------------------------------- #

import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

# -------------------- Inputs -------------------------------------- #
# Input the number corresponding to the month you want to open the Excel file  
# containing the dates:
month = 12
# Input the data path by changing the file name of the month you want to 
# extract the data from:
data_path = os.path.join(os.getcwd(),'2022-12 - 2023-01_energy-raw-data-report_DSB.xlsx')
#data_path = os.path.join(os.getcwd(),'Test - Dec.xlsx')
df_trains = pd.read_excel(data_path)

# --------------------- Outputs ----------------------------------- #
month_31 = [1, 3, 5, 7, 8, 10, 12] # Months having 31 days.
month_30 = [4, 6, 9, 11] # Months having 30 days.

# Reading the excel file that contains only 5 minute timestamps for the inputted month, 
# which was created through 'New_Df_Files.py'.
data_path_new = os.path.join(os.getcwd(),'New_Df_Month - ' + str(month) + '.xlsx')
df_new = pd.read_excel(data_path_new)

regen_l = [] # List to store the total regeneration at each 5-minute timestamp.
num_trains = [] # List to store the number of active trains available at each hour.
hourly_regen = [] # List to store what active trains are available at each hour.

# convert the date column to datetime format
df_trains['Time'] = pd.to_datetime(df_trains['Time'], dayfirst=True) # This ...
# ... is to arrange the date in the dataframe in day/month/year format.

df_trains['Time'] = df_trains['Time'].dt.tz_localize('UTC')

# Assigning the end day depending on the type of month:
if month in month_31:
    day_end = 32 # For months with 31 days, the end day is 31.
                 # (Here, 1 is added to 31 because, later in this code, the 'range' 
                 # function is used to create the range of days within that month).
    
elif month in month_30:
    day_end = 31 # For months with 30 days, the end day is 30.
    
else: 
    day_end = 29 # For month of February in year 2022, the end day is 28.

days = range(1,day_end) # Range of days of a month
hours = range(0,24) # 24 hours of a day
min_s = [0,5,10,15,20,25,30,35,40,45,50,55] # Minutes with 5 minute resolution

for day in days:
    for hour in hours:
        for mints in min_s:
            
            # Start-time to extract the 5-minute timestamp:
            t_s = pd.Timestamp(dt.datetime(2022, month, day, hour, mints, 0), tz='UTC')
            # End-time to extract the 5-minute timestamp:
            t_e = pd.Timestamp(dt.datetime(2022, month, day, hour, mints+4, 59), tz='UTC')
            
            # Extracting the 5-minute timestamp specified by t_s and t_e, from the dataframe:
            df_train_set1 = df_trains.loc[(df_trains['Time']>=t_s) & (df_trains['Time']<=t_e)]
            df_train_set1 =df_train_set1.reset_index(drop=True)
            
            # Count the entries that has nonzero regeneration
            n = np.count_nonzero(df_train_set1["Generation (MWh)"])
            #num_trains.append(n)
            
            # Add the regeneration of all active trains within that corresponding timestamp...
            # ... to obtain the total regeneration at that timestamp
            x = df_train_set1["Generation (MWh)"].sum()
            regen_l.append(x) # Inserting the total regeneration at each timestamp ...
            # ... to the list: regen_l
            
            if mints == 0: # At a timestamp where there is a 'start ... 
            # ... of a new hour' (minutes is equal to 00):
                
                # Filtering the df_train_set1 dataframe to obtain a dataframe with ...
                # ... nonzero regeneration.
                train_set2 = df_train_set1.loc[df_train_set1["Generation (MWh)"] > 0] 
                all_consum_Points = train_set2.ConsumptionPoint.unique() # Filter all the  ...
                # ... unique consump. points at this particular time stamp. This is an array.
    
                consumP_list = all_consum_Points.tolist() # Convert "all_consum_Points" ...
                # ... to a list.
                
            else: # At a timestamp of the 'same hour but not the start of that hour'... 
            # ... (minutes is not equal to 00):
                
                # Filtering the df_train_set1 dataframe to obtain a dataframe with ...
                # ... nonzero regeneration.
                train_set3 = df_train_set1.loc[df_train_set1["Generation (MWh)"] > 0] 
                other_CP = train_set3.ConsumptionPoint.unique() # Filter all the  ...
                # ... unique consump. points at this particular time stamp. This is an array.
                
                other_CP_list = other_CP.tolist() # Convert "other_CP" ...
                # ... to a list.
                
                
                # If there is a consumption point in other_CP_list that is not present in ...
                # ... consumP_list, add it to consumP_list. This is to count a ...
                # ... consumption point (train) that is active within the corresponding hour, only once.
                for i in other_CP_list:
                    if i not in consumP_list:
                        consumP_list.append(i)
        
        trains = len(consumP_list) # Counting the total number of active trains within ...
        # ... the corresponding hour.
        num_trains.append(trains) # This contains the number of active trains available ...
        # .... at each hour for all the days of the month. 
        hourly_regen.append(consumP_list) # This contains all the active trains at each hour ...
        # .... for all the days of the month.

df_new['Total regeneration (MWh)'] = regen_l # Insert the column with total regeneration ...
# ... at each 5 minute timestamp for every day for the inputted month.
P_max_regen = df_new['Total regeneration (MWh)'].max()
df_new['Time'] = pd.to_datetime(df_new['Time'], dayfirst=True)
df_new_hourly = df_new.resample('H', on='Time').mean() # Get the total ...
# ... regeneration at each hour. 
df_new_hourly = df_new_hourly.reset_index() # Resetting the index of the dataframe.
df_new_hourly['Number of trains available'] = num_trains # Insert the ...
# ... active number of trains available at each hourly timestamp for ...
# ... every day.
df_new_hourly['Time'] = pd.to_datetime(df_new_hourly['Time'], dayfirst=True)
df_new_hourly["day"] = df_new_hourly["Time"].dt.day # Extracting the day ....
# ... of the month.
df_new_hourly["hour"] =df_new_hourly['Time'].dt.hour # Extracting the hour ...
# ... of the day.
df_new_hourly["day of week"] = df_new_hourly["Time"].dt.dayofweek  # Extracting the day ...
# ... of the week with Monday=0, Sunday=6.

# Creating the excel file containing the total regeneration of all active trains ...
# ... within each hour for an entire month:

#df_new_hourly.dtypes
#df_new_hourly['Time'] = df_new['Time'].dt.tz_localize(None)

file_name = 'RegenData - Month' + str(month) + '.xlsx'
df_new_hourly.to_excel(file_name)
#    return df_new