
from tree_search import SearchDomain 

from math import hypot

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
    action: (w|s|a|d)
}
"""
class KeeperDomain(SearchDomain):

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

    def __init__(self,map,boxes):
        self.map = map 
        self.boxes = boxes

    """ 
    Define possible actions for keeper position so that
    - Does not move against the wall
    - Does not move against a box
    --- Parameters
    state
      keeper            (x, y)
    --- Returns
    actions             [ action ], action type is char
    """
    def actions(self, state):
        actions = []

        for action, move in self.allActions.items():

            keeper = move(state['keeper'])

            # 1. Check if keeper is hover the wall
            if self.map[keeper[1]][keeper[0]] == '#': 
                continue

            # 2. Check if keeper is hover a box
            if self.map[keeper[1]][keeper[0]] in ['$', '*']: 
                continue

            # If action is valid, append it to list
            actions.append(action)

        return actions     
        

    """
    Given a state and done the action, returns the result state
    --- Parameters
    state
      keeper            (x, y)
    action      (indexBox, action)
    --- Returns
    newState with keeper position updated
    """
    async def result(self, state, action):
        return { 'keeper' : self.allActions[action](state['keeper']), 'action': action }
          
    def cost(self, state, action):
        return 0 

    """
    Returns the Manhatan distance between the keeper current and goal positions
    --- Parameters
    state       Current state 
    goal        Goal state
    --- Returns
    distance    float
    """
    def heuristic(self, state, goal):
        (x,y) = state['keeper']
        (x1,y1) = goal['keeper']

        return hypot(x-x1,y-y1)
        
              
    # test if the given "goal" is satisfied in "state"
    def satisfies(self, state, goal):
        return state['keeper'] == goal['keeper']

