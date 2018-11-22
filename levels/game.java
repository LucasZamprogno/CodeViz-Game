"""
Initially adapted/learned from:
http://programarcadegames.com/python_examples/f.php?file=platform_scroller.py

Requires Python3, pygame package
"""

import pygame
import os

"""
Controls:
Left/Right arrows or A/D to move left/right. You gain speed over time, to a cap.
Up arrow, W, or SPACE to jump. Holding it makes you jump further.
S to skip level (some could be impossible with weird indents).
Q to quit.


Gameplay considerations:
Ideally the combination of SPEED_MAX, GRAV, GRAV_REDUCTION, and LINE_WIDTH
should be such that the player can jump 2x indents near the apex of the a single jump
if they hold jump.
The player should also be able to use small hops to cross single lines at max speed
i.e _-_-_-_-_ you should be able to jump along the top platforms at max speed

TODOs/ideas:
- [FIXED] BUG: Hitting walls doesn't reset velocity
- Max level length seems to be 16 bits, so -65536, so don't use files too long (~ > 300 lines)
- Might be good to start level at first non-0-indent line -> DONE (i think)
- Keep track of average velocity over the run
- If hazards are introduced, keep track of furthest line reached
- End of game screen with stats etc
- Show controls on screen
- Extract globals/constants to some config file
- Other hazards (e.g. a small spike) for going over some line length
- Display current file name
- Add a level reset button for if you get stuck (reset player pos, world scroll, any progress stats)
"""

# Global constants

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450

# Dimensions
LINE_WIDTH = 180
LINE_HEIGHT = 65

# Config
START_OFFSET = 700
RIGHT_LIMIT = 500
LEFT_LIMIT = 150
SPEED_MIN = 6
SPEED_MAX = 12
JUMP_FORCE = -13
ACCEL_X = .04
GRAV = 1
GRAV_REDUCTION = -(0.45 * GRAV)


class Player(pygame.sprite.Sprite):
    width = 40
    height = 60

    def __init__(self):
        # Call the parent's constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface([Player.width, Player.height])
        self.image.fill(RED)

        # Set a referance to the image rect.
        self.rect = self.image.get_rect()

        # Set speed vector of player
        self.change_x = 0
        self.change_y = 0

        # List of sprites we can bump against
        self.level = None

    def update(self):
        """ Move the player. """
        self.update_x()
        self.update_y()

    def update_x(self):
        # Move left/right
        self.rect.x += self.change_x
        # See if we hit anything
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            self.change_x = 0

        if len(enemy_hit_list) > 0:
            reset_current_level(self, self.level)

    def update_y(self):
        # Add effect of gravity
        self.change_y += GRAV
        # Move up/down
        self.rect.y += self.change_y
        # Check and see if we hit anything
        for block in block_hit_list:

        # Stop our vertical movement
        self.change_y = 0

        if len(enemy_hit_list) > 0:
            reset_current_level(self, self.level)

        # See if we are on the ground.
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def on_ground(self):
        # move down 2px and check collision. Apparently just 1px is buggy
        self.rect.y += 2
        self.rect.y -= 2
        return len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT