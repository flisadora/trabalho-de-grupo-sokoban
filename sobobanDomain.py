from tree_search import SearchDomain

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
    'keeper': (x, y),
    'boxes': [ (x, y) ]
}
"""
class SokobanDomain(SearchDomain):

    allActions = { # Up, left, down and right
        'w': lambda x: (x[0], x[1]-1),
        'a': lambda x: (x[0]-1, x[1]),
        's': lambda x: (x[0], x[1]+1),
        'd': lambda x: (x[0]+1, x[1]),
    }

    def __init__(self,map):
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
    Define possible actions for keeper position so that
    - Does not move againts the wall
    - Does not push a box to a dead end
    - Does not move a box on diamond
    --- Parameters
    state
      keeper          (x, y)
      boxes           [(x, y)]
    """
    def actions(self, state):
        actions = []
        # For every possible action
        for action, move in self.allActions.items():
            actionValid = True

            # Compute keeper new position
            keeperPosition = move(state['keeper'])

            # 1. Check if keeper is moving against the wall
            if self.map[keeperPosition[1]][keeperPosition[0]] == '#': continue

            # 2. Validate box movements
            for box in state['boxes']:
                if box == keeperPosition:
                    # 2.1. Check if box is hover diamond (don't want to remove it!)
                    if box in self.diamonds: actionValid = False

                    # Get box new position
                    boxPosition = move(box)
                    boxNextPosition = move(boxPosition)
                    
                    # 2.2. Check if new position is hover diamond
                    if boxPosition in self.diamonds: continue

                    # 2.3. Check if moving box to dead end (if next position is wall)
                    if self.map[boxNextPosition[1]][boxNextPosition[0]] == '#':
                        print("GOING AGAINST THE WALL with action", action)
                        actionValid = False
            
            # If action is valid, append it to list
            if not actionValid: continue
            actions.append(action)

        return actions

    """
    Given a state and done the action, returns the result state
    """
    def result(self, state, action):
        move = self.allActions[action]

        newState = {
            'keeper': move(state['keeper']),
            'boxes': []
        }

        for box in state['boxes']:
            if box == newState['keeper']:
                newState['boxes'].append(move(box))
            else:
                newState['boxes'].append(box)

        return newState

    # custo de uma accao num estado
    def cost(self, state, action):
        return 0

    # custo estimado de chegar de um estado a outro
    def heuristic(self, state, goal):
        points = 0
        for box in goal['boxes']:
            if box in self.diamonds:
                points -= 1

        return points

    # test if the given "goal" is satisfied in "state"
    def satisfies(self, state, goal):
        for box in goal['boxes']:
            if box not in state['boxes']:
                return False
        return True