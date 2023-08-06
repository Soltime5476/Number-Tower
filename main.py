import pygame
from pygame.locals import K_ESCAPE
from utils import resize
from gameobjects import (
    Player, 
    Block, 
    SubTower, 
    LevelLayout,
    ALL_SPRITES,
    BLOCKS,
    CHARACTERS
)
from constants import (
    SCREEN,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SKY_BLUE,
    BLOCK_SIDE_LENGTH,
    PLAYER_INIT_POS,
    TOWER_CLEARED
)

def main():
    clock = pygame.time.Clock()
    pygame.display.set_caption('Number Tower')
    bg = resize(pygame.image.load('./assets/sky_bridge.png').convert(), scale=0.4)
    SCREEN.blit(bg, bg.get_rect())
    running = True
    paused = False
    shifting = False
    level_passed = False
    
    player = Player(PLAYER_INIT_POS)

    # Player starts in an empty block regardless of level layout
    starting_block = Block((5, SCREEN_HEIGHT - BLOCK_SIDE_LENGTH))

    layout = LevelLayout([2, 2, 3, 3, 4, 1], player, SCREEN)

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        if not shifting:
            for event in pygame.event.get(): 
                
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    for block in BLOCKS:
                        if block.rect.collidepoint(event.pos):
                            block.on_mouse_hover()
                        else:
                            block.on_mouse_leave()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for block in BLOCKS:
                        if block.rect.collidepoint(event.pos):
                            layout.teleport_player_to(block)

                elif event.type == pygame.KEYDOWN:   
                    if event.key == K_ESCAPE:
                        running = False   
                
                if event == TOWER_CLEARED:
                    if len(layout.queue) >= 5:
                        shifting = True
                        #ALL_SPRITES.camera_shift()
                    layout.queue.popleft()
                    if layout.queue:
                        layout.current_tower = layout.queue[0]  
                    else: 
                        level_passed = True    

                      
        # fill the screen with a color to wipe away anything from last frame
        #SCREEN.fill(SKY_BLUE)
        if shifting:
            for sprite in ALL_SPRITES:
                shifting = sprite.shift()
        SCREEN.blit(bg, bg.get_rect())        
        ALL_SPRITES.update()
        ALL_SPRITES.draw(SCREEN)
        
        #player.render_power()
        # RENDER YOUR GAME HERE
        #for character in CHARACTERS:
            #character.render_power()       
        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()


if __name__ == main():
    main()
