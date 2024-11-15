
# build with: pyinstaller --onefile --windowed Main.py

from tkinter import Tk, messagebox
import sys
import os
import math
import random as rng

try:
    import pygame as pyg
except ImportError:
    root = Tk()
    root.withdraw()
    if messagebox.askokcancel("Pygame not installed", "install pygame?"):
        os.system("pip install pygame")
    else:
        sys.exit()
    
import pygame as pyg

from Entity import Entity
from Eraser import Eraser
from Player import Player
from Bullet import Bullet
from Boost import Boost
from Constatns import *

pyg.init()

waveNum = 1
waveSpeed = 3
highscore = 1

isPaused = False

boostCount = 0
bulletCount = 0
playerCount = 0
eraserCount = 0


PLAYERS: list[Player] = [
    Player([pyg.K_w, pyg.K_s, pyg.K_a, pyg.K_d, pyg.K_LSHIFT], "player 1")
]

emptyIcon = pyg.Surface((1, 1))
emptyIcon.fill(CLR_WHITE)
pyg.display.set_icon(emptyIcon)
pyg.display.set_caption("")

entities: list[Entity] = []
entities.append(*PLAYERS)
playerCount = len(PLAYERS)

def SaveHiScore():
    with open("save.bin", "w+") as f:
        f.write(bin(highscore))

def LoadHiScore():
    global highscore
    
    try:
        with open("save.bin", "r") as f:
            highscore = int(f.read(), 2)
    except FileNotFoundError:
        highscore = 0

def RefreshWindow():
    WIN.fill(CLR_BLACK)
    for object in entities:
        object.draw(WIN)
        if isinstance(object, Player):
            WIN.blit(
                SMALL_FONT.render(
                    "Boost: {} | {}".format(object.boostAmmount, object.boostTimer / 100),
                    True,
                    CLR_WHITE,
                    ),
                (5, 5),
            )
        
        if DEBUG:
            pyg.draw.rect(WIN, CLR_BLUE, object.getRect(), 1)
        

    if DEBUG:
        text = SMALL_FONT.render(
            "Bullet count: {}".format(bulletCount), True, CLR_WHITE
        )
        size = text.get_size()
        WIN.blit(text, (WIN_WIDTH - 5 - size[0], 5))

    text = SMALL_FONT.render("{} | {}".format(waveNum, highscore), True, CLR_WHITE)
    size = text.get_size()
    WIN.blit(text, (WIN_WIDTH / 2 - size[0] / 2, 5))

    if isPaused:
        pauseOverlay = pyg.Surface((WIN_WIDTH, WIN_HEIGHT))
        pauseOverlay.set_alpha(128)
        pauseOverlay.fill(CLR_GRAY)
        pauseText = BIG_FONT.render("PAUSED", True, CLR_WHITE)
        pauseOverlay.blit(
            pauseText,
            (
                WIN_WIDTH / 2 - pauseText.get_size()[0] / 2,
                WIN_HEIGHT / 2 - pauseText.get_size()[1] / 2,
            ),
        )
        WIN.blit(pauseOverlay, (0, 0))

    pyg.display.update()

def GameOver():
    WIN.fill(CLR_RED)
    text = BIG_FONT.render("GAME OVER - SPACE TO RESTART", True, CLR_WHITE)
    size = text.get_size()
    WIN.blit(text, (WIN_WIDTH // 2 - size[0] // 2, WIN_HEIGHT // 2 - size[1] // 2))
    pyg.display.update()

def Reset():
    global waveNum, waveSpeed, playerCount
    
    entities.clear()
    entities.append(*PLAYERS)
    playerCount = len(PLAYERS)
    waveNum = 1
    waveSpeed = 3
    for player in entities:
        if not isinstance(player, Player): continue
        player.isBoosted = False
        player.boostTimer = 0
        player.boostAmmount = 0
        player.x = WIN_WIDTH / 2
        player.y = WIN_HEIGHT / 2

    RefreshWindow()

    Game()

def Wave(speed: float):
    global bulletCount
    
    num = rng.randint(0, 8)
    if DEBUG:
        print(num)
    match (num):
        case 0:  # wall L > R
            gapPos = rng.randint(0, 40)
            gap = range(gapPos * 10, gapPos * 10 + 100)

            for i in range(0, 500, 10):
                if not i in gap:
                    bullet = Bullet(5, i, 0, speed)
                    entities.append(bullet)
                    bulletCount += 1
        case 1:  # wall R > L
            gapPos = rng.randint(0, 40)
            gap = range(gapPos * 10, gapPos * 10 + 100)

            for i in range(0, 500, 10):
                if not i in gap:
                    bullet = Bullet(WIN_WIDTH - 5, i, -180, speed)
                    entities.append(bullet)
                    bulletCount += 1
        case 2:  # wall T > B
            gapPos = rng.randint(0, 80)
            gap = range(gapPos * 10, gapPos * 10 + 200)
            for i in range(0, 1000, 10):
                if not i in gap:
                    bullet = Bullet(i, 5, 90, speed / 2)
                    entities.append(bullet)
                    bulletCount += 1
        case 3:  # wall B > T
            gapPos = rng.randint(0, 80)
            gap = range(gapPos * 10, gapPos * 10 + 200)
            for i in range(0, 1000, 10):
                if not i in gap:
                    bullet = Bullet(i, WIN_HEIGHT - 5, -90, speed / 2)
                    entities.append(bullet)
                    bulletCount += 1
        case 4:  # center spread
            for i in range(0, 360, 20):
                bullet = Bullet(WIN_WIDTH / 2, WIN_HEIGHT / 2, i, speed / 3)
                entities.append(bullet)
                bulletCount += 1
        case 5:  # spread from upper-left corner
            for i in range(-45, 90, 10):
                bullet = Bullet(5, 5, i, speed / 3)
                entities.append(bullet)
                bulletCount += 1
        case 6:  # spread from bottom-right corner
            for i in range(-180, -45, 10):
                bullet = Bullet(WIN_WIDTH - 5, WIN_HEIGHT - 5, i, speed / 3)
                entities.append(bullet)
                bulletCount += 1
        case 7:  # spread from top-right corner
            for i in range(90, 225, 10):
                bullet = Bullet(WIN_WIDTH - 5, 5, i, speed / 3)
                entities.append(bullet)
                bulletCount += 1
        case 8:  # spread from bottom-left corner
            for i in range(-90, 45, 10):
                bullet = Bullet(5, WIN_HEIGHT - 5, i, speed / 3)
                entities.append(bullet)
                bulletCount += 1

def BulletLogic():
    global bulletCount, playerCount
    
    bullets_to_remove = []
    players_to_remove = []

    for bullet in entities:
        if not isinstance(bullet, Bullet):
            continue
        for player in entities:
            if not isinstance(player, Player):
                continue
            if bullet.hit(player.getRect()):
                players_to_remove.append(player)

        bullet.move()
        if bullet.is_off_screen():
            bullets_to_remove.append(bullet)

    for bullet in bullets_to_remove:
        if bullet in entities:
            entities.remove(bullet)
            bulletCount -= 1

    for player in players_to_remove:
        if player in entities:
            entities.remove(player)
            playerCount -= 1
        if playerCount == 0:
            GameOver()

def WaveLogic():
    global waveSpeed, NextWaveFrameCounter, waveNum, highscore

    NextWaveFrameCounter -= 1
    if NextWaveFrameCounter == 0:
        NextWaveFrameCounter = WAVE_DELAY
        Wave(waveSpeed)
        waveSpeed += 0.5
        waveNum += 1
        if waveNum > highscore:
            highscore = waveNum
        SaveHiScore()

def BoostLogic():
    global NextBoostFrameCounter

    NextBoostFrameCounter -= 1
    if NextBoostFrameCounter == 0:
        NextBoostFrameCounter = BOOST_DELAY
        boost = Boost(rng.randint(30, WIN_WIDTH - 30), rng.randint(30, WIN_HEIGHT - 30))
        entities.append(boost)

def EraserLogic(): ...

def main():
    global NextWaveFrameCounter, NextBoostFrameCounter, clock, targetFps

    LoadHiScore()
    NextWaveFrameCounter = WAVE_DELAY
    NextBoostFrameCounter = BOOST_DELAY
    clock = pyg.time.Clock()
    targetFps = 60
    RefreshWindow()
    Game()

def Game():
    global isPaused, boostCount

    running = True
    while running:

        clock.tick(targetFps)
        if playerCount > 0:
            RefreshWindow()

        for event in pyg.event.get():
            match (event.type):
                case pyg.QUIT:
                    running = False
                case pyg.KEYDOWN:
                    if event.key == pyg.K_DELETE:
                        return
                    if event.key == pyg.K_ESCAPE:
                        isPaused = not isPaused
                    if event.key == pyg.K_SPACE and playerCount == 0:
                        Reset()
                    for player in entities:
                        if not isinstance(player, Player): continue
                        if event.key == player.controls[4] and player.boostAmmount > 0:
                            player.boostAmmount -= 1
                            player.boost()
        if not isPaused:
            WaveLogic()
            BoostLogic()
            BulletLogic()

            if playerCount > 0:
                for player in entities:
                    if not isinstance(player, Player): continue
                    player.move(pyg.key.get_pressed())
                    if player.boostTimer != 0:
                        player.boostTimer -= 1
                    else:
                        player.isBoosted = False

                for boost in entities:
                    if not isinstance(boost, Boost): continue
                    for player in entities:
                        if not isinstance(player, Player): continue
                        if boost.hit(player.getRect()):
                            entities.remove(boost)
                            boostCount -= 1
                            player.boostAmmount += 1

if __name__ == "__main__":
    main()
