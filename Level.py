import pygame
import Config


class Level:
    def __init__(self, player, platforms, enemies, end, file):
        """ Represents the level
        :param player: Not entirely sure what this is needed for tbh
        :param platforms: All the platforms [width, height, x, y] representing lines
        :param end: Endpoint of the level
        """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.player = player
        self.level_limit = end
        self.file_name = file
        self.speed = 0
        self.iterations = 0
        for platform in platforms:
            block = Platform(platform[0], platform[1])
            block.rect.x = platform[2]
            block.rect.y = platform[3]
            block.player = self.player
            self.platform_list.add(block)

        for enemy in enemies:
            if enemy[1] == -1:
                continue
            e_block = Enemy()
            e_block.rect.x = enemy[2]     # x
            e_block.rect.y = enemy[3]     # y
            e_block.player = self.player
            self.enemy_list.add(e_block)

        # How far this world has been scrolled left/right
        self.world_shift = 0

    def update(self):
        """ Update everything on this level """
        self.platform_list.update()
        self.enemy_list.update()

    def draw(self, screen):
        """ Draw all background + platforms on this level """
        # screen.fill(BLACK)  # Draw the background
        self.platform_list.draw(screen)  # Draw all the sprites/platforms
        self.enemy_list.draw(screen)

        for spike in self.enemy_list:
            x = spike.rect.x
            y = spike.rect.y
            bot_left = (x, y + Config.LINE_HEIGHT / 2)
            top = (x + (Config.LINE_WIDTH / 6), y)
            bot_right = (x + (Config.LINE_WIDTH / 3), y + Config.LINE_HEIGHT / 2)
            point_list = [bot_left, top, bot_right]
            pygame.draw.polygon(screen, Config.GREEN, point_list)

    def shift_world(self, shift_x):
        """ When the user moves left/right against the barrier
        and we need to scroll everything """

        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprites and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for enemy in self.enemy_list:
            enemy.rect.x += shift_x


class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on. Visualization of a line of code via indent"""
    def __init__(self, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(Config.GREEN)
        self.rect = self.image.get_rect()


class Enemy(pygame.sprite.Sprite):
    """ Enemt box to help with triangle collisons. Visualization of a line of code that is longer than 80 characters"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([Config.LINE_WIDTH / 3, Config.LINE_HEIGHT / 2])
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
