#connect to discord using authentication token and read chat data

import websocket #pip install websocet-client
import json
import threading
import time
import os
from datetime import datetime
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()

def send_json_request(ws, request):
    ws.send(json.dumps(request))


def receive_json_response(ws):
    response = ws.recv()
    if response:
        return (json.loads(response))


def heartbeat(interval, ws):
    print("heartbeat begins")
    while True:
        time.sleep(interval)
        heartbeatJSON = {
            "op":1,
            "d": "null"
        }
        send_json_request(ws, heartbeatJSON)
        print("heartbeat sent")


def safe_get():
    try:
        val = event['d']['guild_id']
    except KeyError:
            return None
    return val

if __name__=='__main__':
    print('starting local read discord server : ', os.getenv('SERVER_NAME'))

    ws = websocket.WebSocket()
    ws.connect('wss://gateway.discord.gg/?v=8&encording=json')
    event = receive_json_response(ws)
    heartbeat_interval = event['d']['heartbeat_interval'] /1000
    threading._start_new_thread(heartbeat, (heartbeat_interval, ws))


    token = os.getenv('TOKEN')

    payload = {
      "op": 2,
      "d": {
        "token": token,
        "intents": 513,
        "properties": {
          "$os": "osx",
          "$browser": "chrome",
          "$device": "pc"
        }
      }
    }

    send_json_request(ws, payload)

    while True:
        event = receive_json_response(ws)
        try:

            op_code = event['op']
            if op_code == 11:
                print('heartbeat received')

            if safe_get():

                guild_id = event['d']['guild_id']
                channel_id = event['d']['channel_id']
                timestamp = event['d']['timestamp']
                username = event['d']['author']['username']
                content = event['d']['content']

                #post request to the flask app
                print(guild_id, channel_id, timestamp, username, content)
                record = {'guild_id':int(guild_id), 'channel_id':int(channel_id), 'time':str(timestamp)}
                r = requests.post(os.getenv('LOG_URL'), json=record)
                print('server response: ', r)

        except Exception as error:
            print('exception', error)
            pass
