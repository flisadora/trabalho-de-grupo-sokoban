
from abc import ABC, abstractmethod
from math import hypot

# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class keeperWorld(SearchDomain):

    # construtor
    
    def __init__(self,map,boxes):
        # map array
        self.map = map 
        self.boxes = boxes

        

    # lista de accoes possiveis num estado
   
    def actions(self, state):
        action = []
        (x,y) = state['keeper']
            
        neighbours = [(x-1,y,"w"),(x+1,y,"s"),(x,y-1,"a"),(x,y+1,"d")]

        for next in neighbours:
            if self.map.is_blocked((next[0],next[1])) or (x,y) in self.boxes:
                continue
            else:
                action.append(next)
        return action     
        

    # resultado de uma accao num estado, ou seja, o estado seguinte
    def result(self, state, action):
        return { 'keeper' : (action[0],action[1]) }
        
    # custo de uma accao num estado
  
    def cost(self, state, action):
        return 0 

    # custo estimado de chegar de um estado a outro

    def heuristic(self, state, goal):
        (x,y) = state['keeper']
        (x1,y1) = goal['keeper']

        return  hypot(x-x1,y-y1)
        
              
    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        return state['keeper'] == goal['keeper']

