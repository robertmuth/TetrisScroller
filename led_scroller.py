#!/usr/bin/python3
import rgbmatrix
from rgbmatrix import graphics
import logging
import pygame

from typing import List, Dict, Tuple, Optional

from pygame.locals import *
import functools
import random


from PIL import ImageFont, ImageDraw, Image


import tetris_font

ATARI_FONT = "./AtariST8x16SystemFont.ttf"

SCALE = 8
SCREEN_W = 128
SCREEN_H = 64


CHARS = ("01234567890"
         "abcdefghijklmnopqrstuvwxyz"
         "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
         "\"'`~!@#$%^&*()_+-={}[]:;<>?,<>?,./"
         "ÄäÖöÜüß")

ATARI_DIM = (8, 16)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (48, 73, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 96, 0)

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


def CmpPieces(piece1, piece2):
    (o1x, o1y), p1 = piece1
    (o2x, o2y), p2, = piece2
    maxy1 = max(o1y + y for _, y in p1)
    maxy2 = max(o1y + y for _, y in p2)
    if maxy1 < maxy2:
        return -1
    if maxy2 > maxy1:
        return 1
    pm = {}
    for x, y in p1:
        pm[x + o1x] = min(pm.get(x + o1x, y + o1y),  y + o1y)
    for x, y in p2:
        if pm.get(x + o2x, y + o2y) < y + o2y:
            return 1
    return -1


def SortPieces(pieces):
    return sorted(pieces, key=functools.cmp_to_key(CmpPieces))


BASE_OFFSET_Y = 24
SPEED_X = 16
SPEED_Y = 2


def time_for_char_to_arrive_at_loc(n, loc):
    return (loc + n) * 8 * SPEED_X


def Draw(screen, text, t, font_tab):

    offset_x = 128 - t // SPEED_X
    # screen.fill(WHITE)
    for n, c in enumerate(text):
        if c == " ":
            continue
        if offset_x + n * 8 < -8:
            continue
        if offset_x + n * 8 > 128:
            continue
        patterns = font_tab[c]
        for num, (ll, piece) in enumerate(patterns):
            offset_y = (t - time_for_char_to_arrive_at_loc(n, 1)) // SPEED_Y
            offset_y -= (48 * num)
            offset_y += len(piece)
            if offset_x + n * 8 > 32:
                if offset_y > 0:
                    offset_y = 0
            else:
                offset_y = (
                    t - time_for_char_to_arrive_at_loc(n, 12)) // SPEED_Y

                offset_y -= (32 * num)
                if offset_y < 0:
                    offset_y = 0

            color = COLORS[num % len(COLORS)]
            color = BLACK
            for pixel in piece:
                x = n * 8 + ll[0] + pixel[0] + offset_x
                y = ll[1] + pixel[1] + offset_y + BASE_OFFSET_Y
                screen.SetPixel(x, y, 0, 255, 0)


def MakeFontTab():
    txt = Image.new("RGBA", ATARI_DIM, (0, 0, 0, 256))
    draw = ImageDraw.Draw(txt)
    print("loadinf:", ATARI_FONT)
    font = ImageFont.truetype(ATARI_FONT, 16)
    out = {}
    for c in CHARS:
        draw.rectangle((0, 0) + ATARI_DIM,  fill=(255, 255, 255, 255))
        draw.text((0, 0), c, font=font, fill=(0, 0, 0, 255))

        # print(bitmap)
        print(f"\nNew char: [{c}] ")
        print(tetris_font.DumpSurface(txt))
        patterns = tetris_font.CheckSurface(txt)
        out[c] = SortPieces([(ll, all[index])
                             for ll, index, all in patterns])

    return out


def XXXmain():

    FONT_TAB = MakeFontTab()
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_W * SCALE, SCREEN_H * SCALE])
    surface = pygame.Surface([SCREEN_W, SCREEN_H])
    print("@@@@", surface.get_size(), screen.get_size())

    t = 0
    while True:
        t += 1
        Draw(surface, "Robert Muth 123 " * 10, t, FONT_TAB)
        pygame.transform.scale(
            surface, (SCREEN_W * SCALE, SCREEN_H * SCALE), screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
        pygame.display.flip()
    pygame.quit()


def MakeMatrix(args):
    options = rgbmatrix.RGBMatrixOptions()

    if args.led_gpio_mapping != None:
        options.hardware_mapping = args.led_gpio_mapping
    options.rows = args.led_rows
    options.cols = args.led_cols
    options.chain_length = args.led_chain
    options.parallel = args.led_parallel
    options.row_address_type = args.led_row_addr_type
    options.multiplexing = args.led_multiplexing
    options.pwm_bits = args.led_pwm_bits
    options.brightness = args.led_brightness
    options.pwm_lsb_nanoseconds = args.led_pwm_lsb_nanoseconds
    options.led_rgb_sequence = args.led_rgb_sequence
    options.pixel_mapper_config = args.led_pixel_mapper
    options.panel_type = args.led_panel_type

    if args.led_show_refresh:
        options.show_refresh_rate = 1

    if args.led_slowdown_gpio != None:
        options.gpio_slowdown = args.led_slowdown_gpio
    if args.led_no_hardware_pulse:
        options.disable_hardware_pulsing = True
    if not args.drop_privileges:
        options.drop_privileges = False

    return rgbmatrix.RGBMatrix(options=options)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", action="store",  type=str,
                        help="Text.",
                        default="Hello World!")
    parser.add_argument("--font_path", action="store",  type=str,
                        help="Font Path.",
                        default="AtariST8x16SystemFont.ttf")
    parser.add_argument("--font_size", action="store",  type=int,
                        help="Font Size.",
                        default=16)
    #
    parser.add_argument("-r", "--led-rows", action="store",
                        help="Display rows. 16 for 16x32, 32 for 32x32. Default: 32", default=32, type=int)
    parser.add_argument("--led-cols", action="store",
                        help="Panel columns. Typically 32 or 64. (Default: 32)", default=32, type=int)
    parser.add_argument("-c", "--led-chain", action="store",
                        help="Daisy-chained boards. Default: 1.", default=1, type=int)
    parser.add_argument("-P", "--led-parallel", action="store",
                        help="For Plus-models or RPi2: parallel chains. 1..3. Default: 1", default=1, type=int)
    parser.add_argument("-p", "--led-pwm-bits", action="store",
                        help="Bits used for PWM. Something between 1..11. Default: 11", default=11, type=int)
    parser.add_argument("-b", "--led-brightness", action="store",
                        help="Sets brightness level. Default: 100. Range: 1..100", default=100, type=int)
    parser.add_argument("-m", "--led-gpio-mapping", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm",
                        choices=['regular', 'regular-pi1', 'adafruit-hat', 'adafruit-hat-pwm'], type=str)
    parser.add_argument("--led-scan-mode", action="store",
                        help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)", default=1, choices=range(2), type=int)
    parser.add_argument("--led-pwm-lsb-nanoseconds", action="store",
                        help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130", default=130, type=int)
    parser.add_argument("--led-show-refresh", action="store_true",
                        help="Shows the current refresh rate of the LED panel")
    parser.add_argument("--led-slowdown-gpio", action="store",
                        help="Slow down writing to GPIO. Range: 0..4. Default: 1", default=1, type=int)
    parser.add_argument("--led-no-hardware-pulse", action="store",
                        help="Don't use hardware pin-pulse generation")
    parser.add_argument("--led-rgb-sequence", action="store",
                        help="Switch if your matrix has led colors swapped. Default: RGB", default="RGB", type=str)
    parser.add_argument("--led-pixel-mapper", action="store",
                        help="Apply pixel mappers. e.g \"Rotate:90\"", default="", type=str)
    parser.add_argument("--led-row-addr-type", action="store",
                        help="0 = default; 1=AB-addressed panels; 2=row direct; 3=ABC-addressed panels; 4 = ABC Shift + DE direct", default=0, type=int, choices=[0, 1, 2, 3, 4])
    parser.add_argument("--led-multiplexing", action="store",
                        help="Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kaler2Scan; 8=ZStripeUneven... (Default: 0)", default=0, type=int)
    parser.add_argument("--led-panel-type", action="store",
                        help="Needed to initialize special panels. Supported: 'FM6126A'", default="", type=str)
    parser.add_argument("--led-no-drop-privs", dest="drop_privileges",
                        help="Don't drop privileges from 'root' after initializing the hardware.", action='store_false')
    parser.set_defaults(drop_privileges=True)

    args = parser.parse_args()
    random.seed(66)

    matrix = MakeMatrix(args)
    FONT_TAB = MakeFontTab()
    canvas = matrix.CreateFrameCanvas()
    text = args.text
    t = 0
    print(canvas.width, canvas.height, text)
    while True:
        t += 1
        canvas.Clear()
        canvas.Fill(0, 0, 0)
        Draw(canvas, text, t, FONT_TAB)
        canvas = matrix.SwapOnVSync(canvas)


if __name__ == "__main__":
    main()