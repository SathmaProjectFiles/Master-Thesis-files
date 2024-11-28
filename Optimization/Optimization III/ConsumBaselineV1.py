# -*- coding: utf-8 -*-
"""
Created on Thu May  9 18:46:13 2024

@author: Sathma Goonathilaka
"""
# ------------------------------------------------------------------------- #
# This function analyses both the consumption data, and the FCRD-Down and FCRD-Up
# price data by seperating the consumption data profiles as well as the price 
# data profiles of a certain day of the week throughout the year 2022 
# (eg. all Mondays of year 2022) into 5 clusters, where each cluster is treated 
# as a scenario. Here, KMeans is used as the clustering algorithm. 
# It also plots the 5 consumption scenarios for each day of the week.

# Further, the function also returns:
    #1. mean consumption of all 24 hours for the 5 clusters of each day 
    #... for the 7 days of the week (merged_cent_list).
    #2. minimum consumption of all 24 hours for the 5 clusters of each day 
    #... for the 7 days of the week (merged_Pmin_list).
    #3. maximum consumption for the 24 hours of a day which is constant throughout
    #... the whole week (df_Pmax).
    #4. FCRD-Up capacity reserves of all 24 hours for the 5 clusters of each day 
    #... for the 7 days of the week (merged_capUP_list).
    #5. FCRD-Down capacity reserves of all 24 hours for the 5 clusters of each day 
    #... for the 7 days of the week (merged_capDWN_list).
    #6. Weighting factors of the 5 clusters of each day for the 7 days of the week
    #... (merged_weighted_ind).
    #7. mean FCRD-Down prices of all 24 hours for the 5 clusters of each day 
    #... for the 7 days of the week (df_meanPrice_week_D).
    #8. mean FCRD-Up prices of all 24 hours for the 5 clusters of each day 
    #... for the 7 days of the week (df_meanPrice_week_U).
# ------------------------------------------------------------------------- #

import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from FCRDownPricesDf import CreateFCRDwnPricesDf
from FCRUpPricesDf import CreateFCRUpPricesDf

def ConsumDataDf():

    list_df = []
    
    cent_list = []
    merged_cent_list = []
    
    list_index = []
    list_index_week = []
    merged_index_list = []
    merged_weighted_ind = []
    
    Pmin_list = []
    merged_Pmin_list = []
    
    Q10_list = []
    merged_Q10_list = []
    
    Q90_list = []
    merged_Q90_list = []
    
    capUP_list = []
    merged_capUP_list = []
    
    capDWN_list = []
    merged_capDWN_list = []
    
    df_consum_pivot = []
    loop_count = 0
    
    df_meanPrice_week_D = []
    df_meanPrice_week_U = []
    
    Months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'] 
    Days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
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
    
    # An array which contains the maximum consumption values at each hour, and
    # this is the same for all 7 days of the week. These values were obtained
    # from the code that was used to compute the capacity reserves. 
    max_Val_Arr = np.array([1.49703, 1.44988, 1.29967, 0.796633, 0.787783, 1.19633, 
                            1.86894, 2.65881, 2.66224, 2.60899, 2.35978, 2.21267, 2.26315, 
                            2.32463, 2.32203, 2.56189, 2.5359, 2.80095, 2.60407, 2.35997, 
                            2.04686, 2.0117, 1.92298, 1.80646]) 
    df_Pmax = pd.DataFrame(max_Val_Arr) # Converting the array into a dataframe.
    
    # The 'plot_clusters' function which takes the inputs:
        #1. The dataframe containing the consumption data profiles of a certain
        #... day of the week throughout the year 2022 (eg. all Mondays of year 2022),
        #... which needs to be clustered (df_pivot).
        #2. The number of clusters (n).
    def plot_clusters(df_pivot, n):
        """Cluster df of 24h profiles and plot the result"""
        
        # Applying KMeans as the clustering algorithm:
        kmeans = KMeans(n_clusters=n, max_iter = 1000)
        kmeans.fit(df_pivot)
    
        idx = kmeans.labels_ # Obtaining the label of each 24-hour consumption  
        #... data profile which is based on the index of the cluster that it was assigned to
        cl  = kmeans.cluster_centers_ # Gives the centroids of the clusters 
    
        # Creating n number of subplots where one subplot represents one cluster:
        fig, axs = plt.subplots(nrows=n, ncols=1, figsize=(8, 14))    
        fig.suptitle("Weekly Cluster of Train Consumption for " + Days[loop_count],
                  fontsize = 10)
        
        len_index = [] # Emptying the list: 'len_index', so that it 
        # could store the data of the next day of the week
    
        for i, ax in enumerate(axs.flat): # Accessing each cluster
        #for i in range(n):
            
            list_index_clus = [] # Emptying the list: 'list_index_clus', so that it 
            #... could store the indicies corresponding to the consumption profiles
            #... whose membership belongs to cluster i
            
            # Plot the cluster i:
            ax.plot(df_pivot.loc[idx==i].T, c = colors_hex[i], linewidth = 1) 
            
            clus = df_pivot.loc[idx==i].T # Gives a dataframe containing all the
            #... 24-hour consumption data profiles whose label/membership 
            #... belongs to cluster i. 
            # Here, the 24 consumption values of each profile is arranged in the  
            #... row-wise direction (row 0 to 23), while the index of each column 
            #... of the dataframe represents the index of the corresponding 
            #... consumption data profile whose label/membership belongs to cluster i.
            
            ax.set_xlabel("Hour of day") # Set the label of the plot's x-axis
            ax.set_ylabel("Consumption (MW)") # Set the label of the plot's y-axis
            ax.set_title("Cluster " + str(i+1)) # Set the title of each subplot
            
            # Plot the centeroid of cluster i:
            ax.plot(cl[i], c = "black", linewidth = 4)
            
            cent_val_i = (cl[i]) # Gives an array of 24 values that composes 
            #... the centeroid of cluster i
            cent_val = cent_val_i.tolist() # Convert the array into a list
            cent_list.append(cent_val) # Storing that list inside another list
            
            # Accessing the index of each column of the dataframe: 'clus', and
            #... storing that respective index in the list named 'list_index_clus':
            for col in clus.columns:
                list_index_clus.append(col)
                
            list_index.append(list_index_clus) # Storing that list of indicies 
            #... belonging to cluster i in another list
            len_index.append(len(list_index_clus)) # Obtain the length of the 
            #... list named 'list_index_clus' which gives the number of 24-hour 
            #... consumption data profiles whose label/membership belongs to cluster i.
            #... This number is then stored in the list named 'len_index'
            
            Pmin_consum = 0.2 * cent_val_i # Returns an array that has the minimum
            #... consumption at each hour. This was introduced as an assumption considering
            #... the train operator's point of view.
            Pmin_consum_list = Pmin_consum.tolist() # Convert the array into a list
            Pmin_list.append(Pmin_consum_list) # Storing that list inside another list
            
            quantile_10 = clus.quantile(.1, axis = 1) # Returns an array containing 
            #... the 10th percentile of each row in the dataframe: 'clus'
            quantile10_list = quantile_10.tolist() # Convert the array into a list
            Q10_list.append(quantile10_list) # Storing that list inside another list
            
            quantile_90 = clus.quantile(.9, axis = 1) # Returns an array containing 
            #... the 90th percentile of each row in the dataframe: 'clus'
            quantile90_list = quantile_90.tolist() # Convert the array into a list
            Q90_list.append(quantile90_list) # Storing that list inside another list
            
            c_Up = quantile_10 - Pmin_consum # Calculating the capacity reserves for 
            #... FCRD-Up services
            cUP_list = c_Up.tolist() # Convert the array into a list
            capUP_list.append(cUP_list) # Storing that list inside another list
            
            c_Down = max_Val_Arr - quantile_90 # Calculating the capacity reserves for 
            #... FCRD-Down services
            cDown_list = c_Down.tolist() # Convert the array into a list
            capDWN_list.append(cDown_list) # Storing that list inside another list
             
        merged_cent = np.array(cent_list) # Convert the nested list called 'cent_list'
        #... into an array
        df_merged_cent = pd.DataFrame(merged_cent) # Convert the array into a dataframe
        
        merged_Pmin = np.array(Pmin_list) # Convert the nested list called 'Pmin_list'
        #... into an array
        df_merged_Pmin = pd.DataFrame(merged_Pmin) # Convert the array into a dataframe
    
        merged_Q10 = np.array(Q10_list) # Convert the nested list called 'Q10_list'
        #... into an array
        df_merged_Q10 = pd.DataFrame(merged_Q10) # Convert the array into a dataframe
        
        merged_Q90 = np.array(Q90_list) # Convert the nested list called 'Q90_list'
        #... into an array
        df_merged_Q90 = pd.DataFrame(merged_Q90) # Convert the array into a dataframe
        
        merged_cUP = np.array(capUP_list)  # Convert the nested list called 'capUP_list'
        #... into an array
        df_merged_cUP = pd.DataFrame(merged_cUP) # Convert the array into a dataframe
        
        merged_cDown = np.array(capDWN_list) # Convert the nested list called 'capDWN_list'
        #... into an array
        df_merged_cDown = pd.DataFrame(merged_cDown) # Convert the array into a dataframe
        
        fig.tight_layout()
        return df_merged_cent, df_merged_Pmin, df_merged_Q10, df_merged_Q90, df_merged_cUP, df_merged_cDown, list_index, len_index    

    # RGB color codes for the colors that are used for plotting clusters:
    colors_rgb = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (128, 0, 0),    # Maroon
    (0, 128, 0),    # Dark green
    (0, 0, 128),    # Navy
    (128, 128, 0),  # Olive
    (128, 0, 128),  # Purple
    (0, 128, 128),  # Teal
    (255, 128, 0),  # Orange
    (255, 0, 128),  # Hot pink
    (128, 255, 0),  # Lime
    (0, 255, 128),  # Spring green
    (128, 0, 255),  # Indigo
    (0, 128, 255),  # Dodger blue
    (255, 128, 128),# Light coral
    (128, 255, 128),# Pale green
    ]
    
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
        
        # Convert the RGB tuples to hex color codes for plotting clusters:
        colors_hex = [f'#{r:02x}{g:02x}{b:02x}' for r, g, b in colors_rgb]
        
        # Calling the 'plot_clusters' function to obtain dataframes containing:
            #1. mean consumption (center of each cluster) of all 24 hours for the 5 clusters (df_merged_cent)
            #2. minimum consumption of all 24 hours for the 5 clusters (df_merged_Pmin)
            #3. 10th quantile of the consumption data of all 24 hours for the 5 clusters (df_merged_Q10)
            #4. 90th quantile of the consumption data of all 24 hours for the 5 clusters (df_merged_Q90)
            #5. FCRD-Up capacity reserves of all 24 hours for the 5 clusters (df_merged_cUP)
            #6. FCRD-Down capacity reserves of all 24 hours for the 5 clusters (df_merged_cDown)
            #7. A list of 5 lists where each list contains the corresponding indicies of the 
            #... 24-hour consumption profiles that belongs to each cluster (list_index)
            #8. A list of 5 elements where each element represents the length of each list
            #... in the nested list named 'list_index' (len_index)
        # for the d-th day of the week:
        df_merged_cent, df_merged_Pmin, df_merged_Q10, df_merged_Q90, df_merged_cUP, df_merged_cDown, list_index, len_index = plot_clusters(merged_pivot, 5)
        
        # Save the subplots of the 5 clusters when the day of the week == 'loop_count' (==d):
        #plt.savefig("Cluster - " + Days[loop_count])
    
        sum_index = sum(len_index) # Summing the 5 elements in the list: 'len_index',
        #... to obtain the total number of consumption profiles belonging to the 
        #... the respective day.
        new_indList = [ i/sum_index  for i in len_index] # Dividing each element in
        #... 'len_index' with the sum of all its elements to obtain the weighting factors
        #... of each element which represents each cluster.
        
        merged_cent_list.append(df_merged_cent) # Storing 'df_merged_cent' of d-th day in a list
        merged_weighted_ind.append(new_indList) # Storing 'new_indList' of d-th day in a list
        merged_index_list.append(list_index) # Storing 'list_index' of d-th day in a list
        merged_Pmin_list.append(df_merged_Pmin) # Storing 'df_merged_Pmin' of d-th day in a list
        merged_Q10_list.append(df_merged_Q10) # Storing 'df_merged_Q10' of d-th day in a list
        merged_Q90_list.append(df_merged_Q90) # Storing 'df_merged_Q90' of d-th day in a list
        merged_capUP_list.append(df_merged_cUP) # Storing 'df_merged_cUP' of d-th day in a list
        merged_capDWN_list.append(df_merged_cDown) # Storing 'df_merged_cDown' of d-th day in a list
    
        loop_count+=1 # Incrementing loop_count to move to the next day
        
        df_consum_pivot = [] # Emptying the list: 'df_consum_pivot', so that it 
        # could store the data of the next day of the week
        cent_list = [] # Emptying the list: 'cent_list', so that it 
        # could store the data of the next day of the week
        list_index = [] # Emptying the list: 'list_index', so that it 
        # could store the data of the next day of the week
        len_index = [] # Emptying the list: 'len_index', so that it 
        # could store the data of the next day of the week
        Pmin_list = [] # Emptying the list: 'Pmin_list', so that it 
        # could store the data of the next day of the week
        Q10_list = [] # Emptying the list: 'Q10_list', so that it 
        # could store the data of the next day of the week
        Q90_list = [] # Emptying the list: 'Q90_list', so that it 
        # could store the data of the next day of the week
        capUP_list = [] # Emptying the list: 'capUP_list', so that it 
        # could store the data of the next day of the week
        capDWN_list = [] # Emptying the list: 'capDWN_list', so that it 
        # could store the data of the next day of the week
        
    FCRDwn_prices_week = CreateFCRDwnPricesDf() # Load FCRD-Down prices (DKK/MW) for all
    # hours from Monday to Sunday. 
    FCRUp_prices_week = CreateFCRUpPricesDf() # Load FCRD-Up prices (DKK/MW) for all
    # hours from Monday to Sunday. 
    
    for day in range(7): # To access each day of the week
        list_mean_D = [] # Emptying the list: 'list_mean_D', so that it 
        #... could store the mean FCRD-Down price profiles for all 24 hours for the 5 clusters
        #... of the respective day.
        list_mean_U = [] # Emptying the list: 'list_mean_U', so that it 
        #... could store the mean FCRD-Up price profiles for all 24 hours for the 5 clusters
        #... of the respective day.
        
        price_day_D = FCRDwn_prices_week[day] # Accessing the FCRD-Down prices for
        #... the day of the week  that is equal to the day represented by the value of the 
        #... variable called 'day'
        price_day_U = FCRUp_prices_week[day] # Accessing the FCRD-Up prices for
        #... the day of the week that is equal to the day represented by the value of the 
        #... variable called 'day'
        
        for cluster in range(5): # To access each cluster
        
            cluster_set_list_D = [] # Emptying the list: 'cluster_set_list_D', so that it 
            #... could store the 24-hour FCRD-Down price profiles corresponding to the
            #... respective day and the respective cluster.
            cluster_set_list_U = [] # Emptying the list: 'cluster_set_list_U', so that it 
            #... could store the 24-hour FCRD-Up price profiles corresponding to the
            #... respective day and the respective cluster.
            
            clus_index = merged_index_list[day][cluster] # For the respective day of the week, 
            #... extracting the list containing the corresponding indicies of the
            #... 24-hour consumption profiles that belongs to the cluster that is 
            #... represented by the value of the variable named 'cluster'.
            
            for i in clus_index: # To access each index of the consumption profiles 
            #... that belongs to the respective cluster
                price_i_D = price_day_D.loc[[i]] # Filtering the 24-hour FCRD-Down
                #... price profile that has the index i, from the FCRD-Down 
                #... price profiles belonging to that respective cluster.
                cluster_set_list_D.append(price_i_D) # Storing that dataframe containing the 
                #... 24-hour price profile in the list named 'cluster_set_list_D'.
                
                price_i_U = price_day_U.loc[[i]] # Filtering the 24-hour FCRD-Up
                #... price profile that has the index i, from the FCRD-Up
                #... price profiles belonging to that respective cluster.
                cluster_set_list_U.append(price_i_U) # Storing that dataframe containing the 
                #... 24-hour price profile in the list named 'cluster_set_list_U'.
                
            cluster_set_D = pd.concat(cluster_set_list_D) # Concatenate all the dataframes
            #... that are present in 'cluster_set_list_D' to obtain a single dataframe.
            mean_clus_price_D = cluster_set_D.mean() # Calculating the mean across each
            #... column in the dataframe to obtain a series containing the mean FCRD-Down 
            #... price at each hour for the respective day and respective cluster. 
            list_m_D = mean_clus_price_D.to_list() # Convert that series into a list.
            list_mean_D.append(list_m_D) # Storing that list in another list.
            
            cluster_set_U = pd.concat(cluster_set_list_U) # Concatenate all the dataframes
            #... that are present in 'cluster_set_list_U' to obtain a single dataframe.
            mean_clus_price_U = cluster_set_U.mean() # Calculating the mean across each
            #... column in the dataframe to obtain a series containing the mean FCRD-Up 
            #... price at each hour for the respective day and respective cluster. 
            list_m_U = mean_clus_price_U.to_list() # Convert that series into a list.
            list_mean_U.append(list_m_U) # Storing that list in another list.
            
        merged_mean_D = np.array(list_mean_D) # Convert the nested list named 'list_mean_D'
        #... into an array.
        df_merged_mean_D = pd.DataFrame(merged_mean_D) # Convert the array into a dataframe
        df_meanPrice_week_D.append(df_merged_mean_D) # Storing that dataframe in a list
        
        merged_mean_U = np.array(list_mean_U) # Convert the nested list named 'list_mean_U'
        #... into an array.
        df_merged_mean_U = pd.DataFrame(merged_mean_U) # Convert the array into a dataframe
        df_meanPrice_week_U.append(df_merged_mean_U) # Storing that dataframe in a list
            
    return merged_cent_list, merged_Pmin_list, df_Pmax, merged_capUP_list, merged_capDWN_list, merged_weighted_ind, df_meanPrice_week_D, df_meanPrice_week_U

#merged_cent_list, merged_Pmin_list, df_Pmax, merged_capUP_list, merged_capDWN_list, merged_weighted_ind, df_meanPrice_week_D, df_meanPrice_week_U = ConsumDataDf()
