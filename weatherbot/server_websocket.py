import asyncio
import json
import logging
import websockets
import time
import requests

LOG = logging.getLogger()
my_ch = logging.StreamHandler()
my_ch.setLevel(logging.DEBUG)
formatter_console = logging.Formatter(
    '%(asctime)s %(levelname) -10s %(name) -10s %(lineno) -5d  %(message)s'
)
my_ch.setFormatter(formatter_console)
LOG.setLevel(logging.INFO)
LOG.addHandler(my_ch)

USERS = set()

VALUE = 0

LOCATIONS = {
    "bucuresti": [44.43, 26.11],
    "corbeanca": [44.60, 26.05],
    "brasov": [45.65, 25.61]
}


def process_weather(message):
    city = message.get("location", "bucuresti")
    lat, lon = LOCATIONS[city]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,rain&forecast_days=1"
    response = requests.get(url)
    weather_data = json.loads(response.text)
    temperatures = weather_data.get("hourly").get("temperature_2m")
    temperature_max = max(temperatures)
    precipitation_list = weather_data.get("hourly").get("rain")
    confirmed_rain = any(precipitation_list)
    weather_dict = {
        "action": "weather",
        "location": city,
        "max temperature": temperature_max,
        "precipitations": confirmed_rain,
        "chatID": message.get("chatID"),
        "username": message.get("username")
    }
    weather_msg = json.dumps(weather_dict)
    websockets.broadcast(USERS, weather_msg)


def process_ping(message):
    current_milli = round(time.time() * 1000)
    pong_dict = {
        "action": "pong",
        "timestamp": current_milli
    }
    pong_msg = json.dumps(pong_dict)
    websockets.broadcast(USERS, pong_msg)


def process_auth(message):
    my_users_dict = {
        "username": "vlad",
        "password": "pass"
    }
    user_recv = message.get("username", "")
    password_recv = message.get("password", "")
    if user_recv == my_users_dict["username"] and password_recv == my_users_dict["password"]:
        auth_dict = {
            "action": "auth",
            "status": True,
            "desc": ""
        }
        auth_msg = json.dumps(auth_dict)
        websockets.broadcast(USERS, auth_msg)
    else:
        error_dict = {
            "action": "auth",
            "status": False,
            "desc": "Error: user does not exist"
        }
        auth_msg_error = json.dumps(error_dict)
        websockets.broadcast(USERS, auth_msg_error)


def users_event():
    return json.dumps({"type": "users", "count": len(USERS)})


def value_event():
    return json.dumps({"type": "value", "value": VALUE})


async def counter(websocket):
    global USERS, VALUE
    actions = {
        "ping": process_ping,
        "auth": process_auth,
        "weather": process_weather
    }
    while True:
        try:
            # Register user
            USERS.add(websocket)
            websockets.broadcast(USERS, users_event())
            # Send current state to user
            await websocket.send(value_event())
            # Manage state changes
            async for message in websocket:
                LOG.info(message)
                event = json.loads(message)
                act = event.get("action", "unknown")
                actions[act](event)

        finally:
            # Unregister user
            USERS.remove(websocket)
            websockets.broadcast(USERS, users_event())


async def start_server():
    async with websockets.serve(counter, "127.0.0.1", 8021):
        await asyncio.Future()  # run forever


def main():
    asyncio.run(start_server())


if __name__ == "__main__":
    main()

