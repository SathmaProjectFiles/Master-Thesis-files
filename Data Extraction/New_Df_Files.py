# -*- coding: utf-8 -*-
"""
Created on Thu May  2 10:32:53 2024

@author: Sathma Goonathilaka
"""
# ------------------------------------------------------------------------- #
# This file creates an excel file with timestamps of 5 minute resolution for 
# all days of a particular month that is inputted by the user. 
# ------------------------------------------------------------------------- #

import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np

dates = []
month = 12 # Input the number of the month you want to create the Excel file 
           # with dates.

month_31 = [1, 3, 5, 7, 8, 10, 12] # Months having 31 days.
month_30 = [4, 6, 9, 11] # Months having 30 days.


# Assigning the end day depending on the type of month:
if month in month_31:
    day_end = 32 # For months with 31 days, the end day is 31.
                 # (Here, 1 is added to 31 because, later in this code, the 'range' 
                 # function is used to create the range of days within that month).
    
elif month in month_30:
    day_end = 31  # For months with 30 days, the end day is 30.
    
else: 
    day_end = 29 # For month of February in year 2022, the end day is 28. 

days = range(1,day_end) # Range of days of a month
hours = range(0,24) # 24 hours of a day
min_s = [0,5,10,15,20,25,30,35,40,45,50,55] # Minutes with 5 minute resolution

# Creating the timestamps for the entire month, with 5 minute resolution:
for day in days:
    for hour in hours:
        for mints in min_s:
            date = dt.datetime(2022, month, day, hour, mints, 0)
            dates.append(date)
            
# Converting the dates to a dataframe:
df_new = pd.DataFrame(dates)
df_new.columns = ['Time']

df_new.dtypes
df_new['Time'] = df_new['Time'].dt.tz_localize(None)

# Creating the excel file containing the dataframe:
file_name = 'New_Df_Month - ' + str(month) + '.xlsx'
df_new.to_excel(file_name)

