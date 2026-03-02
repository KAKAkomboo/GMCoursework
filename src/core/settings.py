import pygame

pygame.init()

screen_resolutions = [(800, 600), (1024, 768), (1280, 720), (1540, 800), (1920, 1080)]
current_resolution_index = 3

screen_width, screen_height = screen_resolutions[current_resolution_index]
SCREEN = pygame.display.set_mode((screen_width, screen_height))

fps = 60

Black_color = (0, 0, 0)
White_color = (255, 255, 255)
Primary_color = (120, 58, 156)
Secondary_color = (51, 55, 84)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (140, 140, 140)
PURPLE = (160, 100, 220)

ASSETS_DIR = "../assets"
ICONS_DIR = ASSETS_DIR + "/images/icons"
FONTS_NAME = "arial"

Primary_font = pygame.font.SysFont("georgia", 24)

tile_size = 32

ENEMIES_ENABLED = False

NPC_SPEED = 1
NPC_DIALOG_DISTANCE = 100
DIALOG_BOX_COLOR = (50, 50, 50)
DIALOG_TEXT_COLOR = (255, 255, 255)

NPC_WANDER_RADIUS = 120
