from tree_search import SearchDomain

from math import hypot

from tree_search import SearchTree, SearchProblem
from keeperDomain import KeeperDomain

"""
Map example:
####--
#-.#--
#--###
#*@--#
#--$-#
#--###

Legend:
@ Keeper
+ Keeper on diamond
# Wall
. Diamond free
$ Box free
* Box on diamond

In the map coordinates (x,y), the vertical axis is y and the horizontal one is x:
_ _ _ > x
|
|
v
y

A state is an object with the following structure:
{
    keeper: (x,y)
    boxes: [ (x, y)* ]
    action: (w|s|a|d)
}
"""


class BoxesDomain(SearchDomain):

    allActions = {  # Up, left, down and right
        'w': lambda x: (x[0], x[1]-1),
        'a': lambda x: (x[0]-1, x[1]),
        's': lambda x: (x[0], x[1]+1),
        'd': lambda x: (x[0]+1, x[1]),
    }

    actionReverse = {
        'a': 'd',
        'd': 'a',
        'w': 's',
        's': 'w'
    }

    def __init__(self, map):
        self.teacherMap = map
        # Build map array
        self.map = map.split("\n")
        # Get diamonds location
        self.diamonds = []
        self.findDiamonds()

    """
    This method finds diamonds location on map
    """

    def findDiamonds(self):
        y = 0
        for line in self.map:
            x = 0
            for char in line:
                if char in ['.', '*', '+']:
                    self.diamonds.append((x, y))
                x += 1
            y += 1

    """ 
    Define possible actions for box position so that
    - Does not move against or hover the wall
    - Does not move hover other box
    - Does not move to a dead end
    --- Parameters
    state
      boxes           [ (x, y)* ]
    --- Returns
    actions           [ (indexBox, action)* ]
    """

    def actions(self, state):
        actions = []
        index = 0

        for box in state['boxes']:

            # For every possible action
            for action, move in self.allActions.items():

                # Compute box new position
                boxPosition = move(box)
                boxNextPosition = move(boxPosition)

                # 1. Check if box is moving hover the wall
                if self.map[boxPosition[1]][boxPosition[0]] == '#':
                    continue

                # 2. Check if box hover another box (can't pile boxes!)
                elif boxPosition in state['boxes']:
                    continue

                # 3. Check if new position is hover diamond
                elif boxPosition in self.diamonds:
                    pass

                # 4. Check if moving box to dead end (if next position is wall)
                elif self.map[boxNextPosition[1]][boxNextPosition[0]] == '#':
                    up = BoxesDomain.allActions['w'](boxPosition)
                    down = BoxesDomain.allActions['s'](boxPosition)
                    left = BoxesDomain.allActions['a'](boxPosition)
                    right = BoxesDomain.allActions['d'](boxPosition)
                    if self.map[up[1]][up[0]] == "#" and (self.map[left[1]][left[0]] == "#" or self.map[right[1]][right[0]] == "#"):
                        continue
                    if self.map[down[1]][down[0]] == "#" and (self.map[left[1]][left[0]] == "#" or self.map[right[1]][right[0]] == "#"):
                        continue

                # If action is valid, append it to list
                actions.append((index, action))

            # Update box index
            index += 1

        return actions

    """
    Given a state and done the action, returns the result state
    --- Parameters
    state
      boxes           [ (x, y)* ]
    action      (indexBox, action)
    --- Returns
    newState
    """
    async def result(self, state, action):
        move = self.allActions[action[1]]
        moveReverse = self.allActions[self.actionReverse[action[1]]]

        # Box to be moved
        box = (state['boxes'][action[0]])

        newState = {
            'keeper': state['keeper'],
            'boxes': [box for box in state['boxes']],
            'action': ''
        }
        newState['boxes'][action[0]] = move(box)

        initialState = {'keeper': state['keeper'], 'action': ''}
        goalState = {'keeper': moveReverse(box), 'action': ''}

        # Check if agent already on goal state
        if initialState['keeper'] == goalState['keeper']:
            # Compute actions
            newState['action'] = action[1]
            # Compute keeper new position
            newState['keeper'] = move(goalState['keeper'])
        # If not on state, find path
        else:
            # Validations
            # Check if goal not in wall
            if self.map[goalState['keeper'][1]][goalState['keeper'][0]] == "#":
                return None
            # Check if goal not in box
            if goalState['keeper'] in state['boxes']:
                return None
            # Check if goal is accessible
            if all(self.map[y][x] == "#" or (x, y) in state['boxes'] for x, y in [move(goalState['keeper']) for _, move in BoxesDomain.allActions.items()]):
                return None

            # Create tree to search keeper path to move box
            sol = None
            threshold = 2*len(self.map) + len(self.map[0])
            multiplyFactor = 1.5
            limit = len(self.map) if len(self.map)<len(self.map[0]) else len(self.map[0])
            d = KeeperDomain(self.map, state['boxes'])
            p = SearchProblem(d, initialState, goalState)
            t = SearchTree(p, 'greedy')
            while not sol and limit<=threshold:
                search = t.search(limit)
                sol = await search
                if not sol:
                    t.recoverSolutions()
                limit = round(limit*multiplyFactor)

            if not sol:
                return None
            
            # Compute actions
            newState['action'] = BoxesDomain.getActions(sol) + action[1]
            # Compute keeper new position
            newState['keeper'] = move(goalState['keeper'])

        return newState

    # custo de uma accao num estado
    def cost(self, state, action):
        return 1

    # custo estimado de chegar de um estado a outro

    def heuristic(self, state, goal):
        h = 0  # heuristic cost.

        for box in state['boxes']:
            # Find closest diamond
            min_distance = float("inf")
            for diamond in self.diamonds:
                distance = hypot(diamond[0] - box[0], diamond[1] - box[1])
                if distance <= min_distance:
                    min_distance = distance
            h += min_distance  # total heuristic.
            min_distance = float("inf")  # reintialize for next iteration

        return h

    # test if the given "goal" is satisfied in "state"
    def satisfies(self, state, goal):
        for box in goal['boxes']:
            if box not in state['boxes']:
                return False
        return True

    @staticmethod
    def getActions(states):
        actions = ""
        for state in states:
            if state['action']:
                actions += state['action']

        return actions
