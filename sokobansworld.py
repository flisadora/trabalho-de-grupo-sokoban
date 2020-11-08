import time
from strips import *


# Sokobans world predicates

class BoxHoverDiamond(Predicate):
    def __init__(self,box, diamond):
        self.args = [box, diamond]

class BoxFree(Predicate):
    def __init__(self,box):
        self.args = [box]

class DiamondFree(Predicate):
    def __init__(self,diamond):
        self.args = [diamond]

# Sokobans world operators

B='Box'
D='Diamond'

class PushHover(Operator):
    args = [B,D]
    pc   = [DiamondFree(D),BoxFree(B)]
    neg  = [DiamondFree(D),BoxFree(B)]
    pos  = [BoxHoverDiamond(B,D)]

class PushOut(Operator):
    args = [B,D]
    pc   = [BoxHoverDiamond(B,D)]
    neg  = [BoxHoverDiamond(B,D)]
    pos  = [DiamondFree(D),BoxFree(B)]
    
initial_state = []