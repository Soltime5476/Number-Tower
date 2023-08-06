import pygame
import random
from constants import *
from typing import Any, Self, Optional, List, Tuple, Deque
from collections import deque

class CameraGroup(pygame.sprite.LayeredUpdates):
    def __init__(self):
        super().__init__()
        self.display_surf = pygame.display.get_surface()
        self.shifting_time = 1500
        # camera offset
        self.offset = pygame.math.Vector2(-CAMERA_OFFSET, 0)

class GameObjects(pygame.sprite.Sprite):
    def __init__(self, pos: tuple[int, int]):
        super(GameObjects, self).__init__()
        self.x_pos, self.y_pos = pos
        self.rect: pygame.Rect
        self.shifting = False
        ALL_SPRITES.add(self)

    def shift(self):
        if self.rect.left > self.x_pos - CAMERA_OFFSET:   
            self.rect.move_ip(-CAMERA_OFFSET / 90, 0)
            return True
        else: 
            self.rect.left = self.x_pos - CAMERA_OFFSET
            self.x_pos = self.rect.left
            return False

            
class Character(GameObjects):
    power_font = pygame.font.SysFont("Times New Roman", FONT_SIZE)
    
    def __init__(self, pos: Tuple[int, int]):
        self._layer = 2
        super(Character, self).__init__(pos)
        CHARACTERS.add(self)
        self.power = 0
        self.alpha = 255
        self.render_offset = 0
        self.width = CHARACTER_WIDTH
        self.height = CHARACTER_HEIGHT
        self.image = pygame.Surface(
            (CHARACTER_WIDTH, CHARACTER_HEIGHT + POWER_HEIGHT), pygame.SRCALPHA
        )
        self.power_surf = self.image.subsurface((0, 0, CHARACTER_WIDTH, POWER_HEIGHT))
        self.character_surf = self.image.subsurface(0, POWER_HEIGHT, CHARACTER_WIDTH, CHARACTER_HEIGHT)
        # create transparent space above player for score display
        #self.image.fill((0, 0, 0, 0), rect=(0, 0, CHARACTER_WIDTH, POWER_HEIGHT))
        self.rect = self.image.get_rect(topleft=pos)
        self.is_dying = False
        self.deceased = False
        
    def render_power(self) -> pygame.Rect:
        self.power_surf.fill(TRANSPARENT)
        power_text = self.power_font.render(str(self.power), 1, BLACK)
        place_pos = (CHARACTER_WIDTH - power_text.get_width()) // 2 - self.render_offset
        power_rect = self.power_surf.blit(power_text, (place_pos, 0))
        return power_rect

    def combat(self, other: Self) -> bool:
        player_won = True
        if self.power > other.power: 
            self.power += other.power           
            other.is_dying = True
        else:
            self.is_dying = True
            player_won = False
        return player_won
    
    def update(self) -> None:
        if self.is_dying:
            if self.alpha > 0:
                self.alpha -= 5
                self.image.set_alpha(self.alpha) 
            else: 
                self.kill() 
                self.deceased = True
        else:
            self.render_power()
        
class Enemy(Character):
    def __init__(self, pos: tuple[int, int], power: int):
        super(Enemy, self).__init__(pos)
        self.power = power
        self.render_offset = 5
        CHARACTERS.add(self)
        enemy_sprite = pygame.image.load('./assets/enemy.PNG').convert_alpha()
        self.character_surf.blit(enemy_sprite, (0, 0))

        
        

class Block(GameObjects):
    """
    Represents a block object inside a subtower \n
    Constructor:
    pos: the x and y position of the blocks
    Side-length of each block is defined in constants.py
    """

    # inner rect for hover effects, relative to each block
    CONTENT_RECT = pygame.Rect(
        BLOCK_PADDING,
        BLOCK_PADDING,
        BLOCK_SIDE_WIDTH - 2 * BLOCK_PADDING,
        BLOCK_SIDE_LENGTH - 2 * BLOCK_PADDING,
    )

    def __init__(self, pos: Tuple[int, int]):
        self._layer = 1
        super(Block, self).__init__(pos)
        BLOCKS.add(self)
        self.is_empty = True  # has no enemy or items
        self.contained_entity = None
        self.image = pygame.Surface((BLOCK_SIDE_WIDTH, BLOCK_SIDE_LENGTH))
        self.image.fill(BLACK)
        self.image.fill(WHITE, rect=self.CONTENT_RECT)
        self.rect = pygame.Rect(pos, (BLOCK_SIDE_WIDTH, BLOCK_SIDE_LENGTH))

    def on_mouse_hover(self):
        self.image.fill(GREY, rect=self.CONTENT_RECT)

    def on_mouse_leave(self):
        self.image.fill(WHITE, rect=self.CONTENT_RECT)

    def add_enemy(self, enemy: Enemy):
        x_coord = self.rect.right - BLOCK_PADDING - 20 - enemy.width
        y_coord = self.rect.bottom - BLOCK_PADDING - POWER_HEIGHT - enemy.height 
        enemy.rect = self.image.blit(enemy.image, (x_coord, y_coord))
        enemy.x_pos, enemy.y_pos = enemy.rect.topleft
        self.contained_entity = enemy
        self.is_empty = False

    def update(self) -> None:
        if self.rect.size == (0, 0) and self.rect.left == 0:
            self.kill()

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

    def is_cleared(self):
        return all(i.is_empty for i in self.blocks_stack)


class Player(Character):
    def __init__(self, pos) -> None:
        super(Player, self).__init__(pos)
        # power should be at most 9999 as rendering 5+ digits can lead to issues
        self.render_offset = 6.5
        self.power = 10
        self.current_block: Optional(Block) = None
        #self.character_surf.fill(SKY_BLUE)
        player_sprite = pygame.image.load('./assets/player.PNG').convert_alpha()
        self.character_surf.blit(player_sprite, (0, 0))
        
    def teleport_to(self, block: Block):
        pass
             
    def interact(self, entity: GameObjects):
        if isinstance(entity, Enemy):
            return self.combat(entity)


class LevelLayout:
    """
    Represents the whole level layout consisting of subtowers, enemies and items \n
    Constructor:
    height_seq: a non-decreasing sequence representing the height of each subtower

    """

    def __init__(self, height_seq: List[int], player: Player, screen: pygame.Surface):
        self.player = player
        self.queue: Deque[SubTower] = deque()
        
        for i, j in enumerate(height_seq, start=1):
            # Each subtower is 180 pixels wide and spacing between them is 100 pixels
            x_pos = (CAMERA_OFFSET) * i
            tower = SubTower(x_pos, j)
            self.queue.append(tower)
        self.current_tower = self.queue[0]    
        self.make_enemies()
        
    # create enemies in each block
    def make_enemies(self):
        min_power = 1
        max_power = self.player.power - 1
        for i in self.queue:
            shuffled_tower = random.sample(i.blocks_stack, k=len(i.blocks_stack))
            for j in shuffled_tower:
                enemy_power = random.randint(min_power, max_power)
                min_power = max_power
                max_power = min_power + enemy_power
                if max_power >= 9999: 
                    max_power = 9999
                new_enemy = Enemy((0,0), enemy_power)
                j.add_enemy(new_enemy)
    
    def teleport_player_to(self, block: Block) -> None:
        if block.is_empty or block not in self.current_tower.blocks_stack:
            return
        dx = block.x_pos + (BLOCK_PADDING + 10 - self.player.x_pos)
        dy = (block.rect.bottom - self.player.rect.bottom) - BLOCK_PADDING
        self.player.rect.move_ip(dx, dy)
        self.player.x_pos, self.player.y_pos = self.player.rect.topleft
        self.player.current_block = block
        block.is_empty = self.player.interact(block.contained_entity)
        if self.current_tower.is_cleared():
            pygame.event.post(TOWER_CLEARED)

    def handle_event(self, event: pygame.event.Event):
        pass            
                

    @classmethod        
    def load_dict(cls):
        pass        

CHARACTERS = pygame.sprite.Group()
BLOCKS = pygame.sprite.Group()
ALL_SPRITES = CameraGroup()