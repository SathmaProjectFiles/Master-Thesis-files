# -*- coding: utf-8 -*-
"""
Created on Mon May  6 22:30:32 2024

@author: Sathma Goonathilaka
"""
# ------------------------------------------------------------------------- #
# This function calculates the FCRD-Up prices for 1 MW of capacity for each hour 
# of each day of Year 2022, in a weekly frame. 
# ------------------------------------------------------------------------- #

import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

def CreateFCRUpPricesDf():

    # -------------------- Loading data -------------------------------------- #
    data_path = os.path.join(os.getcwd(),'FCRDUpPrices.xlsx') # Join various
    # ... path components
    df_prices = pd.read_excel(data_path) # Read the data path.
    
    # Convert the date column to datetime format
    df_prices['Time'] = pd.to_datetime(df_prices['Time'], dayfirst=True) # This ...
    # ... is to arrange the date in the dataframe in day/month/year format.
    
    # Adding time-zone information
    df_prices['Time'] = df_prices['Time'].dt.tz_localize('UTC')
    
    # Convert the unit of FCRD-Up prices from EUR/MW to DKK/MW:
    df_prices['FCRD-Up Price Total (DKK/MW)'] = df_prices['Price Total (EUR/MW)'] * 7.46
    
    df_prices["day of week"] = df_prices["Time"].dt.dayofweek # Extracting the day ...
    # ... of the week with Monday=0, Sunday=6.
    df_prices["hour"] =df_prices['Time'].dt.hour # Extracting the hour ...
    # ... of the day.
    
    df_price_pivot = []
    merged_pivot_week = []
    df_meanPrice_week = []
    df_mean = []
       
    for d in range(7): # To access each day of the week
        df_price_day = df_prices.loc[df_prices["day of week"] == d] # Filtering 
        # the dataframe 'df_prices' based on the condition that the day of week for
        # each day of 2022 being equal to d. 
        df_price_day = df_price_day.reset_index() # Resetting the indicies of the
        # dataframe to start from 0.
        
        df_new = df_price_day[["Time", 'FCRD-Up Price Total (DKK/MW)']] # Create ...
        # ... a new dataframe with columns: "Time" and "FCRD-Up Price Total (DKK/MW)".
        
        df_new["day"] = df_new["Time"].dt.day # Extracting the day of the month...
        # ... and adding it as a column to the dataframe: 'df_new'.
        df_new["hour"] = df_new['Time'].dt.hour # Extracting the hour of the day...
        # ... and adding it as a column to the dataframe: 'df_new'.
        df_new['Day of year'] = df_new['Time'].dt.dayofyear # Extracting the day... 
        # ... of the year and adding it as a column to the dataframe: 'df_new'.
        
        # Creating a table with 'FCRD-Up prices' of each 'Day of year' (row-wise)
        # at each hour (column-wise):
        df_pivot = pd.pivot_table(df_new, values='FCRD-Up Price Total (DKK/MW)', index='Day of year', columns='hour')
        df_pivot = df_pivot.reset_index(drop=True) # Resetting the indicies
        # of the dataframe to start from 0.
        df_pivot = df_pivot.fillna(0) # Fill the NaN values in 'df_pivot' with 0.
        
        df_price_pivot.append(df_pivot) # Appending 'df_pivot' into a list: 'df_price_pivot'.
        merged_pivot_day = pd.concat(df_price_pivot) # Converting that list to a dataframe.
        merged_pivot_day = merged_pivot_day.reset_index(drop=True) # Resetting the indicies
        # of the dataframe to start from 0.
        
        #merged_pivot_week.append(merged_pivot_day)
        
        mean_price = merged_pivot_day.mean() # Calculating the mean of FCRD-Up prices...
        # ... of all days(=d) of the year of each hour. 
        df_m = mean_price.to_frame() # Converting the series into a dataframe.
        df_mean.append(df_m) # Appending 'df_m' into the list: 'df_mean'.
        
        
        df_price_pivot = [] # Emptying the list: 'df_price_pivot', so that it 
        # could store the data of the next day of the week
        
    return df_mean
    

