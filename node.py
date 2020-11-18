class Node:
    def __init__(self,pos,parent,move):
        self.pos = pos
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0 
        self.move = move 

    def __eq__(self, other):
        return self.pos == other.pos
    
    def __lt__(self, other):
         return self.f < other.f

    def __str__(self):
        return "no(" + str(self.pos) + "," + str(self.parent) + "," + str(self.g) + "," + str(self.h) + "," + str(self.f) +")"
   
    def __repr__(self):
        return str(self)

class PathAlgorithm :

    def __init__(self):
        self.solution = 0 
    
    def search (self,start,end):
        open_list = []
        closed_list = []

        start = Node(start,None,None)
        goal = Node(end,None,None)
        
        open_list.append(start)

        while len(open_list) > 0:

            open_list.sort()

            current = open_list.pop(0)

            closed_list.append(current)

            if current == goal:
                path = []
                while current != start:
                    path.append((current.pos,current.move))
                    current = current.parent
                return path[::-1]

            (x,y) = current.pos
            
            neighbours = [(x-1,y,"w"),(x+1,y,"s"),(x,y-1,"a"),(x,y+1,"d")]
            
            for next in neighbours:
                
                mapArray = str(map).split("\n")
                
                '''
                if mapArray[next[0]][next[1]] == '#':
                    continue
                '''

                neighbor = Node((next[0],next[1]),current,next[2])

                if neighbor in closed_list:
                    continue

                neighbor.g = abs(neighbor.pos[0] - start.pos[0]) + abs(neighbor.pos[1] - start.pos[1])
                neighbor.h = abs(neighbor.pos[0] - goal.pos[0]) + abs(neighbor.pos[1] - goal.pos[1])
                neighbor.f = neighbor.g + neighbor.h
                

                if (self.add_to_open(open_list,neighbor) == True):
                    open_list.append(neighbor)

        return None
        
    def add_to_open(self,open,neighbor):
        for node in open:
            if (neighbor == node and neighbor.f >= node.f):
                return False
        return True
