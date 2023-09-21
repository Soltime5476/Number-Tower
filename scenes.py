import pygame
import pygame.mixer
import random
from pygame.locals import KEYDOWN, MOUSEBUTTONDOWN
from constants import *
from gameobjects import (
    GameObjects,
    Player,
    Enemy,
    Block,
    SubTower,
    BLOCKS,
    ENEMIES,
    LEVEL_SPRITES
)
from itertools import cycle
from typing import Deque, List, Self
from collections import deque
from abc import ABC, abstractmethod
from utils import resize

class BaseScene(ABC):
    bg_image: pygame.Surface = None

    def __init__(self) -> None:
        self.next = self

    @abstractmethod 
    def handle_events(self, event: pygame.event.Event) -> None:
        pass

    @abstractmethod
    def render(self) -> None:
        pass

    def switch_scene_to(self, next_scene: Self) -> Self:
        self.next = next_scene
        return next_scene

class IntroScene(BaseScene):
    bg_image = resize(pygame.image.load('./assets/backgrounds/IntroScene.png').convert(), scale=3.2)
    title_text = AURORA_FONT.render('Number Tower', 1, BLACK)
    start_text_on = HEADLINER_FONT.render('CLICK OR PRESS ANY KEY TO START GAME', 1, WHITE)
    start_text_off = pygame.Surface(start_text_on.get_rect().size)
    start_text_off.set_colorkey(BLACK)
    blink_surf = cycle([start_text_on, start_text_off])
    blinking_text = start_text_on

    def __init__(self) -> None:
        pygame.time.set_timer(BLINK_EVENT, 1000)
        super(IntroScene, self).__init__()
                
    def handle_events(self, event: pygame.event.Event) -> None:
        if event.type in (KEYDOWN, MOUSEBUTTONDOWN):
            self.switch_scene_to(LevelScene([2, 2, 3, 3, 4, 1]))
        if event == BLINK_EVENT:
            self.blinking_text = next(self.blink_surf)    
        
    def render(self) -> None:    
        SCREEN.blit(self.bg_image, (0, 0)) 
        SCREEN.blit(self.title_text, ((SCREEN_WIDTH - self.title_text.get_width()) / 2, 250))
        SCREEN.blit(self.blinking_text, ((SCREEN_WIDTH - self.start_text_on.get_width()) / 2, 375))

class LevelScene(BaseScene):
    """
    Represents the whole level layout consisting of subtowers, enemies and items \n
    Constructor:
    height_seq: a non-decreasing sequence representing the height of each subtower

    """
    bg_image = resize(pygame.image.load('./assets/backgrounds/LevelScene.png').convert(), scale=0.4)
    # Player starts in an empty block regardless of level layout
    starting_block = Block((5, SCREEN_HEIGHT - BLOCK_SIDE_LENGTH))

    def __init__(self, height_seq: List[int]):
        super(LevelScene, self).__init__()
        self.player = Player(PLAYER_INIT_POS)
        self.queue: Deque[SubTower] = deque()
        self.waiting = False
        self.paused = False
        self.shifting = False
        
        for i, j in enumerate(height_seq, start=1):
            # Each subtower is 240 pixels wide and spacing between them is 100 pixels
            x_pos = (CAMERA_OFFSET) * i
            tower = SubTower(x_pos, j)
            self.queue.append(tower)
        self.current_tower = self.queue[0]    
        self.make_enemies()
        
    # create enemies in each block
    def make_enemies(self, rand: bool = True):
        min_power = 1
        max_power = self.player.power - 1
        for i in self.queue:
            shuffled_tower = random.sample(i.blocks_stack, k=len(i.blocks_stack))
            for j in shuffled_tower:
                enemy_power = random.randint(min_power, max_power)
                min_power = max_power
                max_power = min_power + enemy_power
                if max_power >= 99999: 
                    max_power = 99998
                new_enemy = Enemy((0,0), enemy_power)
                j.add_enemy(new_enemy)
    
    def teleport_player_to(self, block: Block) -> GameObjects:
        if block.cleared or block not in self.current_tower.blocks_stack:
            return
        dx = block.x_pos + (BLOCK_PADDING + 10 - self.player.x_pos)
        dy = (block.rect.bottom - self.player.rect.bottom) - BLOCK_PADDING - 5
        self.player.rect.move_ip(dx, dy)
        self.player.x_pos, self.player.y_pos = self.player.rect.topleft
        return block.contained_entity
        
    def handle_events(self, event: pygame.event.Event) -> None:
        # listening to player inputs, temporaily stops when enemy killed / tower cleared 
        for block in BLOCKS:     
            if not self.waiting:                      
                if event.type == pygame.MOUSEMOTION: 
                    if block.rect.collidepoint(event.pos):
                        block.on_mouse_hover()
                    else:
                        block.on_mouse_leave()
                elif event.type == pygame.MOUSEBUTTONDOWN:  
                    if block.rect.collidepoint(event.pos):
                        entity = self.teleport_player_to(block)
                        block.cleared = self.waiting = self.player.interact(entity)

        if event == GAME_OVER:
            BLOCKS.empty()
            ENEMIES.empty()
            LEVEL_SPRITES.empty()
            pygame.time.wait(200)
            self.switch_scene_to(GameoverScene())
        elif event == PLAYER_WIN:
            BLOCKS.empty()
            ENEMIES.empty()
            LEVEL_SPRITES.empty()
            self.switch_scene_to(VictoryScene())

        if event == BLOCK_CLEARED: 
            self.waiting = False

        if event == TOWER_CLEARED:
            if len(self.queue) >= 5:
                    self.shifting = True
                    self.waiting = True     
            self.queue.popleft()        
            # queue empty -> all towers cleared               
            if self.queue:
                self.current_tower = self.queue[0]
            else: 
                pygame.time.wait(300)
                pygame.event.post(PLAYER_WIN)  

    def render(self): 
        SCREEN.blit(self.bg_image, (0, 0)) 
        if not self.waiting:
            self.player.update()  
            if self.current_tower.is_cleared() and self.queue:
                pygame.event.post(TOWER_CLEARED)         
        elif self.shifting:  
            SCREEN.blit(self.bg_image, (0, 0)) 
            for sprite in LEVEL_SPRITES:
                shift_finished = sprite.shift() 
            # determine if transition is finished    
            self.shifting = self.waiting = shift_finished      
        ENEMIES.update()
        LEVEL_SPRITES.draw(SCREEN)          
    
    # use for loading levels, unfinished 
    @classmethod        
    def load_dict(cls):
        pass

class GameoverScene(BaseScene):  
    gameover_text = AURORA_FONT.render('GAME OVER !', 1, BLOOD)
    bg_image = pygame.image.load('./assets/backgrounds/GameoverScene.png').convert()
    def __init__(self):
        super(GameoverScene, self).__init__()
        game_over_sfx = pygame.mixer.Sound('./assets/sounds/game_over.mp3')
        game_over_sfx.play()
        
    def handle_events(self, event: pygame.event.Event) -> None:
        return super().handle_events(event)              
    
    def render(self) -> None:
        SCREEN.blit(self.bg_image, (0, 0)) 
        SCREEN.blit(self.gameover_text, (595, 75))

class VictoryScene(BaseScene):
    victory_text = AURORA_FONT.render('You Win !', 1, ORANGE)
    bg_image = resize(pygame.image.load('./assets/backgrounds/VictoryScene.png').convert(), scale=1.536)
    def __init__(self):
        super(VictoryScene, self).__init__()
        victory_sfx = pygame.mixer.Sound('./assets/sounds/victory.mp3')
        victory_sfx.play()
        
    def handle_events(self, event: pygame.event.Event) -> None:
        return super().handle_events(event)              
    
    def render(self) -> None:
        SCREEN.blit(self.bg_image, (0, 0)) 
        SCREEN.blit(self.victory_text, ((SCREEN_WIDTH - self.victory_text.get_width()) / 2 , 75))


