import asyncio
import getpass
import json
import os

import websockets
from mapa import Map
import random
from node import PathAlgorithm


def moves (map, pos_boxes, pos_keeper):
    if map == None or len(pos_boxes) == 0 or len(pos_keeper):
        return []
    k = []
    n = PathAlgorithm() 
    k = n.search(pos_boxes[1],pos_keeper) #retorna uma lista com o caminho e as teclas
    return k 


async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        # Keep positiontrack of elements positions
        pos_boxes = []
        pos_keeper = None
        s = []
        while True:
            try:
                update = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server

                if "map" in update:
                    # we got a new level
                    # Example: {'fps': 10, 'timeout': 3000, 'map': 'levels/1.xsb'}
                    mapa = Map(update["map"])
                    print("\nNew level received!")
                    print("The map is...")
                    print(mapa)
                    print(update)
                    state = None
                else:
                    # we got a current map state update
                    # Example: {'player': 'goncalom', 'level': 1, 'step': 144, 'score': [0, 0, 144], 'keeper': [2, 3], 'boxes': [[1, 3], [3, 4]]}
                    if state == None:
                        state = update
                        # If first state, output it as an example
                        print("\nFirst state received!")
                        import pprint
                        pprint.pprint(state)
                    else:
                        state = update
                        # Update elements positions
                        pos_boxes = update['boxes']
                        pos_keeper = update['keeper']

                #Se o resultado do moves for uma array vazio ele continua e caso nao guarda o valor 
                # do caminho e das teclas em s     
                while True:
                    if moves (map,pos_boxes,pos_keeper) == []:     
                        continue
                    else:
                        s = moves (map,pos_boxes,pos_keeper)
                        import pprint
                        pprint.pprint(s)
                        pprint.pprint(pos_boxes)  
                         
                    break
                       
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