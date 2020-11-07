import asyncio
import getpass
import json
import os

import websockets
from mapa import Map
import random

def throwsBoxAgainstTheWall(map, pos_boxes, pos_keeper, move):
    """ Validates if an action with the current elements positions will throw a box against a wall
    --- Parameters
    map             Map object 
    pos_boxes       Array of box positions in the form [x, y]
    pos_keeper      Position of keeper in the form [x, y]
    move            Function that computes position evolution
    --- Returns
    againstWall     True if action is not going to throw box against the wall
    """

    # Compute agent new position
    newAgentPosition = move(pos_keeper)

    # Check if there is any box at that position (that whould be pushed)
    mapArray = str(map).split("\n")
    for box in pos_boxes:
        if box == newAgentPosition:
            # Get box new position
            newBoxPosition = move(box)
            # Check if up that position is wall, and if so that box is going to be thrown against the wall
            shouldNotBeWall = move(newBoxPosition)
            # Invert coordinates because mapArray first index goes for the line (y) and the second for the col (x)
            if mapArray[shouldNotBeWall[1]][shouldNotBeWall[0]] == '#':
                return True
    
    return False

def goingAgainstTheWall(map, pos_keeper, move):
    """ Tells if the agent is moving against the wall
    --- Parameters
    map             Map object 
    pos_keeper      Position of keeper in the form [x, y]
    move            Function that computes position evolution
    --- Returns
    goingAgainst    True if going against the wall
    """
    # Compute agent new position and map array
    newAgentPosition = move(pos_keeper)
    mapArray = str(map).split("\n")

    # Check if at the agent new position it is wall
    if mapArray[newAgentPosition[1]][newAgentPosition[0]] == '#':
        return True
    
    return False


def actionValid(map, pos_boxes, pos_keeper, action):
    """ Tells if an action is valid
    --- Parameters
    map             Map object 
    pos_boxes       Array of box positions in the form [x, y]
    pos_keeper      Position of keeper in the form [x, y]
    action          Action to throw (String)
    --- Returns
    actionValid     True if action is valid
    """
    # Check if arguments are already defined (they are not defined on first action yet)
    if map == None or len(pos_boxes) == 0 or pos_keeper == None:
        return True
    
    # Define function to compute position changes based on action
    move = None
    if action == 'w': #Up
        move = lambda x: [x[0], x[1]-1]
    elif action == 'a': #Left
        move = lambda x: [x[0]-1, x[1]]
    elif action == 's': #Down
        move = lambda x: [x[0], x[1]+1]
    elif action == 'd': #Right
        move = lambda x: [x[0]+1, x[1]]
    
    # Check if it is going to throw box against the wall
    if throwsBoxAgainstTheWall(map, pos_boxes, pos_keeper, move):
        return False
    # Check if agent is moving against the wall
    if goingAgainstTheWall(map, pos_keeper, move):
        return False

    return True

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:

        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        # Keep positiontrack of elements positions
        pos_boxes = []
        pos_keeper = None

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

                # Execute commands
                while True:
                    # Pick a random key
                    keys = ["w", "a", "s", "d"] # Up, left, down and right
                    key = keys[random.randint(0, len(keys)-1)]

                    # Check if action is valid
                    if not actionValid(mapa, pos_boxes, pos_keeper, key):
                        continue

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
