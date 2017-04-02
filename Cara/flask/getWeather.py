from flask import Flask, render_template, url_for, request, session, flash, g, jsonify
from functools import wraps
import sys
from flask_mysqldb import MySQLdb
import dbconnect

#create appl object
app = Flask(__name__)

sql = """SELECT DISTINCT
    weather.timeStamp,
    weather.weatherID,
    weather.temp,
    weather.descp,
    weather.icons
FROM
    weather
<<<<<<< HEAD
ORDER BY timeStamp
=======
ORDER BY timeStamp DESC
>>>>>>> 0c25ed2088ae9fa222413612ebad0b3ec4949e2b
LIMIT 1;"""

@app.route('/')
def get_weather():
    g.db = dbconnect.connection()
    c = g.db.cursor()
    cur = c.execute(sql) 
    rows = c.fetchall()
    dbdata = []
    for eachRow in rows:
        dbdata.append(eachRow)
    c.close()
    g.db.close()
    return jsonify(dbdata=dbdata)

if __name__ == '__main__':
        app.run(debug=True)
