
# Module: tree_search
# 
# This module provides a set o classes for automated
# problem solving through tree search:
#    SearchDomain  - problem domains
#    SearchProblem - concrete problems to be solved
#    SearchNode    - search tree nodes
#    SearchTree    - search tree with the necessary methods for searhing
#
#  (c) Luis Seabra Lopes
#  Introducao a Inteligencia Artificial, 2012-2019,
#  Inteligência Artificial, 2014-2019

from abc import ABC, abstractmethod

import asyncio

# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal
    def goal_test(self, state):
        return self.domain.satisfies(state,self.goal)

# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self,state,parent,depth=0, cost=0, heuristic = 0, action=None): 
        self.state = state
        self.parent = parent
        self.depth = depth
        self.cost = cost
        self.heuristic = heuristic
        self.action = action

    def in_upper_family(self, state):
        """ Tells is state is in the upper family of current node (parent, grandparent, ...)
        --- Parameters
        state       str         state to test for family relationship
        --- Returns
        inFamily    boolean     has upper family relationship
        """
        if self.parent == None:
            return False
        elif self.parent.state == state:
            return True
        return self.parent.in_upper_family(state)

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + "," + str(self.depth) + ")"
    
    def __repr__(self):
        return str(self)

# Arvores de pesquisa
class SearchTree:

    # construtor
    def __init__(self,problem, strategy='breadth'): 
        self.problem = problem
        # Ex11 Add heuristic distance from initial state to goal
        root = SearchNode(problem.initial, None, heuristic=problem.domain.heuristic(problem.initial, problem.goal))
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.length = 0
        self.terminals = 1
        self.non_terminals = 0
        self.avg_branching = 0
        self.cost = 0
        self.nodesWithGreaterCost = []
        self.avg_depth = 0 # TODO (?)

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return(path)

    def get_plan(self,node):
        if node.parent == None:
            return []
        plan = self.get_plan(node.parent)
        plan += [node.action]
        return(plan)

    @property
    def plan(self):
        return self.get_plan(self.solution)

    # procurar a solucao
    async def search(self, limit=None):
        while self.open_nodes != []:

            await asyncio.sleep(0)

            node = self.open_nodes.pop(0)
            print("\n",node.state)
            # Ex15 Check if node has the greatest cost
            # It has greater cost than all the others?
            if len(self.nodesWithGreaterCost)==0 or all([node.cost > n.cost for n in self.nodesWithGreaterCost]):
                self.nodesWithGreaterCost = [node]
            # It has the same cost as the others?
            elif all([node.cost == n.cost for n in self.nodesWithGreaterCost]):
                self.nodesWithGreaterCost.append(node)
            # Check if node solves problem
            if self.problem.goal_test(node.state):
                self.solution = node
                # Ex5 Register number of terminal nodes
                self.terminals = len(self.open_nodes) + 1 # Nó solução é terminal, por isso +1
                # Ex6 Ramification factor
                self.avg_branching = (self.terminals + self.non_terminals - 1) / self.non_terminals
                # Ex3 Register length of the solution found
                self.length = node.depth
                # Ex9 Register tree total cost
                self.cost = node.cost
                return self.get_path(node)
            # Ex5 Register number of non terminal nodes
            self.non_terminals += 1
            lnewnodes = []
            #print("\nStudying node ", node.state)
            #print("Actions available are...")
            for a in self.problem.domain.actions(node.state):
                newstate = self.problem.domain.result(node.state,a)
                # Ex1 Avoid cycles (don't visit states already visited) 
                # Ex4 Depth search with limit (newnode.depth = node.depth + 1 <= limit)
                if not node.in_upper_family(newstate) and (limit is None or node.depth < limit):
                    # Ex2 Add depth attr to search nodes
                    # Ex 8 Add cost (from root to self) attr to node 
                    # Ex11 Add heuristic distance from newnode to goal
                    #print("Action", a)
                    #print("New state would be", newstate)
                    newnode = SearchNode(newstate,node,node.depth+1,node.cost + self.problem.domain.cost(node.state, a), self.problem.domain.heuristic(newstate, self.problem.goal), a)
                    lnewnodes.append(newnode)
            self.add_to_open(lnewnodes)
        return None

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'uniform':
            self.open_nodes.extend(lnewnodes)
            # Ex10 Put nodes with less cost first
            self.open_nodes.sort(key=lambda node: node.cost)
        elif self.strategy == 'greedy':
            self.open_nodes.extend(lnewnodes)
            # Ex13 Put nodes with less heuristic
            self.open_nodes.sort(key=lambda node: node.heuristic)
        elif self.strategy == 'a*':
            self.open_nodes.extend(lnewnodes)
            # Ex14 Search a*
            self.open_nodes.sort(key=lambda node: node.cost + node.heuristic)
            # Fazemos só soma pq cost e heuristic estão na mesma unidade (km)
            # Caso contrário teríamos de converter