import pygame as pyg

WIN_WIDTH = 1000
WIN_HEIGHT = 500
WIN = pyg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

pyg.font.init()
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