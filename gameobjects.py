import pygame
import pygame.mixer
from constants import *
from typing import Any, Self, Optional, List, Tuple

ENEMIES = pygame.sprite.Group()
BLOCKS = pygame.sprite.Group()
LEVEL_SPRITES = pygame.sprite.LayeredUpdates()

class GameObjects(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int]):
        super(GameObjects, self).__init__()
        self.x_pos, self.y_pos = pos
        self.image = pygame.Surface((0, 0))
        self.rect = pygame.Rect((0, 0, 0, 0))
        self.shifting = False
        LEVEL_SPRITES.add(self)

    def shift(self):
        if self.rect.left > self.x_pos - CAMERA_OFFSET:
            self.rect.move_ip(-CAMERA_OFFSET / 90, 0)
            return True
        else:
            self.rect.left = self.x_pos - CAMERA_OFFSET
            self.x_pos = self.rect.left
            return False
        
class Character(GameObjects):
    sprite = None
    def __init__(self, pos: Tuple[int, int]):
        self._layer = 2
        super(Character, self).__init__(pos)
        # power should be at most 99999 as rendering 6+ digits can lead to issues
        self.power = 0
        self.attacked = False
        self.alpha = 255
        self.frame_counter = 0
        self.render_offset = 0
        self.width = CHARACTER_WIDTH
        self.height = CHARACTER_HEIGHT
        self.image = pygame.Surface(
            (CHARACTER_WIDTH, CHARACTER_HEIGHT + POWER_HEIGHT), pygame.SRCALPHA
        )
        self.power_surf = self.image.subsurface((0, 0, CHARACTER_WIDTH, POWER_HEIGHT))
        self.power_surf.set_colorkey(BLACK)
        self.character_surf = self.image.subsurface(
            0, POWER_HEIGHT, CHARACTER_WIDTH, CHARACTER_HEIGHT
        )
        self.rect = self.image.get_rect(topleft=pos)
        # need to first blit the static image onto character subsurface 
        self.character_rect = self.character_surf.blit(self.sprite, (0, 0))
        self.vet = pygame.math.Vector2(self.character_rect.right, self.character_rect.bottom) / 30
        self.attacking = False
        self.dying = False
        self.deceased = False
        self.event_when_died = None

    def render_power(self) -> pygame.Rect:
        self.power_surf.fill(TRANSPARENT)
        power_text = POWER_FONT.render(str(self.power), 1, BLACK)
        place_pos = (CHARACTER_WIDTH - power_text.get_width()) // 2 - self.render_offset
        self.power_rect = self.power_surf.blit(power_text, (place_pos, 0))

    def update(self) -> None:
        self.render_power() 
        if self.attacked:
            pygame.draw.line(self.character_surf, BLOOD, (0, 0), self.frame_counter * self.vet, 3)
            if self.frame_counter >= 30: 
                self.frame_counter = 0
                self.attacked = False
                self.dying = True
            self.frame_counter += 1    
        if self.dying:
            self.fade_out()
        if self.deceased:
            pygame.event.post(self.event_when_died)

    def fade_out(self) -> None:     
        if self.alpha > 0:
            self.alpha -= 5
            self.image.set_alpha(self.alpha)
        else:
            self.kill()
            self.deceased = True

class Enemy(Character):
    sprite = pygame.image.load("./assets/sprites/enemy.PNG").convert_alpha()
    attack_sfx = pygame.mixer.Sound('./assets/sounds/enemy_attack.mp3')
    def __init__(self, pos: tuple[int, int], power: int):
        super(Enemy, self).__init__(pos)
        self.event_when_died = BLOCK_CLEARED
        self.power = power
        self.render_offset = 5
        ENEMIES.add(self)
        
    '''def update(self) -> None:
        self.render_power() 
        if self.attacked:
            pygame.draw.line(self.character_surf, BLOOD, (0, 0), self.frame_counter * self.vet, 3)
            if self.frame_counter >= 30: 
                self.frame_counter = 0
                self.attacked = False
                self.dying = True
            self.frame_counter += 1    
        if self.dying:
            self.fade_out()
        if self.deceased:
            pygame.event.post(BLOCK_CLEARED)'''
        
               
class Player(Character):
    sprite = pygame.image.load("./assets/sprites/player.PNG").convert_alpha()
    attack_sfx = pygame.mixer.Sound('./assets/sounds/player_slash.mp3')
    def __init__(self, pos) -> None:
        super(Player, self).__init__(pos)       
        self.event_when_died = GAME_OVER
        self.render_offset = 6.5 
        self.power = 10
    
    '''def update(self) -> None:
        if self.attacked:
            pygame.draw.line(self.character_surf, BLOOD, (0, 0), self.frame_counter * self.vet, 3)
            if self.frame_counter >= 30: 
                self.frame_counter = 0
                self.attacked = False
                self.dying = True
            self.frame_counter += 1    
        if self.dying:
            self.fade_out()
        if self.deceased:
            pygame.time.wait(150)
            pygame.event.post(GAME_OVER)
        else:
            self.render_power()'''    
        
    def interact(self, entity: GameObjects):
        if isinstance(entity, Enemy):
            return self.combat(entity)
        
    def combat(self, other: Enemy) -> bool:
        if self.power > other.power:
            self.attack_sfx.play()
            if self.power + other.power > 99999:
                self.power = 99999
            else: self.power += other.power 
            other.attacked = True   
        else:
            other.attack_sfx.play()
            self.attacked = True   
        return not self.attacked    

class Block(GameObjects):
    """
    Represents a block object inside a subtower \n
    Constructor:
    pos: the x and y position of the blocks
    Side-length of each block is defined in constants.py
    """

    # inner rect for hover effects, relative to each block
    normal_image = pygame.image.load('./assets/sprites/block_normal.png').convert()
    hover_image = pygame.image.load('./assets/sprites/block_hovered.png').convert()
    
    def __init__(self, pos: Tuple[int, int]):
        self._layer = 1
        super(Block, self).__init__(pos)
        BLOCKS.add(self)
        self.cleared = True  # has no enemy or items
        self.contained_entity = None
        self.image = self.normal_image
        self.rect = self.image.get_rect(topleft=pos)
       
        #self.rect = pygame.Rect(pos, (BLOCK_SIDE_WIDTH, BLOCK_SIDE_LENGTH))
        
    def on_mouse_hover(self):
        self.image = self.hover_image

    def on_mouse_leave(self):
        self.image = self.normal_image
        
    def add_enemy(self, enemy):
        x_coord = self.rect.right - BLOCK_PADDING - 20 - enemy.width
        y_coord = self.rect.bottom - BLOCK_PADDING - POWER_HEIGHT - enemy.height
        enemy.rect = self.image.blit(enemy.image, (x_coord, y_coord))
        enemy.x_pos, enemy.y_pos = enemy.rect.topleft
        self.contained_entity = enemy
        self.cleared = False

    def update(self) -> None:
        if self.rect.size == (0, 0) and self.rect.left == 0:
            self.kill()

class Roof(GameObjects):
    def __init__(self, pos: tuple[int, int]):
        self._layer = 1 
        super(Roof, self).__init__(pos)
        self.image = pygame.image.load('./assets/sprites/roof1.png').convert()
        self.image.set_colorkey(BLACK)
        self.rect = pygame.Rect(pos, (240, 125))

class SubTower:
    """
    Represents a tower being part of the level layout \n
    Constructor:
    x_pos: the common x position of the blocks
    stack_num: number of blocks in a tower, maximum 5
    """

    def __init__(self, x_pos: float, stack_num):
        self.blocks_stack: List[Block] = []
        for i in range(1, stack_num + 1):
            y_pos = SCREEN_HEIGHT - BLOCK_SIDE_LENGTH * i
            new_block = Block((x_pos + 5, y_pos))
            self.blocks_stack.append(new_block)
        roof_pos = (self.blocks_stack[-1].rect.left, self.blocks_stack[-1].rect.top - 113)
        tower_roof = Roof(roof_pos)


    def is_cleared(self):
        return all(i.cleared for i in self.blocks_stack)
 
    