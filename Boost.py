from Entity import Entity
from Constatns import *

class Boost(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 7.5, CLR_GREEN)
