import asyncio
import getpass
import json
import os

import websockets
from mapa import Map
import random

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        while True:
            try:
                update = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                if "map" in update:
                    # we got a new level
                    # Example: {'fps': 10, 'timeout': 3000, 'map': 'levels/1.xsb'}
                    game_properties = update
                    mapa = Map(update["map"])
                    print("\nNew level received!")
                    print("The map is...")
                    print(mapa)
                    state = None
                else:
                    # we got a current map state update
                    # Example: {'player': 'goncalom', 'level': 1, 'step': 144, 'score': [0, 0, 144], 'keeper': [2, 3], 'boxes': [[1, 3], [3, 4]]}
                    if state == None:
                        state = update
                        print("\nFirst state received!")
                        import pprint
                        pprint.pprint(state)
                    else:
                        state = update

                # Execute random keys
                keys = ["w", "a", "s", "d"]
                key = keys[random.randint(0, len(keys)-1)]

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server - you must implement this send in the AI agent

            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return


# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
