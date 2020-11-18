import asyncio
import getpass
import json
import os
import random

import websockets
from mapa import Map
from node import PathAlgorithm 

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        
        pos_boxes = []
        pos_keeper = None
        '''
        n = PathAlgorithm() 
        k = n.search((1,1),(3,4))
        print(n.search((1,1),(3,4)))
       '''
        
        while True:
            try:
                update = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or your game will get out of sync with the server
                
                if "map" in update:
                    # we got a new level
                    game_properties = update
                    mapa = Map(update["map"])
                    state = None
                else:
                    if state == None:
                        state = update
                        # If first state, output it as an example

                        print("\nFirst state received!")
                        #import pprint
                        #pprint.pprint(state)
                    else:
                        state = update
                        # Update elements positions
                        pos_boxes = update['boxes']
                        pos_keeper = update['keeper']
                        import pprint
                        pprint.pprint(pos_keeper)
                       

                    #n = PathAlgorithm()
                    #pprint.pprint(n.search(pos_boxes[1],pos_keeper))                  
                    #key = [ i[1] for i in k]
                    
                while True:
                    # Pick a random key
                    keys = ["w", "a", "s", "d"] # Up, left, down and right
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
