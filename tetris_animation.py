#!/usr/bin/python3
import logging
import pygame
import random
import argparse

from typing import List, Dict, Tuple, Optional

from pygame.locals import *


from PIL import ImageFont, ImageDraw, Image


import tetris_font


BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)


RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (48, 73, 255, 255)
YELLOW = (255, 255, 0, 255)
CYAN = (0, 255, 255, 255)
MAGENTA = (255, 0, 255, 255)
ORANGE = (255, 96, 0, 255)

COLORS = [
    #    BLACK,
    #    WHITE,
    RED,
    GREEN,
    BLUE,
    YELLOW,
    CYAN,
    MAGENTA,
    ORANGE
]

GRAY_COLORS = [
    (0, 0, 0, 255),
    (16, 16, 16, 255),
    (32, 32, 32, 255),
    (48, 48, 48, 255),
    (64, 64, 64, 255),
    (80, 80, 80, 255),
    (96, 96, 96, 255),
    (112, 112, 112, 255),
    (128, 128, 128, 255),
]

PASTEL_COLORS = [
    (224, 187, 228, 255),
    (149, 125, 173, 255),
    (210, 145, 188, 255),
    (254, 200, 216, 255),
    (255, 223, 211, 255),
]

EARTH_COLORS = [
    (180, 163, 144, 255),
    (146, 126, 117, 255),
    (121, 99, 99, 255),
    (153, 168, 133, 255),
    (212, 219, 186, 255),
    (253, 237, 207, 255),
]

DARK_MUSTARD_COLORS = [
    (255, 222, 92, 255),
    (205, 118, 12, 255),
    (150, 71, 5, 255),
    (117, 35, 35, 255),
    (176, 49, 49, 255),
]


BASE_OFFSET_Y = 24
SPEED_X = 48 * 3
SPEED_Y = 6 * 3


def time_for_char_to_arrive_at_loc(n, loc):
    return (loc + n) * 8 * SPEED_X


SCALE = 8
SCREEN_W = 128
SCREEN_H = 64


def Draw(screen, text, t, font_tab, font_w, colors):
    offset_x = 128 - t // SPEED_X
    screen.fill(WHITE)
    for n, c in enumerate(text):
        if c == " ":
            continue
        if offset_x + n * font_w < -font_w:
            continue
        if offset_x + n * font_w > 128:
            continue
        patterns = font_tab[c]
        for num, (ll, piece) in enumerate(patterns):
            color = colors[num % len(colors)]
            offset_y = (t - time_for_char_to_arrive_at_loc(n, 1)) // SPEED_Y
            offset_y -= (48 * num)
            offset_y += len(piece)
            if offset_x + n * font_w > font_w * 4:
                if offset_y > 0:
                    offset_y = 0
            else:
                offset_y = (
                    t - time_for_char_to_arrive_at_loc(n, 12)) // SPEED_Y

                offset_y -= (32 * num)
                if offset_y < 0:
                    offset_y = 0

            for pixel in piece:
                x = n * 8 + ll[0] + pixel[0] + offset_x
                y = ll[1] + pixel[1] + offset_y + BASE_OFFSET_Y
                screen.set_at((x, y), color)


def RenderPyGame(FONT_TAB, font_w, chars):
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_W * SCALE, SCREEN_H * SCALE])
    surface = pygame.Surface([SCREEN_W, SCREEN_H])

    t = 0
    while True:
        t += 1
        Draw(surface, chars, t, FONT_TAB, font_w, GRAY_COLORS)
        pygame.transform.scale(
            surface, (SCREEN_W * SCALE, SCREEN_H * SCALE), screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
        pygame.display.flip()
    pygame.quit()


ATARI_FONT = "./AtariST8x16SystemFont.ttf"
ATARI_SIZE = 16

AMIGA_FONT = "./amiga4ever.ttf"
AMIGA_SIZE = 8

CHARS = ("01234567890"
         "abcdefghijklmnopqrstuvwxyz"
         "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
         "\"'`~!@#$%^&*()_+-={}[]:;<>?,<>?,./"
         "ÄäÖöÜüß")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scroll_text", action="store",  type=str,
                    help="Text to scroll.",
                    default=CHARS)
    parser.add_argument("--font_path", action="store",  type=str,
                    help="Font Path.",
                    default=ATARI_FONT)
    parser.add_argument("--font_size", action="store",  type=int,
                    help="Font Size.",
                    default=ATARI_SIZE)

    random.seed(66)
    args = parser.parse_args()
    dim, font_tab = tetris_font.MakeFontTab(args.font_path, args.font_size, CHARS * 10)
    #dim, font_tab = tetris_font.MakeFontTab(AMIGA_FONT, AMIGA_SIZE, CHARS * 10)

    RenderPyGame(font_tab, dim[0], args.scroll_text)


if __name__ == '__main__':
    main()
