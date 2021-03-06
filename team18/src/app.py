from flask import Flask, render_template, url_for, request, session, flash, g, jsonify
import functools
import numpy as np
import pandas as pd
import datetime
import time
import sys
from flask_mysqldb import MySQLdb
import dbconnect

#create app object
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

# Create variable from todays date to pass into the sql query when clicked. 
todaysDay = datetime.date.today().strftime("%A") #
ChartDay = todaysDay[:3] #check ordering here

# SQL query to display current weather
sql1 = """SELECT DISTINCT
    weather.timeStamp,
    weather.weatherID,
    weather.temp,
    weather.descp,
    weather.icons
FROM
    weather
ORDER BY uniqueID DESC
LIMIT 1;"""
  
# SQL query  to display daily chart information by station id(passed from javascript ajax)
# chart day information is passed from chartDay variable above into Like parameter.
sql2 = """SELECT DISTINCT
  static.num,
  DynamicTest.last_update,
  DynamicTest.available_bikes,
  DynamicTest.available_bike_stands
FROM
  static,
  DynamicTest
WHERE
  static.num = DynamicTest.num
  and static.num = '{stationChart}'
  and DynamicTest.last_update LIKE '{}%';
  """

# SQL query for weekly chart information by station id.
sql3 = """SELECT DISTINCT
  static.num,
  DynamicTest.last_update,
  DynamicTest.available_bikes,
  DynamicTest.available_bike_stands
FROM
  static,
  DynamicTest
WHERE
  static.num = DynamicTest.num
  and static.num = '{stationChart}'; 
  """
  
# SQL query for search function. 
sql4 = """SELECT DISTINCT
    static.num,
    static.addr,
    DynamicTest.last_update,
    DynamicTest.status,
    static.lat,
    static.longti,
    DynamicTest.available_bikes,
    DynamicTest.available_bike_stands,
    DynamicTest.bike_stands,
    DynamicTest.banking
FROM
    static,
    DynamicTest
WHERE
    static.num = DynamicTest.num and
    static.addr= '{addr}'
ORDER BY uniqueID DESC
LIMIT 1;
    """

# Flask function to display weather. Passes SQL to list and returns output on webpage in json format. 
@app.route('/weather')
def get_weather():
    g.db = dbconnect.connection()
    c = g.db.cursor()
    cur = c.execute(sql1) 
    rows = c.fetchall()
    weather = []
    for eachRow in rows:
        weather.append(eachRow)
    c.close()
    g.db.close()
    return jsonify(weather=weather)

# Flask function that takes station clicked via ajax request returns output on webpage in json format. 
@app.route('/selectedStation', methods=['GET', 'POST'])
def selectedStation():
    if request.method == "POST":
        global stationData
        stationData = 0
        stationData = request.json['data']
        return jsonify(stationData=stationData)
    return jsonify(stationData=stationData)

# Flask function to send
@app.route('/chart')
def make_chart():
    g.db = dbconnect.connection()
    c = g.db.cursor()
    cur = c.execute(sql2.format(ChartDay, stationChart=stationData))
    chdata = [x for x in c.fetchall()]
    df = pd.DataFrame(data=chdata)
    df['avgVacency'] = round(df[2], 0)  # / (df[3] + df[2]), 2)
    # convert string time to datetime for easy manipulation
    # Find max value for the y axis on the graph. Otherwise it just takes average.
    dfMax = df.iloc[df[3].max()]
    vAxis = dfMax.ix[3] + dfMax.ix[2]
    maxB = int(vAxis)

    end = datetime.time(0, 0, 0)
    start = datetime.time(6, 0, 0)
    df[1] = pd.to_datetime(df[1]).dt.time
    # create variables for time intervals.
    interval0s = datetime.time(6, 0, 0)
    interval0e = datetime.time(8, 59, 59)
    interval1s = datetime.time(9, 0, 0)
    interval1e = datetime.time(11, 59, 59)
    interval2s = datetime.time(12, 0, 0)
    interval2e = datetime.time(14, 59, 59)
    interval3s = datetime.time(15, 0, 0)
    interval3e = datetime.time(17, 59, 59)
    interval4s = datetime.time(18, 0, 0)
    interval4e = datetime.time(20, 59, 59)
    interval5s = datetime.time(21, 0, 0)
    interval5e = datetime.time(23, 59, 59)
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

    dfOne = df.loc[df['interval'] == 1]
    df2 = df.loc[df['interval'] == 2]
    df3 = df.loc[df['interval'] == 3]
    df4 = df.loc[df['interval'] == 4]
    df5 = df.loc[df['interval'] == 5]
    df6 = df.loc[df['interval'] == 6]  # is this getting all values?
    dfTest = df[df['interval'] == 1]

    mean1 = np.mean(dfOne["avgVacency"]) # .round
    mean2 = np.mean(df2["avgVacency"])
    mean3 = np.mean(df3["avgVacency"])
    mean4 = np.mean(df4["avgVacency"])
    mean5 = np.mean(df5["avgVacency"])
    mean6 = np.mean(df6["avgVacency"])

    columns = ['Time', 'avgVac', 'TotalBikes']
    dfFinal = pd.DataFrame(
        [["06:00 - 09:00", mean1, maxB], ["09:00 - 12:00", mean2, maxB], ["12:00 - 15:00", mean3, maxB], ["15:00 - 18:00", mean4, maxB],
         ["18:00 - 21:00", mean5, maxB], ["21:00 - 00:00", mean6, maxB]], columns=columns)
    df1 = dfFinal.to_json(orient='records')  # json string
    c.close()
    g.db.close()
    return df1


@app.route('/chartWeek')
def make_chartWeekly():
    g.db = dbconnect.connection()
    c = g.db.cursor()
    cur = c.execute(sql3.format(stationChart=stationData))
    chdata = [x for x in c.fetchall()]
    df = pd.DataFrame(data=chdata)
    df['avgVacency'] = round(df[2], 0)  # / (df[3] + df[2]), 2)
    # convert string time to datetime for easy manipulation

    # Find max value for the y axis on the graph. Otherwise it just takes average.
    dfMax = df.iloc[df[3].max()]
    vAxis = dfMax.ix[3] + dfMax.ix[2]
    maxB = int(vAxis)

    end = datetime.time(0, 0, 0)
    start = datetime.time(6, 0, 0)
    df['Time'] = pd.to_datetime(df[1]).dt.time
    df['Day'] = pd.to_datetime(df[1]).dt.weekday_name
    
    # Create the time intervals from 6am to 12am. 

    interval0s = datetime.time(6, 0, 0)
    interval0e = datetime.time(8, 59, 59)
    interval1s = datetime.time(9, 0, 0)
    interval1e = datetime.time(11, 59, 59)
    interval2s = datetime.time(12, 0, 0)
    interval2e = datetime.time(14, 59, 59)
    interval3s = datetime.time(15, 0, 0)
    interval3e = datetime.time(17, 59, 59)
    interval4s = datetime.time(18, 0, 0)
    interval4e = datetime.time(20, 59, 59)
    interval5s = datetime.time(21, 0, 0)
    interval5e = datetime.time(23, 59, 59)

    df['interval'] = 0

    for i, row in df.iterrows():
        if df['Time'][i] > end and df['Time'][i] < start:
            df.drop(i, inplace=True)
        elif df['Time'][i] > interval0s and df['Time'][i] < interval0e:
            df.loc[i, 'interval'] = 1
        elif df['Time'][i] > interval1s and df['Time'][i] < interval1e:
            df.loc[i, 'interval'] = 2
        elif df['Time'][i] > interval2s and df['Time'][i] < interval2e:
            df.loc[i, 'interval'] = 3
        elif df['Time'][i] > interval3s and df['Time'][i] < interval3e:
            df.loc[i, 'interval'] = 4
        elif df['Time'][i] > interval4s and df['Time'][i] < interval4e:
            df.loc[i, 'interval'] = 5
        elif df['Time'][i] > interval5s and df['Time'][i] < interval5e:
            df.loc[i, 'interval'] = 6
    
    # create 7 dataframes for each day, split by the average number of bikes per interval. 

    monInt1 = df[(df['Day'] == 'Monday') & (df['interval'] == 1)].mean()
    monInt2 = df[(df['Day'] == 'Monday') & (df['interval'] == 2)].mean()
    monInt3 = df[(df['Day'] == 'Monday') & (df['interval'] == 3)].mean()
    monInt4 = df[(df['Day'] == 'Monday') & (df['interval'] == 4)].mean()
    monInt5 = df[(df['Day'] == 'Monday') & (df['interval'] == 5)].mean()
    monInt6 = df[(df['Day'] == 'Monday') & (df['interval'] == 6)].mean()

    tueInt1 = df[(df['Day'] == 'Tuesday') & (df['interval'] == 1)].mean()
    tueInt2 = df[(df['Day'] == 'Tuesday') & (df['interval'] == 2)].mean()
    tueInt3 = df[(df['Day'] == 'Tuesday') & (df['interval'] == 3)].mean()
    tueInt4 = df[(df['Day'] == 'Tuesday') & (df['interval'] == 4)].mean()
    tueInt5 = df[(df['Day'] == 'Tuesday') & (df['interval'] == 5)].mean()
    tueInt6 = df[(df['Day'] == 'Tuesday') & (df['interval'] == 6)].mean()

    wedInt1 = df[(df['Day'] == 'Wednesday') & (df['interval'] == 1)].mean()
    wedInt2 = df[(df['Day'] == 'Wednesday') & (df['interval'] == 2)].mean()
    wedInt3 = df[(df['Day'] == 'Wednesday') & (df['interval'] == 3)].mean()
    wedInt4 = df[(df['Day'] == 'Wednesday') & (df['interval'] == 4)].mean()
    wedInt5 = df[(df['Day'] == 'Wednesday') & (df['interval'] == 5)].mean()
    wedInt6 = df[(df['Day'] == 'Wednesday') & (df['interval'] == 6)].mean()

    thuInt1 = df[(df['Day'] == 'Thursday') & (df['interval'] == 1)].mean()
    thuInt2 = df[(df['Day'] == 'Thursday') & (df['interval'] == 2)].mean()
    thuInt3 = df[(df['Day'] == 'Thursday') & (df['interval'] == 3)].mean()
    thuInt4 = df[(df['Day'] == 'Thursday') & (df['interval'] == 4)].mean()
    thuInt5 = df[(df['Day'] == 'Thursday') & (df['interval'] == 5)].mean()
    thuInt6 = df[(df['Day'] == 'Thursday') & (df['interval'] == 6)].mean()

    friInt1 = df[(df['Day'] == 'Friday') & (df['interval'] == 1)].mean()
    friInt2 = df[(df['Day'] == 'Friday') & (df['interval'] == 2)].mean()
    friInt3 = df[(df['Day'] == 'Friday') & (df['interval'] == 3)].mean()
    friInt4 = df[(df['Day'] == 'Friday') & (df['interval'] == 4)].mean()
    friInt5 = df[(df['Day'] == 'Friday') & (df['interval'] == 5)].mean()
    friInt6 = df[(df['Day'] == 'Friday') & (df['interval'] == 6)].mean()

    satInt1 = df[(df['Day'] == 'Saturday') & (df['interval'] == 1)].mean()
    satInt2 = df[(df['Day'] == 'Saturday') & (df['interval'] == 2)].mean()
    satInt3 = df[(df['Day'] == 'Saturday') & (df['interval'] == 3)].mean()
    satInt4 = df[(df['Day'] == 'Saturday') & (df['interval'] == 4)].mean()
    satInt5 = df[(df['Day'] == 'Saturday') & (df['interval'] == 5)].mean()
    satInt6 = df[(df['Day'] == 'Saturday') & (df['interval'] == 6)].mean()

    sunInt1 = df[(df['Day'] == 'Sunday') & (df['interval'] == 1)].mean()
    sunInt2 = df[(df['Day'] == 'Sunday') & (df['interval'] == 2)].mean()
    sunInt3 = df[(df['Day'] == 'Sunday') & (df['interval'] == 3)].mean()
    sunInt4 = df[(df['Day'] == 'Sunday') & (df['interval'] == 4)].mean()
    sunInt5 = df[(df['Day'] == 'Sunday') & (df['interval'] == 5)].mean()
    sunInt6 = df[(df['Day'] == 'Sunday') & (df['interval'] == 6)].mean()

    weekMean = [
        [(round(monInt1['avgVacency'], 0)), (round(monInt2['avgVacency'], 0)), (round(monInt3['avgVacency'], 0)),
         (round(monInt4['avgVacency'], 0)), (round(monInt5['avgVacency'], 0)), (round(monInt6['avgVacency'], 0)), maxB],
        [(round(tueInt1['avgVacency'], 0)), (round(tueInt2['avgVacency'], 0)), (round(tueInt3['avgVacency'], 0)),
         (round(tueInt4['avgVacency'], 0)), (round(tueInt5['avgVacency'], 0)), (round(tueInt6['avgVacency'], 0))],
        [(round(wedInt1['avgVacency'], 0)), (round(wedInt2['avgVacency'], 0)), (round(wedInt3['avgVacency'], 0)),
         (round(wedInt4['avgVacency'], 0)), (round(wedInt5['avgVacency'], 0)), (round(wedInt6['avgVacency'], 0))],
        [(round(thuInt1['avgVacency'], 0)), (round(thuInt2['avgVacency'], 0)), (round(thuInt3['avgVacency'], 0)),
         (round(thuInt4['avgVacency'], 0)), (round(thuInt5['avgVacency'], 0)), (round(thuInt6['avgVacency'], 0)),],
        [(round(friInt1['avgVacency'], 0)), (round(friInt2['avgVacency'], 0)), (round(friInt3['avgVacency'], 0)),
         (round(friInt4['avgVacency'], 0)), (round(friInt5['avgVacency'], 0)), (round(friInt6['avgVacency'], 0))],
        [(round(satInt1['avgVacency'], 0)), (round(satInt2['avgVacency'], 0)), (round(satInt3['avgVacency'], 0)),
         (round(satInt4['avgVacency'], 0)), (round(satInt5['avgVacency'], 0)), (round(satInt6['avgVacency'], 0))],
        [(round(sunInt1['avgVacency'], 0)), (round(sunInt2['avgVacency'], 0)), (round(sunInt3['avgVacency'], 0)),
         (round(sunInt4['avgVacency'], 0)), (round(sunInt5['avgVacency'], 0)), (round(sunInt6['avgVacency'], 0))]]
    c.close()
    g.db.close()
    return jsonify(weekMean=weekMean)

# this is the search function we build in , we get key works form html serach input, use it as a argument for sql to ask for data. 

@app.route('/search', methods=['GET', 'POST']) # we have two route attch to this function as one is for home page to index1, one is for search with index1 html
@app.route('/index1', methods=['GET', 'POST'])
def search():
    # if request.method == "POST":
    g.db = dbconnect.connection()
    c = g.db.cursor()
    search = request.form['search']
    sql4_str = sql4.format(addr = search)
    cur = c.execute(sql4_str) 
    rows = c.fetchall()
    stations = {} # i created  a local dictionary to store the information from sql, and then pass it to my js to precess and use. 
    for eachRow in rows:
        case = {'key1': eachRow[0], 'key2': eachRow[1], 
                'key3':eachRow[2], 'key4':eachRow[3], 
                'key5':eachRow[4],'key6':eachRow[5],    
                'key7':eachRow[6],'key8':eachRow[7],
                'key9':eachRow[8],'key10':eachRow[9]}
        stations.update(case)
    print('connection')
    c.close()
    g.db.close()
    return  render_template('index1.html', stations=stations )
        
if __name__ == '__main__':
        app.run(debug=True, use_reloader=True)