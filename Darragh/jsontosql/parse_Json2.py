import json
import sys
import sqlite3 as lt
from pprint import pprint   
from flask import Flask

def open_Json(json_info):
    with open(json_info) as jsonfile:
        data = json.load(jsonfile)   
        # opens a list with multiple dictionaries inside of it.
        #pprint(data) 
    return data

def convert_Sql(data):
    # to access an item in the list, you access the first dictionary.Then the key See below
    # print(data[1]["number"])
    
#   To iterate through the entire list of dictionaries, list variables were created for each column.

    number = []
    name = []
    address = []
    latitude = []
    longitude = []
    
    i = 0
    while i < len(data):
        number.append(data[i]["number"])
        name.append(data[i]["name"])
        address.append(data[i]["address"])
        latitude.append(data[i]["latitude"])
        longitude.append(data[i]["longitude"])
        i += 1  
    
    # create database to parse data into. 
    con = lt.connect('db_Dataset.db')
    
    # grab con and create table and enter input variable records. 
    # REAL is a floating point number in SQLITE3
    
    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE Static(num INT, Sname TEXT, addr TEXT, lat REAL, long REAL)")
        
        for i in range(0, len(data)):
            cur.execute("INSERT INTO Static (num, Sname, addr, lat, long) VALUES(?,?,?,?,?)",
                        (number[i], name[i], address[i], latitude[i], longitude[i]))
            con.commit()    
    cur.close()
    con.close()

    return None

def read_from_db():
    # open connection again and print out parsed sql dataset.
    
    con = lt.connect('db_Dataset.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM Static')
    data2 = cur.fetchall()
    cur.close()
    con.close()

app = Flask(__name__)

@app.route('/')
def index():
    file = 'static_dublin.json'
    data = open_Json(file)
    read_from_db()
    return "hello World"

if __name__ == "__main__":
    app.run()

# if __name__== '__main__':
    # Everything below here means that only the functions that are called will be run. This is helpful then
    # when running tests so it doesn't test every item. 
            
