import asyncio
import getpass
import json
import os
import random

import websockets
from mapa import Map
from tree_search import SearchTree, SearchProblem
from boxesDomain import boxesDomain
from time import time

def getActions(states):
    actions = ""
    for state in states:
        if state['action']:
            actions += state['action']

    return actions

async def solver(puzzle, solution):
    while True:
        game_properties = await puzzle.get()
        mapa = Map(game_properties["map"])
        print("\nSearching solution for a new map!")
        print(mapa)

        print("\nBuilding search domain...")
        d = boxesDomain(str(mapa))
        print(d.map)
        print(d.diamonds)

        print("\nBuilding search problem...")
        initialState = { 'boxes': mapa.boxes }
        print(initialState)
        goalState = { 'boxes': d.diamonds }
        print(goalState)
        p = SearchProblem(d, initialState, goalState)
        
        print("\nBuilding search tree...")
        t = SearchTree(p, 'a*')

        print("\nCreating coroutine for search...")
        start_time = time()
        search = t.search(40)
        print(search)
        
        print("\nWaiting for search...")
        sol = await search
        print("\nSearch done!")
        print(sol)

        keys = ""
        if sol:
            print("\nTHERE IS A SOLUTION")
            print("\nThe keys are...")
            keys = getActions(sol)
            print(keys)
            # Save solution to file
            with open(f'solutions/{game_properties["map"].split("/")[1]}', 'w') as f:
                for l in d.map:
                    f.write(l)
                    f.write("\n")
                f.write("\n")
                f.write("Keys for solution are:")
                f.write(keys)
                f.write("\n\n")
                f.write(f'Time taken to run: {time() - start_time} seconds')
                f.write("\n")
        else:
            print("\nSolution NOT FOUND!")

        await solution.put(keys)

async def agent_loop(puzzle, solution, server_address="localhost:8000", agent_name="student"):
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
                    game_properties = update
                    keys = ""
                    print("\nReceived game properties!")
                    print(game_properties)
                    await puzzle.put(game_properties)

                if not solution.empty():
                    keys = await solution.get()

                key = ""
                if len(keys):  # we got a solution!
                    key = keys[0]
                    keys = keys[1:]

                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )

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

puzzle = asyncio.Queue(loop=loop)
solution = asyncio.Queue(loop=loop)

net_task = loop.create_task(agent_loop(puzzle, solution, f"{SERVER}:{PORT}", NAME))
solver_task = loop.create_task(solver(puzzle, solution))

loop.run_until_complete(asyncio.gather(net_task, solver_task))
loop.close()
