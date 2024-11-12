from Entity import Entity
import math
from Constatns import *

class Player(Entity):
    def __init__(self, controls: list[int], name: str):
        self.color = CLR_WHITE
        super().__init__(WIN_WIDTH / 2, WIN_HEIGHT / 2, 10, self.color)
        self.velocity = 5
        self.controls = controls
        self.isBoosted = False
        self.boostTimer = 0
        self.boostAmmount = 0

    def draw(self, surface):
        self.color = CLR_GREEN if self.isBoosted else CLR_WHITE
        super().draw(surface)

    def move(self, keysPressed):
        if not self.isBoosted:
            self.velocity = 5

        move_x = keysPressed[self.controls[3]] - keysPressed[self.controls[2]]
        move_y = keysPressed[self.controls[1]] - keysPressed[self.controls[0]]

        if move_x != 0 and move_y != 0:
            move_x *= self.velocity / math.sqrt(2)
            move_y *= self.velocity / math.sqrt(2)
        else:
            move_x *= self.velocity
            move_y *= self.velocity

        self.x = min(max(0, self.x + move_x), WIN_WIDTH)
        self.y = min(max(0, self.y + move_y), WIN_HEIGHT)

    def boost(self):
        self.boostTimer = 60 * 10
        self.isBoosted = True
        self.velocity += 3
