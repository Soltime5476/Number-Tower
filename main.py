import pygame

pygame.init()

from pygame.locals import K_ESCAPE
from gameobjects import (
    LEVEL_SPRITES,
    Roof,
    BLOCKS,
    ENEMIES
)
from scenes import IntroScene
from constants import *

def main():
    clock = pygame.time.Clock()
    pygame.display.set_caption('Number Tower')
    
    running = True

    current_scene = IntroScene()

    while running:
        
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():    
            if event.type == pygame.QUIT:
                    running = False                 
            if event.type == pygame.KEYDOWN:   
                if event.key == K_ESCAPE:
                    running = False            
            current_scene.handle_events(event)
        
        # RENDER YOUR GAME HERE
        current_scene.render() 
        
        # flip() the display to put your work on screen
        pygame.display.flip()
        
        current_scene = current_scene.next
   
        clock.tick(60)  # limits FPS to 60

    pygame.quit()

if __name__ == main():
    main()
