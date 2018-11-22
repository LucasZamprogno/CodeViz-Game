import pygame
import Config


class Player(pygame.sprite.Sprite):
    """ This class represents the rectangle at the bottom that the player controls. """
    width = 40
    height = 60

    def __init__(self):
        # Call the parent's constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.image.load("elisasa.jpg")
        self.image = pygame.transform.scale(self.image, (75, 100))

        # Set a referance to the image rect.
        self.rect = self.image.get_rect()

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

        # List of sprites we can bump against
        self.level = None

        self.manager = None

    def register_manager(self, manager):
        self.manager = manager

    def update(self, background, is_right):
        """ Move the player. """
        self.update_x(background, is_right)
        self.update_y()

    def update_x(self, background, is_right):
        # Move left/right
        self.rect.x += self.change_x
        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right
            self.change_x = 0

        if len(block_hit_list) == 0:
            background.start -= self.change_x / 2
            background.end -= self.change_x / 2

        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        if len(enemy_hit_list) > 0:
            self.manager.reset_current_level()

    def update_y(self):
        # Add effect of gravity
        self.change_y += Config.GRAV
        # Move up/down
        self.rect.y += self.change_y
        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:

            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom

            # Stop our vertical movement
            self.change_y = 0

        enemy_hit_list = pygame.sprite.spritecollide(self, self.level.enemy_list, False)
        if len(enemy_hit_list) > 0:
            self.manager.reset_current_level()

        # See if we are on the ground.
        if self.rect.y >= Config.SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = Config.SCREEN_HEIGHT - self.rect.height

    def jump(self):
        """ Called when user hits 'jump' button. """
        if self.on_ground():
            self.change_y = Config.JUMP_FORCE

    def float(self):
        if not self.on_ground():
            self.change_y += Config.GRAV_REDUCTION

    def on_ground(self):
        # move down 2px and check collision. Apparently just 1px is buggy
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2
        return len(platform_hit_list) > 0 or self.rect.bottom >= Config.SCREEN_HEIGHT

    def acc_left(self):
        """ Called when the user hits the left arrow. """
        if self.change_x > -Config.SPEED_MIN:
            self.change_x = -Config.SPEED_MIN
        elif self.change_x <= -Config.SPEED_MAX:
            self.change_x = -Config.SPEED_MAX
        else:
            self.change_x -= Config.ACCEL_X

    def acc_right(self):
        """ Called when the user hits the right arrow. """
        if self.change_x < Config.SPEED_MIN:
            self.change_x = Config.SPEED_MIN
        elif self.change_x >= Config.SPEED_MAX:
            self.change_x = Config.SPEED_MAX
        else:
            self.change_x += Config.ACCEL_X

    def stop_x(self):
        """ Called when the user lets off the keyboard or collides. """
        self.change_x = 0

    def stop_y(self):
        """ Called when the player collides. """
        self.change_y = 0
