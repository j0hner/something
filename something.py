import pygame as pyg
import math
import random as rng

pyg.init()

WIN_WIDTH = 1000
WIN_HEIGHT = 500
WIN = pyg.display.set_mode((WIN_WIDTH,WIN_HEIGHT))

FONT = pyg.font.SysFont("consolas",30)

CLR_WHITE = (255,255,255)
CLR_BLACK = (0,0,0)
CLR_RED = (255, 0, 0)
CLR_GREEN = (0, 255, 0)

WAVE_DELAY = 60 * 4 # num seconds per wave
BOOST_DELAY = 60 * 12

# rectX = WIN_WIDTH // 2
# rectY = WIN_HEIGHT // 2
# rectWidth = 20
# rectHeight = 20
# isAlive = True
waveNum = 1
waveSpeed = 3
# playerVel = 5


class Bullet:
    def __init__(self, x, y, angle, speed):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.radius = 5
        
        angle_radians = math.radians(angle)
        self.dx = math.cos(angle_radians) * speed
        self.dy = math.sin(angle_radians) * speed

    def move(self):
        
        self.x += self.dx
        self.y += self.dy

    def draw(self, surface):
        pyg.draw.circle(surface, CLR_RED, (int(self.x), int(self.y)), self.radius)

    def is_off_screen(self) -> bool:
        return self.x < self.radius or self.x > WIN_WIDTH or self.y < self.radius or self.y > WIN_HEIGHT
    
    def hit(self, player_rect):
        bullet_rect = pyg.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        return bullet_rect.colliderect(player_rect)

class Boost:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = self.radius = 7.5
    
    def draw(self, surface):
        pyg.draw.circle(surface,CLR_GREEN, (self.x, self.y), self.radius)
    
    def hit(self, player_rect):
        boost_rect = pyg.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        return boost_rect.colliderect(player_rect)

class Player:
    def __init__(self, contrtrolls: list[int]) -> None:
        self.radius = 10
        # self.isAlive = True
        self.velocity = 5
        self.x = WIN_WIDTH / 2 - self.radius
        self.y = WIN_HEIGHT / 2 - self.radius
        self.controlls = contrtrolls
    
    def draw(self, surface):
        pyg.draw.circle(surface, CLR_WHITE, (self.x, self.y), self.radius)
        
    def getRect(self) -> pyg.Rect:
        return pyg.Rect((self.x - self.radius, self.y - self.radius),(self.radius * 2, self.radius * 2))
    
    def move(self,keysPressed):
        move_x = keysPressed[self.controlls[3]] - keysPressed[self.controlls[2]]
        move_y = keysPressed[self.controlls[1]] - keysPressed[self.controlls[0]]
        
        if move_x != 0 and move_y != 0:
            move_x *= self.velocity / math.sqrt(2)
            move_y *= self.velocity / math.sqrt(2)
        else:
            move_x *= self.velocity
            move_y *= self.velocity

        self.x = min(max(0, self.x + move_x), WIN_WIDTH - self.radius)
        self.y = min(max(0, self.y + move_y), WIN_HEIGHT - self.radius)

PLAYERS: list[Player] = [Player([pyg.K_UP, pyg.K_DOWN, pyg.K_LEFT, pyg.K_RIGHT]), Player([pyg.K_w, pyg.K_s, pyg.K_a, pyg.K_d])]
players: list[Player] = PLAYERS
bullets:list[Bullet] = []
boosts:list[Boost] = []

def RefreshWindow():
    WIN.fill(CLR_BLACK)
    
    for player in players:
        player.draw(WIN)

    for bullet in bullets:
        bullet.draw(WIN)
    
    for boost in boosts:
        boost.draw(WIN)
    
    pyg.display.update()

def GameOver():
    WIN.fill(CLR_RED)
    text = FONT.render("GAME OVER - CLICK TO RESTART",True,CLR_WHITE)
    size = text.get_size()
    WIN.blit(text, (WIN_WIDTH//2 - size[0]//2, WIN_HEIGHT//2 - size[1]//2))
    pyg.display.update()

def Reset():
    global waveNum, waveSpeed, players
    
    bullets.clear()
    boosts.clear()
    players = PLAYERS
    waveNum = 1
    waveSpeed = 3

    main()
    
def Wave(speed:float):
    match (rng.randint(0,6)):
        case 0:
            gapPos = rng.randint(0,40)
            gap = range(gapPos * 10, gapPos * 10 + 100)
            
            for i in range(0,500,10):
                if not i in gap: bullets.append(Bullet(0,i,0,speed))
        case 1:
            gapPos = rng.randint(0,40)
            gap = range(gapPos * 10, gapPos * 10 + 100)
            
            for i in range(0,500,10):
                if not i in gap: bullets.append(Bullet(WIN_WIDTH,i,-180,speed))
        case 2:
            gapPos = rng.randint(0,80)
            gap = range(gapPos * 10, gapPos * 10 + 200)
            for i in range(0,1000,10):
                if not i in gap: bullets.append(Bullet(i,0,90,speed/2))
        case 3:
            gapPos = rng.randint(0,80)
            gap = range(gapPos * 10, gapPos * 10 + 200)
            for i in range(0,1000,10):
                if not i in gap: bullets.append(Bullet(i,WIN_HEIGHT,-90,speed/2))
        case 4:
            for i in range(0, 360, 20):
                bullets.append(Bullet(WIN_WIDTH/2 - 5, WIN_HEIGHT/2 -5, i, speed/3))
        case 5:
            for i in range(0,90, 10):
                bullets.append(Bullet(0,0, i,speed/3))
        case 6:
            for i in range(-180,-90, 10):
                bullets.append(Bullet(WIN_WIDTH, WIN_HEIGHT, i, speed/3))

def BulletLogic():
    bullets_to_remove = []
    players_to_remove = []

    for bullet in bullets:
        for player in players:    
            if bullet.hit(player.getRect()):
                players_to_remove.append(player)
                if len(players_to_remove) == len(players):
                    GameOver()

            bullet.move()
            if bullet.is_off_screen():
                bullets_to_remove.append(bullet)

    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)

    for player in players_to_remove:
        if player in players:
            players.remove(player)

def WaveLogic():
    global waveSpeed, NextWaveFrameCounter
    
    NextWaveFrameCounter -= 1
    if NextWaveFrameCounter == 0:
        NextWaveFrameCounter = WAVE_DELAY
        Wave(waveSpeed)
        waveSpeed += .5

def BoostLogic():
    global NextBoostFrameCounter
    
    NextBoostFrameCounter -= 1
    if NextBoostFrameCounter == 0:
        NextBoostFrameCounter = BOOST_DELAY
        boosts.append(Boost(rng.randint(30,WIN_HEIGHT - 30), rng.randint(30,WIN_WIDTH - 30)))

def main():
    global rectX, rectY, NextWaveFrameCounter, NextBoostFrameCounter

    # bullets.append(Bullet(30,30,0,0))
    
    NextWaveFrameCounter = WAVE_DELAY
    NextBoostFrameCounter = BOOST_DELAY
    running = True

    clock = pyg.time.Clock()
    target_fps = 60
    RefreshWindow()
    
    while running:    
        
        for event in pyg.event.get():
            match (event.type):
                case pyg.QUIT:
                    running = False
                case pyg.MOUSEBUTTONDOWN:
                    if len(players) == 0: Reset()
                    
        WaveLogic()
        BoostLogic()

        if len(players) > 0: 
            for player in players:
                player.move(pyg.key.get_pressed())
            
            BulletLogic()
            
            if len(players) > 0: RefreshWindow()
        clock.tick(target_fps)

if __name__ == "__main__":
    main()