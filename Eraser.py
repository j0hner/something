import pygame as pyg
import random as rng
from Entity import *

class Eraser(Entity):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.active = False
        self.warnFrames = 60 * 3
        self.activeFrames = 60 * 1
        self.alpha = 122

    def tryActivate(self):
        if not self.active:
            self.active = rng.randint(0, 9) == 0

    def advanceActive(self):
        if not self.active:
            return

        if self.warnFrames > 0:
            self.warnFrames -= 1

    def draw(self, surface, color):
        alpha = 255 if self.active else 128
        return pyg.draw.circle(surface, color + (alpha), self.x, self.y, self.radius)

    def hit(self, collisionRect):
        if self.active:
            return super().hit(collisionRect)
        return False