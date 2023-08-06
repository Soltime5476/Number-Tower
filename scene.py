import pygame

class Background():
    def __init__(self):
        super().__init__()
        self.bg_image = pygame.image.load('Background').convert()
