import asyncio
import websockets
import json
import time
import logging

LOG = logging.getLogger()
my_ch = logging.StreamHandler()
my_ch.setLevel(logging.DEBUG)
formatter_console = logging.Formatter(
    '%(asctime)s %(levelname) -10s %(name) -10s %(lineno) -5d  %(message)s'
)
my_ch.setFormatter(formatter_console)
LOG.setLevel(logging.INFO)
LOG.addHandler(my_ch)


class WssClient:
    def __init__(self,callback_function):
        self.ws_client= None
        self.callback=callback_function

    async def on_msg(self, websocket):
        while True:
            async for message in websocket:
                LOG.info(message)
                await self.callback(message)
            await asyncio.sleep(0.1)

    def get_ping_json(self):
        curent_mili = round(time.time() * 1000)
        ping_dict = {
            "action": "ping",
            "timestamp": curent_mili
        }
        json_string = json.dumps(ping_dict)
        return json_string

    def mesaj_auth(self):
        auth_dict = {
            "action": "auth",
            "username": "vlad",
            "password": "pass"
        }
        json_string = json.dumps(auth_dict)
        return json_string

    def get_weather_msg(self,chat_id=0):
        weather_dict = {
            "action": "weather",
            "location":"bucuresti",
            "chatID": chat_id
        }
        json_string = json.dumps(weather_dict)
        return json_string

    async def start_wsclient(self):
        async with websockets.connect('ws://localhost:8000') as websocket:
            self.ws_client=websocket
            new_ping = self.get_ping_json()
            await websocket.send(new_ping)
            resp = await websocket.recv()
            # await websocket.send("Salut!")

            vreme = self.get_weather_msg()
            await  websocket.send(vreme)

            auth = self.mesaj_auth()
            await websocket.send(auth)

            # raspuns_timer=await websocket.recv()
            # print(raspuns_timer)

            await self.on_msg(websocket)
            # await asyncio.sleep(60)

    # asyncio.run(start_wsclient())
