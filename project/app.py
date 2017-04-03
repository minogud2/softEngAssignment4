from flask import Flask, render_template, url_for, request, session, flash, g
from functools import wraps
import sys
from flask_mysqldb import MySQLdb
import dbconnect
from flask import Flask, g, jsonify,render_template

#create appl object
app = Flask(__name__)

# @app.route('/')
# def hello():
#     g.db = dbconnect.connection()
#     print('connect to data base')
#     c = g.db.cursor()
#     cur = c.execute('select * from DynamicTest ') 
    
#     dbdata = []
#     rows = c.fetchall()
#     for eachRow in rows[:15]:
#         dbdata.append(dict(num=eachRow[0], last_update=eachRow[1], status=eachRow[2], available_bikes=eachRow[3], bike_stands=eachRow[4], available_bike_stands=eachRow[5], banking=eachRow[6]))
    
#     c.close()
#     g.db.close()
#     return render_template('helloDynamic.html', dbdata=dbdata)
@app.route("/")
def index():

    return render_template('index.html')

@app.route("/stations") 
def staticStation():

    g.db = dbconnect.connection()
    print('connect to data base')
    c = g.db.cursor()
    cur = c.execute('select * from static ') 
    
    stations = []
    rows = c.fetchall()
    for eachRow in rows:
        # stations.append(dict(ID=eachRow[0], address=eachRow[1], name=eachRow[2], long=eachRow[3], lat=eachRow[4]))
        stations.append(eachRow[0])
        stations.append(eachRow[1])
        stations.append(eachRow[2])
        stations.append(eachRow[3])
        stations.append(eachRow[4])
    
    c.close()
    g.db.close()

    return jsonify(stations=stations)



sql = """SELECT DISTINCT
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
    static.num = DynamicTest.num
ORDER BY last_update ASC
LIMIT 101;"""

sql1 = """SELECT DISTINCT
    weather.timeStamp,
    weather.weatherID,
    weather.temp,
    weather.descp,
    weather.icons
FROM
    weather
ORDER BY timeStamp DESC
LIMIT 1;"""
@app.route('/stations1')
def get_mainpage():
    g.db = dbconnect.connection()
    c = g.db.cursor()
    cur = c.execute(sql) 
    rows = c.fetchall()
    stations = []
    for eachRow in rows:
        stations.append(eachRow)
    c.close()
    g.db.close()
    return jsonify(stations=stations)

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



if __name__ == '__main__':
        app.run(debug=True)