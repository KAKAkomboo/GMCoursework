import pygame

pygame.init()

screen_width = 1540
screen_height = 800
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

ASSETS_DIR = "assets"
ICONS_DIR = ASSETS_DIR + "/images/icons"
FONTS_NAME = "arial"

Primary_font = pygame.font.SysFont("georgia", 40)

tile_size = 32

NPC_SPEED = 1
NPC_DIALOG_DISTANCE = 100
DIALOG_BOX_COLOR = (50, 50, 50)
DIALOG_TEXT_COLOR = (255, 255, 255)

NPC_WANDER_RADIUS = 120

# pygame.init()
# screen = pygame.display.set_mode((800, 600))
# pygame.display.set_caption("wefwef")
#
#
# font = pygame.font.SysFont("helveticaoblique", 40)
#
# text = font.render("ПРИВІТТ. HELLO", True, (255, 255, 255))
# text_rect = text.get_rect(center=(400, 300))
#
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#
#     screen.fill((0, 0, 0))
#     screen.blit(text, text_rect)
#     pygame.display.flip()
#
# pygame.quit()