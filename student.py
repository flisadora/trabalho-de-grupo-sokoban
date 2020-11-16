import asyncio
import getpass
import json
import os
import random

import websockets
from mapa import Map
from tree_search import SearchTree, SearchProblem
from sobobanDomain import SokobanDomain

async def solver(puzzle, solution):
    while True:
        game_properties = await puzzle.get()
        mapa = Map(game_properties["map"])
        print("\nSearching solution for a new map!")
        print(mapa)

        print("\nBuilding search domain...")
        d = SokobanDomain(str(mapa))
        print(d.map)
        print(d.diamonds)

        print("\nBuilding search problem...")
        initialState = { 'keeper': mapa.keeper, 'boxes': mapa.boxes }
        print(initialState)
        goalState = { 'keeper': mapa.keeper, 'boxes': d.diamonds }
        print(goalState)
        p = SearchProblem(d, initialState, goalState)
        
        print("\nBuilding search tree...")
        t = SearchTree(p, 'a*')

        sol = t.search(50)
        if sol:
            print("\nTHERE IS A SOLUTION")
            print(sol)
        else:
            print("\nSolution NOT FOUND!")


        while True:
            # Pick a random key
            # keys = ["w", "a", "s", "d"] # Up, left, down and right
            # key = keys[random.randint(0, len(keys)-1)]

            await asyncio.sleep(0)
            break

        await solution.put("")

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
