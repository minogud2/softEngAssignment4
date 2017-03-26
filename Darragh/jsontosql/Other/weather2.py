import requests
import json
import pprint
import sqlite3 as lt
import datetime

# Source: https://gist.github.com/Tafkas/fe7dc920b288fc5d5b45
# print(dir(requests))
# 
# help(requests.get)

url='http://api.openweathermap.org/data/2.5/weather?id=2964574&APPID=33e340fbba76a4645e26160abb37f014&units=metric'
DB_PATH = ''

def get_Data():
    data = requests.get(url).json()
    pprint.pprint(data)
    temp = data['main']['temp']
    pressure = data['main']['pressure']
    temp_min = data['main']['temp_min']
    temp_max = data['main']['temp_max']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    wind_deg = data['wind']['deg']
    clouds = data['clouds']['all']
    weather_id = data['weather'][0]['id']
    sunrise = data['sys']['sunrise']
    sunset = data['sys']['sunset']
    
    return [temp, pressure, temp_min, temp_max, humidity, wind_speed, wind_deg, clouds,
            weather_id, sunrise, sunset]

def save_data_to_db(data):
    con = lt.connect('db_Dataset.db')
    
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE Static(timeStamp DATETIME, weather TEXT, temp TEXT)")
        
        cur = con.cursor()
        query = '''INSERT INTO weather_data VALUES (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        cur.execute(query, tuple([datetime.datetime.now().isoformat()] + data[:-2]))
        con.commit()
        con.close()
    
def main():
    data = get_Data()
    print(data)
    
if __name__ == '__main__':
    main()