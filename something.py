import pygame as pyg
import math
import random as rng

pyg.init()

WIN_WIDTH = 1000
WIN_HEIGHT = 500
WIN = pyg.display.set_mode((WIN_WIDTH,WIN_HEIGHT))

GAME_OVER_FONT = pyg.font.SysFont("consolas", 30)
UI_FONT = pyg.font.SysFont("consolas", 20)

CLR_WHITE = (255,255,255)
CLR_BLACK = (0,0,0)
CLR_RED = (255, 0, 0)
CLR_GREEN = (0, 255, 0)

WAVE_DELAY = 60 * 3 # num seconds per wave
BOOST_DELAY = 60 * 12

DEBUG = False

waveNum = 1
waveSpeed = 3
highscore = 1

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
        self.y = y
        self.radius = 7.5
    
    def draw(self, surface):
        pyg.draw.circle(surface,CLR_GREEN, (self.x, self.y), self.radius)
    
    def hit(self, player_rect):
        boost_rect = pyg.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        return boost_rect.colliderect(player_rect)

class Player:
    def __init__(self, contrtrolls: list[int], name:str) -> None:
        self.radius = 10
        # self.isAlive = True
        self.velocity = 5
        self.x = WIN_WIDTH / 2 - self.radius
        self.y = WIN_HEIGHT / 2 - self.radius
        self.controlls = contrtrolls
        self.isBoosted = False
        self.boostTimer = 0
        self.boostAmmount = 0
    
    def draw(self, surface):
        color: tuple[int]
        if self.isBoosted: color = CLR_GREEN
        else: color = CLR_WHITE
        
        pyg.draw.circle(surface, color, (self.x, self.y), self.radius)
        
    def getRect(self) -> pyg.Rect:
        return pyg.Rect((self.x - self.radius, self.y - self.radius),(self.radius * 2, self.radius * 2))
    
    def move(self,keysPressed):
        if self.isBoosted: self.velocity = 8
        else: self.velocity = 5
        
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
    
    def boost(self):
        self.boostTimer = 60 * 10
        self.isBoosted = True

PLAYERS: list[Player] = [Player([pyg.K_UP, pyg.K_DOWN, pyg.K_LEFT, pyg.K_RIGHT, pyg.K_LSHIFT], "player 1")]
players: list[Player] = PLAYERS.copy()
bullets:list[Bullet] = []
boosts:list[Boost] = []

def RefreshWindow():
    WIN.fill(CLR_BLACK)

    for bullet in bullets:
        bullet.draw(WIN)
    
    for boost in boosts:
        boost.draw(WIN)
    
    for player in players:
        player.draw(WIN)
        WIN.blit(UI_FONT.render("Boost: {} | {}".format(player.boostAmmount, player.boostTimer / 100), True, CLR_WHITE), (5,5))
    
    if DEBUG:
        text = UI_FONT.render("Bullet count: {}".format(len(bullets)), True, CLR_WHITE)
        size = text.get_size()
        WIN.blit(text, (WIN_WIDTH - 5 - size[0] ,5))
    
    text = UI_FONT.render("{} | {}".format(waveNum, highscore), True, CLR_WHITE)
    size = text.get_size()
    
    WIN.blit(text, (WIN_WIDTH / 2 - size[0] / 2 ,5))

    pyg.display.update()

def GameOver():
    WIN.fill(CLR_RED)
    text = GAME_OVER_FONT.render("GAME OVER - CLICK TO RESTART",True,CLR_WHITE)
    size = text.get_size()
    WIN.blit(text, (WIN_WIDTH//2 - size[0]//2, WIN_HEIGHT//2 - size[1]//2))
    pyg.display.update()

def Reset():
    global waveNum, waveSpeed, players
    
    bullets.clear()
    boosts.clear()
    players = PLAYERS.copy()
    waveNum = 1
    waveSpeed = 3
    for player in players:
        player.isBoosted = False
        player.boostTimer = 0
        player.boostAmmount = 0
    
    RefreshWindow()

    Game()
    
def Wave(speed:float):
    num = rng.randint(0,6)
    print(num)
    match (num):
        case 0: # wall L > R
            gapPos = rng.randint(0,40)
            gap = range(gapPos * 10, gapPos * 10 + 100)
            
            for i in range(0,500,10):
                if not i in gap: bullets.append(Bullet(5,i,0,speed))
        case 1: # wall R > L
            gapPos = rng.randint(0,40)
            gap = range(gapPos * 10, gapPos * 10 + 100)
            
            for i in range(0,500,10):
                if not i in gap: bullets.append(Bullet(WIN_WIDTH - 5,i,-180,speed))
        case 2: # wall T > B
            gapPos = rng.randint(0,80)
            gap = range(gapPos * 10, gapPos * 10 + 200)
            for i in range(0,1000,10):
                if not i in gap: bullets.append(Bullet(i,5,90,speed/2))
        case 3: # wall B > T
            gapPos = rng.randint(0,80)
            gap = range(gapPos * 10, gapPos * 10 + 200)
            for i in range(0,1000,10):
                if not i in gap: bullets.append(Bullet(i,WIN_HEIGHT - 5,-90,speed/2))
        case 4: # center spread
            for i in range(0, 360, 20):
                bullets.append(Bullet(WIN_WIDTH/2, WIN_HEIGHT/2, i, speed/3))
        case 5:
            for i in range(0, 90, 10):
                bullets.append(Bullet(5, 5, i, speed / 3))
        case 6:
            for i in range(-180,-90, 10):
                bullets.append(Bullet(WIN_WIDTH - 5, WIN_HEIGHT - 5, i, speed/3))

def BulletLogic():
    bullets_to_remove = []
    players_to_remove = []

    for bullet in bullets:
        for player in players:    
            if bullet.hit(player.getRect()):
                players_to_remove.append(player)
                
            bullet.move()
            if bullet.is_off_screen():
                bullets_to_remove.append(bullet)

    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)

    for player in players_to_remove:
        if player in players:
            players.remove(player)
            if  len(players) == 0: GameOver()

def WaveLogic():
    global waveSpeed, NextWaveFrameCounter, waveNum, highscore
    
    NextWaveFrameCounter -= 1
    if NextWaveFrameCounter == 0:
        NextWaveFrameCounter = WAVE_DELAY
        Wave(waveSpeed)
        waveSpeed += .5
        waveNum += 1
        if waveNum > highscore: highscore = waveNum

def BoostLogic():
    global NextBoostFrameCounter
    
    NextBoostFrameCounter -= 1
    if NextBoostFrameCounter == 0:
        NextBoostFrameCounter = BOOST_DELAY
        boosts.append(Boost(rng.randint(30,WIN_HEIGHT - 30), rng.randint(30,WIN_WIDTH - 30)))          

def main():
    global NextWaveFrameCounter, NextBoostFrameCounter, clock, target_fps

    # bullets.append(Bullet(30,30,0,0))
    
    NextWaveFrameCounter = WAVE_DELAY
    NextBoostFrameCounter = BOOST_DELAY
    clock = pyg.time.Clock()
    target_fps = 60
    RefreshWindow()
    Game()
    
def Game():
    running = True
    while running:    
        
        for event in pyg.event.get():
            match (event.type):
                case pyg.QUIT:
                    running = False
                case pyg.KEYDOWN:
                    for player in players:
                        if event.key == player.controlls[4] and player.boostAmmount > 0:
                            player.boostAmmount -= 1
                            player.boost()
                case pyg.MOUSEBUTTONDOWN:
                    if len(players) == 0: Reset()
                    
        WaveLogic()
        BoostLogic()

        if len(players) > 0: 
            for player in players:
                player.move(pyg.key.get_pressed())
                if player.boostTimer != 0: player.boostTimer -= 1
                else: player.isBoosted = False
                
            for boost in boosts:
                for player in players:
                    if boost.hit(player.getRect()):
                        boosts.remove(boost)
                        player.boostAmmount += 1
            
            BulletLogic()
            
            if len(players) > 0: RefreshWindow()
        clock.tick(target_fps)
    

if __name__ == "__main__":
    main()