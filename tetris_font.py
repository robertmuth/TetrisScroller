#!/usr/bin/python3
"""
See whether character in a font can be tiles with tetris  pieces

https://www.dafont.com/search.php?q=chicago
https://int10h.org/oldschool-pc-fonts/fontlist/?2#kaypro

/tetris_font.py ./amiga4ever.ttf 8  "9"
./tetris_font.py ./AtariST8x16SystemFont.ttf 16  "@"
"""
import logging

from typing import List, Dict, Tuple, Optional

from pygame.locals import *
import random
import functools

from PIL import ImageFont, ImageDraw, Image

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)


def DumpSurface(surface):
    lines = []
    w, h = surface.size

    for y in range(h):
        line = ""
        for x in range(w):

            pixel = surface.getpixel((x, y))
            if pixel[0] == 0:
                line += "X"
            elif pixel[0] == 255:
                line += "."
            else:
                line += "o"
        lines.append(line)
    return "\n".join(lines)


TETRIS_PIECES = [
    # SQUARE
    [(0, 0), (0, 1), (1, 0), (1, 1)],
    # L
    [(0, 0), (0, 1), (1, 0), (2, 0)],
    [(0, 0), (0, 1), (0, 2), (1, 2)],
    [(-2, 1), (-1, 1), (0, 1), (0, 0)],
    [(0, 0), (1, 0), (1, 1), (1, 2)],
    # reverse L
    [(0, 0), (0, 1), (1, 1), (2, 1)],
    [(-1, 2), (0, 0), (0, 1), (0, 2)],
    [(0, 0), (1, 0), (2, 0), (2, 1)],
    [(0, 0), (0, 1), (0, 2), (1, 0)],
    # I
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    # S
    [(-1, 1), (-1, 2), (0, 0), (0, 1)],
    [(0, 0), (1, 0), (1, 1), (2, 1)],
    # reverse
    [(0, 0), (0, 1), (1, 1), (1, 2)],
    [(-1, 1), (0, 0), (0, 1), (1, 0)],
    # T
    [(-1, 1), (0, 0), (0, 1), (0, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 0)],
    [(0, 0), (0, 1), (0, 2), (1, 1)],
    [(-1, 1), (0, 0), (0, 1), (1, 1)],
    # Corner
    [(0, 1), (1, 1), (0, 0)],
    [(0, 1), (0, 0), (1, 0)],
    [(1, 1), (1, 0), (0, 0)],
    [(-1, 1), (0, 1), (0, 0)],
]


CHEAT_PIECES = set([n for n, x in enumerate(TETRIS_PIECES) if len(x) != 4])

TETRIES_PIECES_CHEATS = [x for x in TETRIS_PIECES if len(x) != 4]
TETRIES_PIECES_NORMAL = [x for x in TETRIS_PIECES if len(x) == 4]
assert len(TETRIES_PIECES_CHEATS) + \
    len(TETRIES_PIECES_NORMAL) == len(TETRIS_PIECES)

POINT = Tuple[int, int]
EMPTY = -1


class Covering:

    def __init__(self, points: List[POINT], w=None, h=None):
        if w is None:
            self._w = 1 + max(x for x, y in points)
        else:
            self._w = w
        if h is None:
            self._h = 1 + max(y for x, y in points)
        else:
            self._h = h
        self._m = self._w * self._h
        self._bitmap = [None] * (self._m + 1)

        self._num_empty = len(points)
        for p in points:
            self._bitmap[p[0] + p[1] * self._w] = EMPTY
        self._bitmap[self._m] = EMPTY
        # print(f"pixels={len(points)} {self._w}x{self._h}")

    def not_covered(self):
        assert self._bitmap[self._m] == EMPTY
        assert self._num_empty + 1 == self._bitmap.count(EMPTY)
        return self._num_empty

    def lowest_left(self) -> Optional[POINT]:
        p = self._bitmap.index(EMPTY)
        x = p % self._w
        y = p // self._w
        if y == self._h:
            return None
        else:
            return (x, y)

    def does_it_fit(self, ll: POINT, piece: List[POINT]) -> bool:
        for p in piece:
            x = ll[0] + p[0]
            y = ll[1] + p[1]
            if x < 0 or x >= self._w or y < 0 or y >= self._h:
                return False
            px = x + y * self._w
            if self._bitmap[px] != EMPTY:
                return False
        return True

    def cover(self, ll: POINT, piece: List[POINT], tag):
        assert tag != EMPTY
        assert self._bitmap[self._m] == EMPTY
        for p in piece:
            x = ll[0] + p[0]
            y = ll[1] + p[1]
            px = x + y * self._w
            # assert self._bitmap[px] == EMPTY

            self._bitmap[px] = tag
            self._num_empty -= 1

    def uncover(self, ll: POINT, piece: List[POINT]):
        for p in piece:
            x = ll[0] + p[0]
            y = ll[1] + p[1]
            px = x + y * self._w
            assert self._bitmap[px] != EMPTY
            self._bitmap[px] = EMPTY
            self._num_empty += 1

    def RenderCover(self):
        out = []

        def render_point(p) -> str:
            v = self._bitmap[p]
            if v is None:
                return "."
            elif v is EMPTY:
                return "."
            else:
                return chr(v + ord("a"))

        for y in range(self._h):
            line = [render_point(x + y * self._w) for x in range(self._w)]
            out.append("".join(line))
        return "\n".join(out)


FREE_PIECES = []
for i in range(100):
    a = TETRIES_PIECES_NORMAL[:]
    b = TETRIES_PIECES_CHEATS[:]
    random.shuffle(a)
    random.shuffle(b)
    FREE_PIECES.append(a+b)


def FindCover(c: Covering, first_approx, verbose=False):
    best_so_far = c.not_covered()
    # contains tuples: (lower-left,index,piece-list)
    stack = []

    while True:
        ep = c.not_covered()
        if ep < best_so_far:
            if verbose:
                print(f"New best={ep}")
            # if ep < first_approx:
            #    print(c.RenderCover())
            best_so_far = ep

        backtrack = True
        if ep == 0:
            cheats = 0
            for x in c._bitmap:
                if x in CHEAT_PIECES:
                    cheats += 1
            yield ep, cheats // 3, stack
        else:
            ll = c.lowest_left()
            if 1:
                a = TETRIES_PIECES_NORMAL[:]
                b = TETRIES_PIECES_CHEATS[:]
                random.shuffle(a)
                random.shuffle(b)
                pieces = a + b
            else:
                pieces = FREE_PIECES[len(stack)]

            for n, piece in enumerate(pieces):
                if c.does_it_fit(ll, piece):
                    # print(f"# add1 {ll} {n}")
                    c.cover(ll, piece, n)
                    stack.append((ll, n, pieces))
                    backtrack = False
                    break

        while backtrack:
            ll, p, pieces = stack.pop(-1)
            c.uncover(ll, pieces[p])
            # print(f"# rem {ll} {n}")
            for n, piece in enumerate(pieces):
                if n <= p:
                    continue
                if c.does_it_fit(ll, piece):
                    # print(f"# add2 {ll} {n}")
                    c.cover(ll, piece, n)
                    stack.append((ll, n, pieces))
                    backtrack = False
                    break


def CheckSurface(surface):
    points = []
    w, h = surface.size
    for y in range(h):
        for x in range(w):
            pixel = surface.getpixel((x, y))
            if pixel[0] == 0:
                points.append((x, y))
    covering = Covering(points, w, h)
    for x, cheats, patterns in FindCover(covering, 20):
        print("")
        print(f"Stats: ep={x} cheats={cheats} pieces={len(patterns)}")
        print(covering.RenderCover())
        for ll, index, all in patterns:
            print(ll, all[index], end=" ")
        print()
        return patterns


def CmpPieces(piece1, piece2):
    (o1x, o1y), p1 = piece1
    (o2x, o2y), p2, = piece2
    maxy1 = max(o1y + y for _, y in p1)
    maxy2 = max(o2y + y for _, y in p2)
    if maxy1 < maxy2:
        return 1
    if maxy2 > maxy1:
        return -1

    pm = {}
    for x, y in p1:
        pm[x + o1x] = min(pm.get(x + o1x, y + o1y),  y + o1y)
    for x, y in p2:
        if pm.get(x + o2x, y + o2y) < y + o2y:
            return 1
    return -1


def SortPieces(pieces):
    return sorted(pieces, key=functools.cmp_to_key(CmpPieces))


def MakeFontTab(font, font_size, chars):
    font = ImageFont.truetype(font, font_size)
    max_w = 0
    max_h = 0
    for c in chars:
        l, t, r, b = font.getbbox(c)
        if r > max_w:
            max_w = r
        if b > max_h:
            max_h = b
    print(f"Dim: {max_w}x{max_h}")
    txt = Image.new("RGBA", (max_w, max_h), BLACK)
    draw = ImageDraw.Draw(txt)
    out = {}
    for c in chars:
        draw.rectangle((0, 0) + (max_w, max_h),  fill=WHITE)
        draw.text((0, 0), c, font=font, fill=BLACK)

        # print(bitmap)
        print(f"\nNew char: [{c}] ")
        print(DumpSurface(txt))
        patterns = CheckSurface(txt)
        out[c] = SortPieces([(ll, all[index])
                             for ll, index, all in patterns])

    return (max_w, max_h), out


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
    args = parser.parse_args()

    font = ImageFont.truetype(args.font_path, args.font_size)
    l, t, r, b = font.getbbox(args.text)
    txt = Image.new("RGBA", (r, b), BLACK)
    draw = ImageDraw.Draw(txt)
    draw.rectangle((0, 0) + (r, b),  fill=WHITE)
    draw.text((0, 0), args.text, font=font, fill=BLACK)
    print(DumpSurface(txt))
    MakeFontTab(args.font_path, args.font_size, args.text)

if __name__ == '__main__':
    main()
