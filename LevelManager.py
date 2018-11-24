import pygame
import os
from Level import Level
import Config


class LevelManager:
    def __init__(self, player):
        self.player = player
        self.current_level_no = 0
        self.levels = self.make_levels()
        self.player.level = self.get_current_level()

    def get_current_level(self):
        return self.levels[self.current_level_no]

    def count_spaces(self, line):
        """ Number of leading spaces for a single line """
        return len(line) - len(line.lstrip())

    def get_indent_standard(self, lines):
        """ Number of leading spaces for a single line """
        for line in lines:
            spaces = self.count_spaces(line)
            if spaces:
                return spaces
        return 2  # File had no idents, return arbitrary/unused default

    def indent(self, line, spaces_per_line):
        """ Indent level of a given line """
        return self.count_spaces(line) / spaces_per_line

    def make_platform_dimensions(self, lines):
        """ Makes [width, height, x, y] formatted input for platform creation """
        indent_format = self.get_indent_standard(lines)
        heights = []
        indent_found = False
        for x in lines:
            indent_level = self.indent(x, indent_format)
            if not indent_found and indent_level == 0:
                continue
            else:
                indent_found = True
                heights.append(indent_level * Config.LINE_HEIGHT)

        return [[Config.LINE_WIDTH, y, Config.START_OFFSET + (x * Config.LINE_WIDTH), Config.SCREEN_HEIGHT - y] for x, y in enumerate(heights)]

    def make_enemy_dimensions(self, lines):
        """ Makes [x, y] formatted input for enemy (collison block) creation """
        indent_format = self.get_indent_standard(lines)
        heights = []
        indent_found = False
        for x in lines:
            indent_level = self.indent(x, indent_format)
            if not indent_found and indent_level == 0:
                continue
            else:
                indent_found = True
                if len(x) < 80:
                    heights.append(-1)
                else:
                    heights.append(indent_level * Config.LINE_HEIGHT)

        return [[Config.LINE_WIDTH, y, Config.START_OFFSET + (x * Config.LINE_WIDTH) + Config.LINE_WIDTH / 3, Config.SCREEN_HEIGHT - y - Config.LINE_HEIGHT / 2]
                for x, y in enumerate(heights)]

    def make_levels(self):
        """ Loop over files to visualize and make levels out of them """
        dir = "./levels/"
        levels = []
        for file in os.listdir(dir):
            src_lines = []
            with open(dir + file) as src:
                src_lines = [x.replace("\t", "  ").rstrip() for x in src.readlines()]  # Replace tabs with 2 spaces
            sprites = self.make_platform_dimensions(src_lines)
            enemies = self.make_enemy_dimensions(src_lines)
            level_end = -(sprites[-1][2] + sprites[-1][0])
            levels.append(Level(self.player, sprites, enemies, level_end, file))
        levels.append(Level(self.player, [], [], 0, ""))
        return levels

    # def end_game(self):
    #     """ Exit for now. Later add end of game message """
    #     pygame.quit()
    #     exit(0)

    def advance_level(self):
        if self.current_level_no < len(self.levels) - 2:
            self.player.rect.x = Config.LEFT_LIMIT
            self.current_level_no += 1
            self.player.level = self.get_current_level()
            return True
        else:
            self.current_level_no += 1
            self.player.level = self.get_current_level()
            return False

    def reset_current_level(self):
        self.player.rect.x = Config.RIGHT_LIMIT - self.player.width  # middle of the screen: (SCREEN_WIDTH / 2) + player.width
        self.player.stop_x()
        self.player.stop_y()
        self.get_current_level().shift_world(-self.get_current_level().world_shift)
        self.get_current_level().speed = 0
        self.get_current_level().iterations = 0
