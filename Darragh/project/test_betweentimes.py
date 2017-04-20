import json
import datetime
import time
import pandas as pd
import numpy as np

def make_chart():
    with open('test_json.json') as data_file:
        data = json.load(data_file)
        newData = []
        for i in range(0, len(data['chdata'])):
            newData.append(data['chdata'][i])
        df = pd.DataFrame(data=newData)
        df['avgVacency'] = round(df[2] / (df[3] + df[2]), 2)
         
        # convert string time to datetime for easy manipulation
        end = datetime.time(0,0,0)
        start = datetime.time(6,0,0)
        df[1] = pd.to_datetime(df[1]).dt.time
        
        # create variables for time intervals.
        interval0s = datetime.time(6,0,0)
        interval0e = datetime.time(8,59,59)
        interval1s = datetime.time(9,0,0)
        interval1e = datetime.time(11,59,59)
        interval2s = datetime.time(12,0,0)
        interval2e = datetime.time(14,59,59)
        interval3s = datetime.time(15,0,0)
        interval3e = datetime.time(17,59,59)
        interval4s = datetime.time(18,0,0)
        interval4e = datetime.time(20,59,59)
        interval5s = datetime.time(21,0,0)
        interval5e = datetime.time(23,59,59)
        
        df['interval'] = 0

        for i, row in df.iterrows():
            if df[1][i] > end and df[1][i] < start:
                df.drop(i, inplace=True)
            elif df[1][i] > interval0s and df[1][i] < interval0e:
                df.loc[i, 'interval'] = 1
            elif df[1][i] > interval1s and df[1][i] < interval1e:
                df.loc[i, 'interval'] = 2
            elif df[1][i] > interval2s and df[1][i] < interval2e:
                df.loc[i, 'interval'] = 3
            elif df[1][i] > interval3s and df[1][i] < interval3e:
                df.loc[i, 'interval'] = 4
            elif df[1][i] > interval4s and df[1][i] < interval4e:
                df.loc[i, 'interval'] = 5
            elif df[1][i] > interval5s and df[1][i] < interval5e:
                df.loc[i, 'interval'] = 6
                
        return df
    
print(make_chart())