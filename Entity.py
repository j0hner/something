import pygame as pyg

class Entity:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def getRect(self) -> pyg.Rect:
        return pyg.Rect(
            (self.x - self.radius, self.y - self.radius),
            (self.radius * 2, self.radius * 2),
        )

    def draw(self, surface):
        pyg.draw.circle(surface, self.color, (self.x, self.y), self.radius)

    def hit(self, collisionRect):
        return self.getRect().colliderect(collisionRect)