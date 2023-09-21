import pygame

SCREEN_WIDTH = 1536
SCREEN_HEIGHT = 864
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
CHARACTER_WIDTH = 70
CHARACTER_HEIGHT = 90
BLOCK_SIDE_WIDTH = 240
BLOCK_SIDE_LENGTH = 180
BLOCK_PADDING = 15
CAMERA_OFFSET = BLOCK_SIDE_WIDTH + 80
FONT_SIZE = CHARACTER_WIDTH // 3
AURORA_FONT = pygame.font.Font('./assets/fonts/Aurora.ttf', size = 50)
HEADLINER_FONT = pygame.font.Font('./assets/fonts/HeadlinerNo45.ttf', size = 30)
POWER_FONT = pygame.font.SysFont("Times New Roman", FONT_SIZE)
POWER_HEIGHT = FONT_SIZE + 10
PLAYER_INIT_POS = (25, SCREEN_HEIGHT - CHARACTER_HEIGHT - POWER_HEIGHT - BLOCK_PADDING)
TRANSPARENT = (0, 0, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
SKY_BLUE = (135, 206, 235)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLOOD = (138, 3, 3)

# Events
BLOCK_CLEARED = pygame.event.Event(pygame.USEREVENT + 1)
TOWER_CLEARED = pygame.event.Event(pygame.USEREVENT + 2) 
PLAYER_WIN = pygame.event.Event(pygame.USEREVENT + 3)
GAME_OVER = pygame.event.Event(pygame.USEREVENT + 4)
BLINK_EVENT = pygame.event.Event(pygame.USEREVENT + 5)









