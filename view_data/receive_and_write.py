#receive data and write to a PostgreSQL db

from flask import Flask, request
import os
import sqlite3
import json
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
load_dotenv()

cur_dir = os.path.dirname(__file__)

def pg_entry(event):
    try:
        conn = psycopg2.connect(user = os.getenv('USER'),
                                password = os.getenv('PASSWORD'),
                                host = os.getenv('HOST'),
                                port = os.getenv('PORT'),
                                database = os.getenv('DB')
                                )

        cursor = conn.cursor()

        # list that contain records to be inserted into table
        data = [event.get("guild_id"), event.get("channel_id"), event.get("time")]
        print(data)

        #insert data
        cursor.execute("INSERT into teststats(guild_id, channel_id, time) VALUES (%s, %s, %s)", data)

        print("inserted successfully...")

        # Commit your changes in the database
        conn.commit()

        # Closing the connection
        conn.close()

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)



app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    print('receiving server')
    incoming_event = request.get_json()

    data = request.data
    data = json.loads(data)

    print(incoming_event)
    pg_entry(incoming_event)
    return {'message': 'success'}

if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)
