import pygame as pyg
import math
from Entity import Entity
from Constatns import *

class Bullet(Entity):
    def __init__(self, x, y, angle, speed):
        super().__init__(x, y, 5, CLR_RED)
        self.angle = angle
        self.speed = speed

        angle_radians = math.radians(angle)
        self.dx = math.cos(angle_radians) * speed
        self.dy = math.sin(angle_radians) * speed

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def is_off_screen(self) -> bool:
        return (
            self.x < self.radius
            or self.x > WIN_WIDTH
            or self.y < self.radius
            or self.y > WIN_HEIGHT
        )