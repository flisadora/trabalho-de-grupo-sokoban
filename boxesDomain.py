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

    allActions = { # Up, left, down and right
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
    
    def __init__(self,map):
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
                if char in ['.', '*']:
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

        print("Actions for...", state)

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
                    continue
                        
                # If action is valid, append it to list
                actions.append((index, action))

            # Update box index
            index += 1

        print(actions)
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
        print("result()", state, action)
        move = self.allActions[action[1]]
        moveReverse = self.allActions[self.actionReverse[action[1]]]

        # Box to be moved
        box = (0,0)
        box = (state['boxes'][action[0]])

        newState = {
            'keeper': state['keeper'],
            'boxes': [box for box in state['boxes']],
            'action': '' 
        }
        newState['boxes'][action[0]] = move(box)
        initialState = { 'keeper': state['keeper'], 'action': '' }
        goalState = { 'keeper': moveReverse(box), 'action': '' }

        # Check if agent already on goal state
        if initialState['keeper'] == goalState['keeper']:
            # Compute actions
            newState['action'] = action[1]
            # Compute keeper new position
            newState['keeper'] = move(goalState['keeper'])
        # If not on state, find path
        # Only if keeper not in wall
        elif self.map[goalState['keeper'][1]][goalState['keeper'][0]] != "#":
            # Create tree to search keeper path to move box
            d = KeeperDomain(self.map, state['boxes'])
            p = SearchProblem(d, initialState, goalState)
            t = SearchTree(p, 'a*')
            search = t.search()
            sol = await search 


            if not sol:
                return None

            # Compute actions
            newState['action'] = BoxesDomain.getActions(sol) + action[1]
            # Compute keeper new position
            newState['keeper'] = move(goalState['keeper'])

        print("FOUND KEEPER PATH", newState)

        return newState

    # custo de uma accao num estado
    def cost(self, state, action):
        return 1


    # custo estimado de chegar de um estado a outro
    def heuristic(self, state, goal):
        heuristic = 0
        for box in state['boxes']:
            # Sum the distance between each box and each diamond
            for diamond in self.diamonds:
                heuristic += hypot(diamond[0] - box[0], diamond[1] - box[1])

        return heuristic

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