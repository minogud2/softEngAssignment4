'''
Created on 26 Mar 2017

@author: minogud2
'''
import sqlite3 as lt
import time
import datetime
import requests

def get_Data(url):
    data = requests.get(url).json()
    unix = time.time()
    date = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H: %M: %S'))
    
    weather_id = data['weather'][0]['id']
    temperature = data['main']['temp']
    description = data['weather'][0]['description']
    weather_icon = data['sys']['sunset']
    cur.execute("INSERT INTO weather(timeStamp, weatherID, temp, desc, icon) VALUES (?,?,?,?,?)",
                (date, weather_id, temperature, description, weather_icon)) 
    con.commit()

if __name__ == '__main__':
    try:
        con = lt.connect('dublin_BikesRDB.db')
        cur = con.cursor()
        url='http://api.openweathermap.org/data/2.5/weather?id=2964574&APPID=33e340fbba76a4645e26160abb37f014&units=metric'
        
        for i in range(2):
            get_Data(url)
            time.sleep(5)     
            
    finally:
        cur.close()
        con.close()