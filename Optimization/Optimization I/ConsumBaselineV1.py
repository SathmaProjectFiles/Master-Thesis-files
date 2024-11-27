# -*- coding: utf-8 -*-
"""
Created on Mon May  6 22:34:32 2024

@author: Sathma Goonathilaka
"""
# ------------------------------------------------------------------------- #
# This function calculates and returns the baseline consumption, minimum consumption,
# maximum consumption, and the reserves available for FCRD-Up and 
# FCRD-Down services for each hour of each day of Year 2022, in a weekly frame.
# ------------------------------------------------------------------------- #

import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns  
from itertools import cycle, islice

def CreateConsumBaselineDf():
        
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
#     #P_max_consum = df_trains['Total consumption (MWh)'].max()
#     P_max_consum = 3.2281 # Maximum consumption value (Extracted from the 
#     # 5minute data extraction code)
#     max_Val_Arr = np.ones(24, dtype = int) * P_max_consum # Returns an array having
#     # a shape of 24 with each element's value being equal to 'P_max_consum'.
#     df_Pmax = pd.DataFrame(max_Val_Arr) # Converts 'max_Val_Arr' into a dataframe.
# =============================================================================
    
    for d in range(7): # To access each day of the week
        df_train_day = df_trains.loc[df_trains["day of week"] == d]  # Filtering 
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
        
        P_min_consum = 0.2 * mean_consum  # Returns a series that has the minimum
        # consumption at each hour. This was introduced as an assumption considering
        # the train operator's point of view.
        df_Pmin_consum = P_min_consum.to_frame() # Converting the series into a dataframe
        df_Pmin.append(df_Pmin_consum)  # Appending 'df_Pmin_consum' into the list:'df_Pmin'
        
        quantile_10 = merged_pivot.quantile(.1, axis = 0)  # Returns a series containing 
        # the 10th percentile of each data column in the dataframe: 'merged_pivot'
        df_q10 = quantile_10.to_frame()  # Converting the series into a dataframe
        df_quantile_10.append(df_q10) # Storing that dataframe in a list
        
        quantile_50 = merged_pivot.quantile(.5, axis = 0) # Returns a series containing 
        # the 50th percentile of each data column in the dataframe: 'merged_pivot'
        df_q50 = quantile_50.to_frame()  # Converting the series into a dataframe
        df_quantile_50.append(df_q50) # Storing that dataframe in a list
        
        quantile_90 = merged_pivot.quantile(.9, axis = 0) # Returns a series containing 
        # the 90th percentile of each data column in the dataframe: 'merged_pivot'
        q90_series.append(quantile_90)
        df_q90 = quantile_90.to_frame() # Converting the series into a dataframe
        df_quantile_90.append(df_q90) # Storing that dataframe in a list
        
        # FCRD-Up capacity reserves
        c_Up = quantile_10 - P_min_consum # Calculating the capacity reserves for 
        # FCRD-Up services
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
    
    return df_mean, df_Pmin, df_Pmax, df_FCRUp, df_FCRDown

#df_mean, df_Pmin, df_Pmax, df_FCRUp, df_FCRDown = CreateConsumBaselineDf()