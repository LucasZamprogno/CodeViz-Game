"""
Initially adapted/learned from:
http://programarcadegames.com/python_examples/f.php?file=platform_scroller.py

Requires Python3, pygame package
"""

import pygame
from LevelManager import LevelManager
from Player import Player
import Config

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
- Patterned background so you can notice speed with no platforms -> Background image functionality there, just need to play with size/resolution
- Add a level reset button for if you get stuck (reset player pos, world scroll, any progress stats)
"""


class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  # call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.image = pygame.transform.scale(self.image, (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        self.start = 0;
        self.end = self.image.get_width()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


def main():
    """ Main Program """

    pygame.init()

    BackGround = Background('test.png', [0,0])

    # Set the height and width of the screen and window title
    size = [Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Side-scrolling Platformer")

    # Create the player
    player = Player()

    # Create all the levels
    manager = LevelManager(player)
    player.register_manager(manager)

    active_sprite_list = pygame.sprite.Group()

    player.rect.x = Config.RIGHT_LIMIT - player.width  # Start at right scroll border
    player.rect.y = Config.SCREEN_HEIGHT - player.rect.height  # Start on ground
    active_sprite_list.add(player)

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Current status of directional keys
    r_down = False
    l_down = False
    u_down = False

    # Used to prevent auto-bunnyhopping. Active while holding up
    jump_lock = False

    speed_sum = 0
    iterations = 1

    large_font = pygame.font.SysFont('comicsans', 30)

    """ Main program loop until user exits or game quits """
    while not done:
        if BackGround.start < BackGround.image.get_width() * -1:
            BackGround.start = BackGround.image.get_width()

        if BackGround.end < BackGround.image.get_width() * -1:
            BackGround.end = BackGround.image.get_width()


        score = large_font.render("score: " + str(round(speed_sum/iterations, 1)), 1, (255, 255, 255))
        file_name = large_font.render(manager.get_current_level().file_name, 1, (255, 255, 255))
        speed_sum += player.change_x
        skip = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            # Check for pressed keys
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_LEFT or key == pygame.K_a:
                    l_down = True
                if key == pygame.K_RIGHT or key == pygame.K_d:
                    r_down = True
                if key == pygame.K_UP or key == pygame.K_w or key == pygame.K_SPACE:
                    u_down = True
                if key == pygame.K_q:
                    manager.end_game()
                if key == pygame.K_s:
                    skip = True
                if key == pygame.K_r:
                    manager.reset_current_level()

            # Check for released keys
            if event.type == pygame.KEYUP:
                key = event.key
                if key == pygame.K_LEFT or key == pygame.K_a:
                    l_down = False
                if key == pygame.K_RIGHT or key == pygame.K_d:
                    r_down = False
                if key == pygame.K_UP or key == pygame.K_w or key == pygame.K_SPACE:
                    u_down = False
                    jump_lock = False

        going_right = None
        # Jump if on the ground, reduce grav if airborne (or haven't released UP)
        if u_down:
            if jump_lock:
                player.float()
            else:
                player.jump()
                jump_lock = True

        if r_down and l_down:
            pass  # Do nothing, but maintain speed
        elif r_down:
            player.acc_right()
            going_right = True
        elif l_down:
            player.acc_left()
            going_right = False
        else:
            player.stop_x()

        # Update the player.
        active_sprite_list.update(BackGround, going_right)

        # Update items in the level
        manager.get_current_level().update()

        # If the player gets near the right side, shift the world left (-x)
        if player.rect.right >= Config.RIGHT_LIMIT:
            diff = player.rect.right - Config.RIGHT_LIMIT
            player.rect.right = Config.RIGHT_LIMIT
            manager.get_current_level().shift_world(-diff)

        # If the player gets near the left side, shift the world right (+x)
        if player.rect.left <= Config.LEFT_LIMIT:
            diff = Config.LEFT_LIMIT - player.rect.left
            player.rect.left = Config.LEFT_LIMIT
            manager.get_current_level().shift_world(diff)


        # If the player gets to the end of the level, go to the next level
        current_position = player.rect.x + manager.get_current_level().world_shift

        if skip or current_position < manager.get_current_level().level_limit:
            manager.advance_level()
 
        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT

        # Invoking background image
        # screen.fill([255, 255, 255])
        # screen.blit(BackGround.image, BackGround.rect)
        screen.blit(BackGround.image, (BackGround.start, 0))
        screen.blit(BackGround.image, (BackGround.end, 0))
        manager.get_current_level().draw(screen)
        active_sprite_list.draw(screen)
        screen.blit(score, (Config.SCREEN_WIDTH / 2 - 2 * score.get_width() + Config.SCREEN_WIDTH / 2, 50))
        screen.blit(file_name, (0.5*file_name.get_width(), 50))
        pygame.display.update()
        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
 
        # Limit to 60 frames per second
        clock.tick(60)
 
        # Update the screen

        iterations += 1
 
    # stats screen should come here
    # speed_sum / iterations
    # Be IDLE friendly. If you forget this line, the program will 'hang' on exit.
    pygame.quit()


if __name__ == "__main__":
    main()
