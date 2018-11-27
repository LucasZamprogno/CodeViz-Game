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
        self.start = 0
        self.end = self.image.get_width()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


def end_game(manager, screen, large_font):
    final_title = large_font.render("FINAL STATS: ", 1, (255, 255, 255))
    average_title = large_font.render("Average Grade: ", 1, (255, 255, 255))
    constant_spacing = Config.SCREEN_HEIGHT / (3 * len(manager.levels))
    spacing = constant_spacing
    screen.blit(final_title, (Config.SCREEN_WIDTH / 2 - 0.5 * final_title.get_width(), Config.SCREEN_HEIGHT / 8))
    screen.blit(average_title,
                (Config.SCREEN_WIDTH / 2 - 0.5 * final_title.get_width(), Config.SCREEN_HEIGHT / 8 + spacing))
    spacing += constant_spacing
    x_position_of_first = 0
    for level_number, level in enumerate(manager.levels):
        if level_number == len(manager.levels) - 1:
            break
        average_grade = round((level.speed / level.iterations + 1) / Config.SPEED_MAX * 100, 1)
        grade = large_font.render(
            "Level " + str(level_number + 1) + " (" + level.file_name + "): " + str(average_grade), 1, (255, 255, 255))
        if level_number == 0:
            x_position_of_first = grade.get_width()
        screen.blit(grade,
                    (Config.SCREEN_WIDTH / 2 - 0.5 * x_position_of_first, Config.SCREEN_HEIGHT / 8 + spacing))
        spacing += constant_spacing


def main():
    """ Main Program """

    pygame.init()

    background = Background('city.png', [0,0])

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

    large_font = pygame.font.SysFont('comicsans', 30)
    over = False
    level_num = 0
    """ Main program loop until user exits or game quits """

    while not done:
        if level_num % 2 == 0 and manager.current_level_no % 2 == 1:
            background = Background('test.png', [0, 0])
            level_num = 1
        elif level_num % 2 == 1 and manager.current_level_no % 2 == 0:
            background = Background('city.png', [0, 0])
            level_num = 0

        if background.start < background.image.get_width() * -1:
            background.start = background.image.get_width()

        if background.end < background.image.get_width() * -1:
            background.end = background.image.get_width()

        manager.get_current_level().iterations += 1
        score = large_font.render("grade: " + str(round((manager.get_current_level().speed / manager.get_current_level().iterations) / Config.SPEED_MAX * 100, 1)), 1, (255, 255, 255))
        file_name = large_font.render(manager.get_current_level().file_name, 1, (255, 255, 255))
        manager.get_current_level().speed += player.change_x
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
        elif l_down:
            player.acc_left()
        else:
            player.stop_x()

        # Update the player.
        active_sprite_list.update(background)

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
            if not manager.advance_level():
                over = True

        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT

        # Invoking background image
        # screen.fill([255, 255, 255])
        # screen.blit(BackGround.image, BackGround.rect)
        screen.blit(background.image, (background.start, 0))
        screen.blit(background.image, (background.end, 0))
        if not over:
            manager.get_current_level().draw(screen)
            active_sprite_list.draw(screen)
            screen.blit(score, (Config.SCREEN_WIDTH / 2 - 2 * score.get_width() + Config.SCREEN_WIDTH / 2, 50))
            screen.blit(file_name, (0.5*file_name.get_width(), 50))
        else:
            end_game(manager, screen, large_font)

        pygame.display.update()
        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
 
        # Limit to 60 frames per second
        clock.tick(60)
 
        # Update the screen
 
    # stats screen should come here
    # speed_sum / iterations
    # Be IDLE friendly. If you forget this line, the program will 'hang' on exit.
    pygame.quit()


if __name__ == "__main__":
    main()
