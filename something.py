import pygame as pyg
import math
import random as rng

pyg.init()

WIN_WIDTH = 1000
WIN_HEIGHT = 500
WIN = pyg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

BIG_FONT = pyg.font.SysFont("consolas", 30)
SMALL_FONT = pyg.font.SysFont("consolas", 20)

CLR_WHITE = (255, 255, 255)
CLR_BLACK = (0, 0, 0)
CLR_RED = (255, 0, 0)
CLR_GREEN = (0, 255, 0)
CLR_BLUE = (0, 0, 255)
CLR_GRAY = (60, 60, 60)

WAVE_DELAY = 60 * 3  # num seconds per wave
BOOST_DELAY = 60 * 3

DEBUG = False

waveNum = 1
waveSpeed = 3
highscore = 1

isPaused = False

boostCount = 0
bulletCount = 0
playerCount = 0
eraserCount = 0


emptyIcon = pyg.Surface((1, 1))
emptyIcon.fill(CLR_WHITE)
pyg.display.set_icon(emptyIcon)
pyg.display.set_caption("")


class GameObject:
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


class Eraser(GameObject):
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


class Bullet(GameObject):
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


class Boost(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 7.5, CLR_GREEN)


class Player(GameObject):
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


PLAYERS: list[Player] = [
    Player([pyg.K_UP, pyg.K_DOWN, pyg.K_LEFT, pyg.K_RIGHT, pyg.K_LSHIFT], "player 1")
]

gameObjects: list[GameObject] = []
gameObjects.append(*PLAYERS.copy())
playerCount = len(PLAYERS)

def RefreshWindow():
    WIN.fill(CLR_BLACK)
    for object in gameObjects:
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
    
    gameObjects.clear()
    gameObjects.append(*PLAYERS)
    playerCount = len(PLAYERS)
    waveNum = 1
    waveSpeed = 3
    for player in gameObjects:
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
                    gameObjects.append(bullet)
                    bulletCount += 1
        case 1:  # wall R > L
            gapPos = rng.randint(0, 40)
            gap = range(gapPos * 10, gapPos * 10 + 100)

            for i in range(0, 500, 10):
                if not i in gap:
                    bullet = Bullet(WIN_WIDTH - 5, i, -180, speed)
                    gameObjects.append(bullet)
                    bulletCount += 1
        case 2:  # wall T > B
            gapPos = rng.randint(0, 80)
            gap = range(gapPos * 10, gapPos * 10 + 200)
            for i in range(0, 1000, 10):
                if not i in gap:
                    bullet = Bullet(i, 5, 90, speed / 2)
                    gameObjects.append(bullet)
                    bulletCount += 1
        case 3:  # wall B > T
            gapPos = rng.randint(0, 80)
            gap = range(gapPos * 10, gapPos * 10 + 200)
            for i in range(0, 1000, 10):
                if not i in gap:
                    bullet = Bullet(i, WIN_HEIGHT - 5, -90, speed / 2)
                    gameObjects.append(bullet)
                    bulletCount += 1
        case 4:  # center spread
            for i in range(0, 360, 20):
                bullet = Bullet(WIN_WIDTH / 2, WIN_HEIGHT / 2, i, speed / 3)
                gameObjects.append(bullet)
                bulletCount += 1
        case 5:  # spread from upper-left corner
            for i in range(-45, 90, 10):
                bullet = Bullet(5, 5, i, speed / 3)
                gameObjects.append(bullet)
                bulletCount += 1
        case 6:  # spread from bottom-right corner
            for i in range(-180, -45, 10):
                bullet = Bullet(WIN_WIDTH - 5, WIN_HEIGHT - 5, i, speed / 3)
                gameObjects.append(bullet)
                bulletCount += 1
        case 7:  # spread from top-right corner
            for i in range(90, 225, 10):
                bullet = Bullet(WIN_WIDTH - 5, 5, i, speed / 3)
                gameObjects.append(bullet)
                bulletCount += 1
        case 8:  # spread from bottom-left corner
            for i in range(-90, 45, 10):
                bullet = Bullet(5, WIN_HEIGHT - 5, i, speed / 3)
                gameObjects.append(bullet)
                bulletCount += 1

def BulletLogic():
    global bulletCount, playerCount
    
    bullets_to_remove = []
    players_to_remove = []

    for bullet in gameObjects:
        if not isinstance(bullet, Bullet):
            continue
        for player in gameObjects:
            if not isinstance(player, Player):
                continue
            if bullet.hit(player.getRect()):
                players_to_remove.append(player)

        bullet.move()
        if bullet.is_off_screen():
            bullets_to_remove.append(bullet)

    for bullet in bullets_to_remove:
        if bullet in gameObjects:
            gameObjects.remove(bullet)
            bulletCount -= 1

    for player in players_to_remove:
        if player in gameObjects:
            gameObjects.remove(player)
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


def BoostLogic():
    global NextBoostFrameCounter

    NextBoostFrameCounter -= 1
    if NextBoostFrameCounter == 0:
        NextBoostFrameCounter = BOOST_DELAY
        boost = Boost(rng.randint(30, WIN_WIDTH - 30), rng.randint(30, WIN_HEIGHT - 30))
        gameObjects.append(boost)


def EraserLogic(): ...

def main():
    global NextWaveFrameCounter, NextBoostFrameCounter, clock, targetFps

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
                    for player in gameObjects:
                        if not isinstance(player, Player): continue
                        if event.key == player.controls[4] and player.boostAmmount > 0:
                            player.boostAmmount -= 1
                            player.boost()
        if not isPaused:
            WaveLogic()
            BoostLogic()
            BulletLogic()

            if playerCount > 0:
                for player in gameObjects:
                    if not isinstance(player, Player): continue
                    player.move(pyg.key.get_pressed())
                    if player.boostTimer != 0:
                        player.boostTimer -= 1
                    else:
                        player.isBoosted = False

                for boost in gameObjects:
                    if not isinstance(boost, Boost): continue
                    for player in gameObjects:
                        if not isinstance(player, Player): continue
                        if boost.hit(player.getRect()):
                            gameObjects.remove(boost)
                            boostCount -= 1
                            player.boostAmmount += 1


if __name__ == "__main__":
    main()
