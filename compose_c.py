# THE SOUTHERN WIRE — NI25 Akun 15 (@sukmawatihss) — Varian C rebuild.
# Pure stdlib raster front page: layered full scenes, full decks, clean
# source/certainty foot lines, chip as badge over the scene.
# Written fresh in this session for the v2 repo (southern-wire).
import zlib, struct

W = H = 1024

def png_bytes(img):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += img[y * stride:(y + 1) * stride]
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)
    def set(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(col)
    def rect(self, x, y, w, h, col):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(col) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row
    def frame(self, x, y, w, h, col, t=1):
        self.rect(x, y, w, t, col); self.rect(x, y + h - t, w, t, col)
        self.rect(x, y, t, h, col); self.rect(x + w - t, y, t, h, col)
    def line(self, x0, y0, x1, y1, col, t=1):
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            x = x0 + dx * i // steps; y = y0 + dy * i // steps
            self.rect(x - t // 2, y - t // 2, t, t, col)
    def circle(self, cx, cy, r, col, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if d <= r * r and (fill or d >= (r - 1) ** 2):
                    self.set(xx, yy, col)
    def tri(self, x0, y0, x1, y1, x2, y2, col):
        minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
        miny, maxy = min(y0, y1, y2), max(y0, y1, y2)
        def edge(ax, ay, bx, by, px, py):
            return (px - ax) * (by - ay) - (py - ay) * (bx - ax)
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                d0 = edge(x0, y0, x1, y1, xx, yy)
                d1 = edge(x1, y1, x2, y2, xx, yy)
                d2 = edge(x2, y2, x0, y0, xx, yy)
                if (d0 >= 0 and d1 >= 0 and d2 >= 0) or (d0 <= 0 and d1 <= 0 and d2 <= 0):
                    self.set(xx, yy, col)
    def blit(self, src, x, y):
        for yy in range(src.h):
            i = ((y + yy) * self.w + x) * 3
            j = yy * src.w * 3
            self.px[i:i + src.w * 3] = src.px[j:j + src.w * 3]
    def text(self, x, y, txt, col, sx=2.0, sy=2.0):
        cx = x
        for ch in txt:
            g = FONT.get(ch, FONT[" "])
            for r in range(7):
                bits = g[r]
                for c in range(5):
                    if bits & (1 << (4 - c)):
                        self.rect(int(cx + c * sx), int(y + r * sy),
                                  max(1, int(sx)), max(1, int(sy)), col)
            cx += 6 * sx
        return cx - x

def text_w(txt, sx=2.0):
    return int(len(txt) * 6 * sx)

def wrap(txt, maxchars):
    words, lines, cur = txt.split(), [], ""
    for wd in words:
        if len(cur) + (1 if cur else 0) + len(wd) <= maxchars:
            cur = (cur + " " + wd) if cur else wd
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return lines

FONT = {
"A": (0x0E,0x11,0x11,0x1F,0x11,0x11,0x11), "B": (0x1E,0x11,0x11,0x1E,0x11,0x11,0x1E),
"C": (0x0E,0x11,0x10,0x10,0x10,0x11,0x0E), "D": (0x1C,0x12,0x11,0x11,0x11,0x12,0x1C),
"E": (0x1F,0x10,0x10,0x1E,0x10,0x10,0x1F), "F": (0x1F,0x10,0x10,0x1E,0x10,0x10,0x10),
"G": (0x0E,0x11,0x10,0x17,0x11,0x11,0x0F), "H": (0x11,0x11,0x11,0x1F,0x11,0x11,0x11),
"I": (0x0E,0x04,0x04,0x04,0x04,0x04,0x0E), "J": (0x07,0x02,0x02,0x02,0x02,0x12,0x0C),
"K": (0x11,0x12,0x14,0x18,0x14,0x12,0x11), "L": (0x10,0x10,0x10,0x10,0x10,0x10,0x1F),
"M": (0x11,0x1B,0x15,0x15,0x11,0x11,0x11), "N": (0x11,0x19,0x15,0x13,0x11,0x11,0x11),
"O": (0x0E,0x11,0x11,0x11,0x11,0x11,0x0E), "P": (0x1E,0x11,0x11,0x1E,0x10,0x10,0x10),
"Q": (0x0E,0x11,0x11,0x11,0x15,0x12,0x0D), "R": (0x1E,0x11,0x11,0x1E,0x14,0x12,0x11),
"S": (0x0F,0x10,0x10,0x0E,0x01,0x01,0x1E), "T": (0x1F,0x04,0x04,0x04,0x04,0x04,0x04),
"U": (0x11,0x11,0x11,0x11,0x11,0x11,0x0E), "V": (0x11,0x11,0x11,0x11,0x11,0x0A,0x04),
"W": (0x11,0x11,0x11,0x15,0x15,0x1B,0x11), "X": (0x11,0x0A,0x04,0x04,0x04,0x0A,0x11),
"Y": (0x11,0x0A,0x04,0x04,0x04,0x04,0x04), "Z": (0x1F,0x01,0x02,0x04,0x08,0x10,0x1F),
"a": (0x00,0x00,0x0E,0x01,0x0F,0x11,0x0F), "b": (0x10,0x10,0x16,0x19,0x11,0x11,0x1E),
"c": (0x00,0x00,0x0E,0x10,0x10,0x11,0x0E), "d": (0x01,0x01,0x0D,0x13,0x11,0x11,0x0F),
"e": (0x00,0x00,0x0E,0x11,0x1F,0x10,0x0E), "f": (0x06,0x08,0x1E,0x08,0x08,0x08,0x08),
"g": (0x00,0x00,0x0F,0x11,0x0F,0x01,0x0E), "h": (0x10,0x10,0x16,0x19,0x11,0x11,0x11),
"i": (0x04,0x00,0x0C,0x04,0x04,0x04,0x0E), "j": (0x02,0x00,0x06,0x02,0x02,0x12,0x0C),
"k": (0x10,0x10,0x12,0x14,0x18,0x14,0x12), "l": (0x0C,0x04,0x04,0x04,0x04,0x04,0x0E),
"m": (0x00,0x00,0x1A,0x15,0x15,0x15,0x15), "n": (0x00,0x00,0x16,0x19,0x11,0x11,0x11),
"o": (0x00,0x00,0x0E,0x11,0x11,0x11,0x0E), "p": (0x00,0x00,0x1E,0x11,0x1E,0x10,0x10),
"q": (0x00,0x00,0x0D,0x13,0x0F,0x01,0x01), "r": (0x00,0x00,0x16,0x19,0x10,0x10,0x10),
"s": (0x00,0x00,0x0F,0x10,0x0E,0x01,0x1E), "t": (0x08,0x08,0x1E,0x08,0x08,0x09,0x06),
"u": (0x00,0x00,0x11,0x11,0x11,0x13,0x0D), "v": (0x00,0x00,0x11,0x11,0x11,0x0A,0x04),
"w": (0x00,0x00,0x11,0x15,0x15,0x1B,0x11), "x": (0x00,0x00,0x11,0x0A,0x04,0x0A,0x11),
"y": (0x00,0x00,0x11,0x11,0x0F,0x01,0x0E), "z": (0x00,0x00,0x1F,0x02,0x04,0x08,0x1F),
"0": (0x0E,0x11,0x13,0x15,0x19,0x11,0x0E), "1": (0x04,0x0C,0x04,0x04,0x04,0x04,0x0E),
"2": (0x0E,0x11,0x01,0x02,0x04,0x08,0x1F), "3": (0x1F,0x02,0x04,0x02,0x01,0x11,0x0E),
"4": (0x02,0x06,0x0A,0x12,0x1F,0x02,0x02), "5": (0x1F,0x10,0x1E,0x01,0x01,0x11,0x0E),
"6": (0x06,0x08,0x10,0x1E,0x11,0x11,0x0E), "7": (0x1F,0x01,0x02,0x04,0x08,0x08,0x08),
"8": (0x0E,0x11,0x11,0x0E,0x11,0x11,0x0E), "9": (0x0E,0x11,0x11,0x0F,0x01,0x02,0x0C),
" ": (0,0,0,0,0,0,0), ".": (0,0,0,0,0,0x0C,0x0C), ",": (0,0,0,0,0x0C,0x04,0x08),
"'": (0x04,0x04,0x08,0,0,0,0), ":": (0,0x0C,0x0C,0,0x0C,0x0C,0), ";": (0,0x0C,0x0C,0,0x0C,0x04,0x08),
"-": (0,0,0,0x1F,0,0,0), "/": (0x01,0x01,0x02,0x04,0x08,0x10,0x10),
"+": (0,0x04,0x04,0x1F,0x04,0x04,0), "%": (0x18,0x19,0x02,0x04,0x08,0x13,0x03),
"(": (0x02,0x04,0x08,0x08,0x08,0x04,0x02), ")": (0x08,0x04,0x02,0x02,0x02,0x04,0x08),
"·": (0,0,0,0x0C,0x0C,0,0), "&": (0x0C,0x12,0x14,0x08,0x15,0x12,0x0D),
"!": (0x04,0x04,0x04,0x04,0x04,0,0x04), "?": (0x0E,0x11,0x01,0x02,0x04,0,0x04),
"$": (0x04,0x0F,0x14,0x0E,0x05,0x1E,0x04), "=": (0,0,0x1F,0,0x1F,0,0),
"#": (0x0A,0x0A,0x1F,0x0A,0x1F,0x0A,0x0A),
}

# ---------- palette: burgundy + pale silver ----------
PAPER  = (233, 230, 222)
CARD   = (242, 240, 234)
INK    = (28, 23, 20)
BURG   = (96, 17, 33)
BURG_D = (56, 8, 20)
SILVER = (172, 168, 159)
SILV_L = (205, 202, 193)
MUTE   = (96, 90, 82)
SKY    = (166, 178, 188)
SKY_D  = (122, 140, 154)
SEA    = (94, 122, 138)
SEA_D  = (62, 88, 104)
SAND   = (208, 188, 150)
SAND_D = (176, 152, 108)
OLIVE  = (110, 118, 84)
OLIVE_D= (78, 88, 58)
EARTH  = (140, 106, 74)
SMOKE  = (120, 116, 110)
WHITE  = (246, 245, 240)
GOLD   = (188, 152, 84)

def scene_base(w, h, sky, ground, gy):
    c = Canvas(w, h, sky)
    c.rect(0, gy, w, h - gy, ground)
    return c

def sc_awacs(w, h):  # #1 NATO AWACS over Poland runway
    gy = int(h * 0.72)
    c = scene_base(w, h, SKY, (88, 94, 88), gy)
    c.rect(0, 6, w, 10, SKY_D); c.rect(0, 22, w, 6, (188, 198, 206))
    for x in (14, 60, 210, 258):
        c.rect(x, 12, 26, 7, WHITE); c.rect(x + 6, 7, 14, 6, WHITE)
    c.rect(0, gy, w, 5, (60, 62, 60))
    for x in range(8, w, 26):
        c.rect(x, gy + 9, 12, 3, (214, 210, 190))
    # AWACS body, subject front
    by = int(h * 0.40)
    c.rect(int(w * 0.10), by, int(w * 0.74), 15, WHITE)
    c.tri(int(w * 0.84), by, int(w * 0.97), by + 7, int(w * 0.84), by + 14, WHITE)
    c.tri(int(w * 0.10), by - 16, int(w * 0.20), by, int(w * 0.10), by, BURG)
    c.rect(int(w * 0.12), by - 15, 12, 14, WHITE); c.rect(int(w * 0.12), by - 15, 12, 7, BURG)
    c.tri(int(w * 0.36), by + 12, int(w * 0.58), by + 12, int(w * 0.47), by + 30, SKY_D)
    c.circle(int(w * 0.47), by - 12, 13, INK)          # radar dome
    c.rect(int(w * 0.455), by - 4, 4, 6, INK)
    for i in range(7):
        c.rect(int(w * 0.22) + i * 13, by + 4, 5, 5, SKY_D)
    c.rect(int(w * 0.30), gy - 4, 5, 6, INK); c.rect(int(w * 0.68), gy - 4, 5, 6, INK)
    return c

def sc_hormuz(w, h):  # #2 tankers + mines in the strait
    gy = int(h * 0.30)
    c = scene_base(w, h, SKY, SEA, gy)
    c.tri(0, gy, int(w * 0.30), int(h * 0.06), int(w * 0.46), gy, SAND_D)   # headland
    c.tri(int(w * 0.60), gy, int(w * 0.84), int(h * 0.10), w, gy, SAND_D)
    for i, (fx, fy, s) in enumerate(((0.16, 0.52, 1.0), (0.52, 0.64, 0.8), (0.78, 0.46, 0.66))):
        x, y, L = int(w * fx), int(h * fy), int(w * 0.30 * s)
        c.rect(x, y, L, int(9 * s) + 3, BURG_D if i == 0 else INK)
        c.rect(x + 4, y - int(8 * s), int(L * 0.62), int(8 * s), (196, 120, 84) if i != 1 else SILVER)
        c.rect(x + int(L * 0.74), y - int(11 * s), int(L * 0.14), int(11 * s), WHITE)
        c.line(x, y + int(11 * s), x + L, y + int(11 * s), WHITE, 1)
    for (fx, fy) in ((0.36, 0.82), (0.63, 0.86), (0.88, 0.74)):
        cx, cy = int(w * fx), int(h * fy)
        c.circle(cx, cy, 5, INK)
        for dx, dy in ((0, -8), (6, -5), (8, 1), (-6, -5), (-8, 1), (0, 4)):
            c.line(cx, cy, cx + dx, cy + dy, INK, 1)
    c.circle(int(w * 0.08), int(h * 0.80), 4, GOLD); c.rect(int(w * 0.08) - 1, int(h * 0.80) - 10, 2, 8, GOLD)
    return c

def sc_iraq(w, h):  # #3 Kurdish oilfields: pumpjacks, tanks, mountains
    gy = int(h * 0.66)
    c = scene_base(w, h, (216, 186, 140), SAND, gy)
    c.circle(int(w * 0.86), int(h * 0.16), 13, GOLD)
    c.tri(0, gy, int(w * 0.30), int(h * 0.16), int(w * 0.55), gy, (150, 128, 104))
    c.tri(int(w * 0.34), gy, int(w * 0.62), int(h * 0.24), int(w * 0.92), gy, (164, 142, 116))
    c.tri(int(w * 0.245), int(h * 0.30), int(w * 0.30), int(h * 0.16), int(w * 0.355), int(h * 0.30), WHITE)
    for fx in (0.16, 0.60):  # pumpjacks
        x, y = int(w * fx), gy
        c.line(x, y, x + 8, y - 34, INK, 3); c.line(x + 8, y - 34, x + 44, y - 26, INK, 3)
        c.line(x + 44, y - 26, x + 44, y - 12, INK, 2); c.rect(x + 40, y - 12, 9, 8, BURG)
        c.line(x + 20, y - 30, x + 26, y, INK, 2); c.rect(x - 4, y - 3, 56, 4, INK)
    for i, fx in enumerate((0.80, 0.90)):  # storage tanks
        x = int(w * fx)
        c.rect(x, gy - 24, 26, 24, SILV_L); c.rect(x, gy - 24, 26, 5, SILVER)
        c.line(x, gy - 24, x + 26, gy - 24, INK, 1)
    c.line(int(w * 0.05), gy + 8, int(w * 0.97), gy + 8, BURG_D, 3)  # pipeline
    return c

def sc_gaza(w, h):  # #4 skyline, smoke, drone
    gy = int(h * 0.78)
    c = scene_base(w, h, (196, 178, 160), (104, 94, 84), gy)
    c.circle(int(w * 0.12), int(h * 0.16), 12, (226, 200, 140))
    hs = (0.52, 0.38, 0.60, 0.44, 0.56, 0.34, 0.50)
    for i, fh in enumerate(hs):
        x = int(w * (0.03 + i * 0.135)); bh = int(h * fh)
        c.rect(x, gy - bh, int(w * 0.115), bh, (84, 76, 70))
        for wy in range(gy - bh + 6, gy - 6, 11):
            for wx in range(x + 4, x + int(w * 0.115) - 4, 10):
                c.rect(wx, wy, 4, 5, (232, 206, 130))
    for fx in (0.30, 0.66):  # smoke plumes
        x = int(w * fx)
        for i in range(4):
            c.circle(x + i * 5, gy - int(h * 0.52) - i * 9, 8 - i, SMOKE)
    dx, dy = int(w * 0.74), int(h * 0.18)  # drone
    c.rect(dx - 10, dy - 2, 20, 5, INK)
    for sx in (-16, 16):
        c.line(dx, dy, dx + sx, dy - 6, INK, 1); c.circle(dx + sx, dy - 7, 4, INK, fill=False)
    c.circle(dx, dy + 6, 3, BURG)
    return c

def sc_count(w, h):  # #6 field of markers, 700,000 dead
    gy = int(h * 0.24)
    c = scene_base(w, h, (148, 156, 150), OLIVE_D, gy)
    c.rect(0, gy, w, 3, OLIVE)
    c.circle(int(w * 0.90), int(h * 0.12), 9, (226, 214, 170))
    for row in range(5):
        y = int(h * (0.36 + row * 0.13)); n = 9 - row
        for i in range(n):
            x = int(w * (0.08 + i * 0.095 + row * 0.02))
            s = 5 + row
            c.rect(x, y - s, 2, s, WHITE); c.rect(x - 3, y - s + 3, 8, 2, WHITE)
    c.rect(int(w * 0.05), int(h * 0.30), 3, int(h * 0.30), EARTH)  # lone tree
    c.circle(int(w * 0.05) + 1, int(h * 0.26), 12, OLIVE)
    return c

def sc_colombia(w, h):  # #8 car bomb street scene
    gy = int(h * 0.70)
    c = scene_base(w, h, SKY, (120, 112, 104), gy)
    for i, (fx, fh) in enumerate(((0.04, 0.46), (0.80, 0.54), (0.62, 0.38))):
        x = int(w * fx); bh = int(h * fh)
        c.rect(x, gy - bh, int(w * 0.17), bh, (150, 142, 132))
        for wy in range(gy - bh + 5, gy - 5, 10):
            c.rect(x + 4, wy, 4, 5, (232, 206, 130)); c.rect(x + 11, wy, 4, 5, SKY_D)
    cx, cy = int(w * 0.42), gy - 8  # car
    c.rect(cx - 26, cy - 10, 52, 11, BURG_D); c.rect(cx - 15, cy - 19, 30, 10, BURG)
    c.circle(cx - 15, cy + 2, 6, INK); c.circle(cx + 16, cy + 2, 6, INK)
    for ang in range(8):  # burst
        import math
        a = ang * 0.785
        x2 = cx + int(34 * math.cos(a)); y2 = cy - 16 + int(26 * math.sin(a))
        c.line(cx, cy - 16, x2, y2, GOLD, 2)
    c.circle(cx, cy - 16, 6, (238, 190, 90))
    c.rect(int(w * 0.06), gy - 26, 3, 26, OLIVE_D); c.circle(int(w * 0.06), gy - 30, 10, OLIVE)
    return c

def sc_senegal(w, h):  # #18 AFCON trophy restored
    gy = int(h * 0.76)
    c = scene_base(w, h, (150, 168, 150), OLIVE, gy)
    c.rect(0, int(h * 0.10), w, int(h * 0.30), (128, 146, 128))  # stadium arc
    c.rect(0, int(h * 0.10), w, 4, WHITE)
    for x in range(6, w, 14):
        c.rect(x, int(h * 0.16), 5, 5, (226, 214, 170)); c.rect(x, int(h * 0.26), 5, 5, SILVER)
    tx, ty = int(w * 0.50), int(h * 0.46)  # trophy
    c.rect(tx - 13, ty - 22, 26, 18, GOLD); c.rect(tx - 3, ty - 4, 6, 10, GOLD)
    c.rect(tx - 9, ty + 6, 18, 4, GOLD)
    c.circle(tx - 18, ty - 16, 6, GOLD, fill=False); c.circle(tx + 18, ty - 16, 6, GOLD, fill=False)
    c.rect(int(w * 0.08), int(h * 0.14), 30, 8, (46, 110, 60)); c.rect(int(w * 0.08), int(h * 0.14) + 8, 30, 8, (232, 206, 90)); c.rect(int(w * 0.08), int(h * 0.14) + 16, 30, 8, BURG)
    c.circle(int(w * 0.84), gy - 10, 9, WHITE); c.circle(int(w * 0.84), gy - 10, 9, INK, fill=False)
    return c

def sc_xiamen(w, h):  # #10 Boeing 737 on apron
    gy = int(h * 0.74)
    c = scene_base(w, h, SKY, (128, 130, 128), gy)
    c.rect(0, gy, w, 4, (96, 98, 96))
    for x in (20, 90, 230):
        c.rect(x, 10, 24, 6, WHITE); c.rect(x + 5, 5, 13, 5, WHITE)
    by = int(h * 0.42)
    c.rect(int(w * 0.06), by, int(w * 0.80), 14, WHITE)
    c.tri(int(w * 0.86), by, int(w * 0.98), by + 6, int(w * 0.86), by + 13, WHITE)
    c.tri(int(w * 0.06), by - 20, int(w * 0.17), by, int(w * 0.06), by, SEA_D)
    c.rect(int(w * 0.075), by - 19, 10, 18, SEA_D)
    c.tri(int(w * 0.40), by + 11, int(w * 0.62), by + 11, int(w * 0.51), by + 28, SKY_D)
    for i in range(9):
        c.rect(int(w * 0.20) + i * 11, by + 4, 4, 4, SEA_D)
    c.rect(int(w * 0.28), gy - 3, 4, 5, INK); c.rect(int(w * 0.70), gy - 3, 4, 5, INK)
    c.text(int(w * 0.30), by - 12, "50 ON ORDER", BURG, 1.2, 1.2)
    return c

def sc_coral(w, h):  # #13 Acropora reef
    c = Canvas(w, h, SEA)
    c.rect(0, 0, w, int(h * 0.30), SEA_D)
    for i in range(6):
        c.line(int(w * (0.1 + i * 0.16)), 0, int(w * (0.04 + i * 0.16)), int(h * 0.4), (150, 180, 190), 1)
    gy = int(h * 0.84); c.rect(0, gy, w, h - gy, SAND_D)
    def branch(x, y, s, col):
        c.line(x, y, x, y - int(16 * s), col, 3)
        for dx, dy in ((-10, -12), (10, -12), (-6, -20), (7, -22)):
            c.line(x, y - int(10 * s), x + int(dx * s), y - int(10 * s) + int(dy * s), col, 2)
            c.circle(x + int(dx * s), y - int(10 * s) + int(dy * s), 2, col)
    branch(int(w * 0.24), gy + 4, 1.15, (216, 120, 110))
    branch(int(w * 0.52), gy + 6, 1.4, (226, 150, 120))
    branch(int(w * 0.78), gy + 4, 1.0, (200, 105, 120))
    for (fx, fy) in ((0.36, 0.34), (0.64, 0.26), (0.84, 0.44)):
        x, y = int(w * fx), int(h * fy)
        c.tri(x, y, x + 14, y + 4, x, y + 8, GOLD); c.circle(x + 2, y + 4, 3, GOLD)
    for (fx, fy) in ((0.15, 0.2), (0.45, 0.14), (0.7, 0.55)):
        c.circle(int(w * fx), int(h * fy), 2, (200, 220, 226), fill=False)
    return c

def sc_fiji(w, h):  # #14 dry island, cracked earth
    gy = int(h * 0.62)
    c = scene_base(w, h, (222, 196, 148), SAND_D, gy)
    c.circle(int(w * 0.82), int(h * 0.16), 14, (240, 206, 110))
    c.rect(0, int(h * 0.44), w, int(h * 0.18), SEA)
    c.tri(0, gy, int(w * 0.3), int(h * 0.36), int(w * 0.55), gy, OLIVE_D)
    for fx in (0.16, 0.40):
        x = int(w * fx)
        c.line(x, gy - 6, x + 3, gy - 30, EARTH, 3)
        for dx in (-12, -5, 4, 12):
            c.line(x + 3, gy - 30, x + 3 + dx, gy - 40, OLIVE, 2)
    for i in range(5):  # cracks
        x = int(w * (0.08 + i * 0.2)); y = int(h * 0.78)
        c.line(x, y, x + 12, y + 6, EARTH, 1); c.line(x + 12, y + 6, x + 6, y + 13, EARTH, 1)
    return c

def sc_punjab(w, h):  # #23 two flags reunite over wheat
    gy = int(h * 0.70)
    c = scene_base(w, h, SKY, (206, 178, 110), gy)
    for fx, col in ((0.30, (232, 140, 60)), (0.68, (70, 130, 180))):
        x = int(w * fx)
        c.rect(x, int(h * 0.14), 3, int(h * 0.52), INK)
        c.rect(x + 3, int(h * 0.14), 34, 20, col); c.rect(x + 3, int(h * 0.14) + 20, 34, 3, WHITE)
    c.line(int(w * 0.44), int(h * 0.52), int(w * 0.56), int(h * 0.52), INK, 3)  # clasp
    c.circle(int(w * 0.50), int(h * 0.52), 5, BURG)
    for x in range(6, w, 12):  # wheat
        c.line(x, h, x + 3, h - 16, (170, 140, 70), 1); c.circle(x + 3, h - 18, 2, (190, 158, 84))
    return c

def sc_indonesia(w, h):  # #25 palace steps, flag, empty chair
    gy = int(h * 0.78)
    c = scene_base(w, h, SKY, (150, 146, 138), gy)
    c.rect(int(w * 0.16), int(h * 0.26), int(w * 0.68), 10, WHITE)
    c.tri(int(w * 0.10), int(h * 0.26), int(w * 0.50), int(h * 0.10), int(w * 0.90), int(h * 0.26), BURG_D)
    for i in range(5):
        x = int(w * (0.22 + i * 0.14))
        c.rect(x, int(h * 0.36), 9, int(h * 0.34), WHITE)
    c.rect(int(w * 0.16), int(h * 0.70), int(w * 0.68), 6, WHITE)
    for i in range(3):
        c.rect(int(w * (0.24 + i * 0.08)), gy + 4 + i * 5, int(w * (0.52 - i * 0.08)), 3, SILVER)
    c.rect(int(w * 0.47), int(h * 0.30), 3, int(h * 0.30), INK)  # flag
    c.rect(int(w * 0.47) + 3, int(h * 0.30), 22, 7, BURG); c.rect(int(w * 0.47) + 3, int(h * 0.30) + 7, 22, 7, WHITE)
    cx = int(w * 0.80)  # empty chair
    c.rect(cx, gy - 20, 16, 4, EARTH); c.rect(cx, gy - 20, 3, 16, EARTH); c.rect(cx + 13, gy - 20, 3, 16, EARTH)
    return c

def sc_nvidia(w, h):  # #36 rising bars + chip
    gy = int(h * 0.80)
    c = scene_base(w, h, (40, 44, 40), (30, 33, 30), gy)
    c.rect(0, gy, w, 2, SILVER)
    bars = (0.16, 0.26, 0.22, 0.38, 0.34, 0.52, 0.68)
    for i, fb in enumerate(bars):
        x = int(w * (0.06 + i * 0.115)); bh = int(h * fb)
        c.rect(x, gy - bh, int(w * 0.085), bh, OLIVE if i < 6 else (140, 190, 90))
    pts = [(int(w * (0.10 + i * 0.115)), gy - int(h * b) - 6) for i, b in enumerate(bars)]
    for a, b in zip(pts, pts[1:]):
        c.line(a[0], a[1], b[0], b[1], GOLD, 2)
    lx, ly = pts[-1]
    c.tri(lx, ly, lx - 12, ly + 2, lx - 4, ly + 10, GOLD)
    cx, cy = int(w * 0.80), int(h * 0.16)  # chip
    c.rect(cx, cy, 30, 24, SILV_L); c.rect(cx + 8, cy + 6, 14, 12, SILVER)
    for i in range(3):
        c.rect(cx - 5, cy + 4 + i * 8, 5, 2, GOLD); c.rect(cx + 30, cy + 4 + i * 8, 5, 2, GOLD)
    return c

SCENES = {1: sc_awacs, 2: sc_hormuz, 3: sc_iraq, 4: sc_gaza, 6: sc_count,
          8: sc_colombia, 10: sc_xiamen, 13: sc_coral, 14: sc_fiji,
          18: sc_senegal, 23: sc_punjab, 25: sc_indonesia, 36: sc_nvidia}

# ---------- story data (numbers ONLY from ni25-pool.md) ----------
LEADS = [3, 1, 4]
GRID = [2, 6, 8, 18, 10, 13, 14, 23, 25, 36]
CARDS = {
 1: ("EUROPE · DEFENCE · POLAND", "NATO sends early-warning jets to Poland",
     "NATO plans AWACS deployment in Poland after Russian missiles landed there. Merz vows complete German support.",
     "WIRE REPORTS · REPORTED", "AWACS TO POLAND"),
 2: ("", "Iran says 3 tankers hit by mines",
     "Hormuz claim: 3 tankers hit mines; fears rise.",
     "IRGC CLAIM · CLAIMED", "3 TANKERS HIT"),
 3: ("MIDDLE EAST · OIL · IRAQ", "Baghdad orders Kurdish oilfields seized",
     "PM Ali al-Zaidi orders federal units to seize oilfields in Kurdish-run regions. Barzani refuses to submit.",
     "STARLIT · WIRES · REPORTED", "OILFIELDS ORDER"),
 4: ("MIDDLE EAST · WAR · GAZA", "Drone strikes kill Hamas security chief",
     "Drone strikes kill a Hamas security chief, three policemen and three siblings, one a child.",
     "AL JAZEERA · REPORTED", "7 KILLED IN STRIKES"),
 6: ("", "700,000 Russian dead, new count finds",
     "Count finds over 700000 Russian dead in Ukraine.",
     "RFE/RL · REPORTED", "700,000+ KILLED"),
 8: ("", "Car bomb: at least 23 hurt",
     "Colombia car bomb injures at least 23 people.",
     "WIRES · REPORTED", "23 INJURED"),
 10: ("", "Xiamen Airlines orders 50 Boeing jets",
     "Xiamen Airlines buys 50 Boeing 737-8 jets.",
     "WIRES · REPORTED", "50 JETS ORDERED"),
 13: ("", "12 coral species brought back",
     "Genetic study resurrects 12 Acropora coral species.",
     "SCIENCE · REPORTED", "12 SPECIES BACK"),
 14: ("", "Fiji declares disaster in dry spell",
     "Fiji declares disaster amid an El Nino dry spell.",
     "WIRES · REPORTED", "DISASTER DECLARED"),
 18: ("", "Senegal's AFCON title restored",
     "CAS ruling restores Senegal's 2025 AFCON title.",
     "WIRES · REPORTED", "TITLE RESTORED"),
 23: ("", "Old allies reunite in Punjab",
     "BJP, Akali Dal reunite for the 2027 Punjab polls.",
     "INDIAN WIRES · REPORTED", "ALLIANCE AGAIN"),
 25: ("", "Indonesia's vice-president resigns",
     "Indonesia's Vice-President resigns amid strain.",
     "STARLIT · REPORTED", "VP RESIGNS"),
 36: ("", "Nvidia's $1 trillion Monday",
     "Monday close: +31.5%, near $1 trillion clawed back.",
     "FORBES · REPORTED", "+31.5% MONDAY"),
}
BRIEFS = [
 (5, "EU unveils new Russia sanctions"), (7, "First Lynx KF41 vehicles arrive"),
 (9, "Gunmen hold dozens in Cartagena"), (11, "Madrid 5-1 PSV: Mbappe, Bellingham"),
 (12, "England level T20I: Fraser-McGurk"), (15, "Iran's pharmacies run dry"),
 (16, "Iran braces for winter gas lack"), (17, "Britain sanctions Houthis chiefs"),
 (19, "Rebels pull back in DR Congo"), (20, "Emir suspended in Nigeria case"),
 (21, "Sudan RSF commander defects"), (22, "Cameroon separatist in court"),
 (24, "Bangladesh opens Guangzhou post"), (26, "Solomon Islands eye Aussie pact"),
 (27, "North Korea touts China ties"), (28, "Denmark upholds ghetto law"),
 (29, "Sarkozy faces Libya-case trial"), (30, "Black Sea clash at the UN"),
 (31, "Shortwave school: Afghan girls"), (32, "Didymos, Dimorphos eclipse"),
 (33, "PCE inflation report due today"), (34, "US targets 7 firms, Alibaba one"),
 (35, "Moscow's inflatable decoys trick"), (37, "Storms target Thanksgiving trips"),
]
NUMSTRIP = [("3", "TANKERS · #2"), ("700000", "RUSSIAN DEAD · #6"),
            ("50", "BOEING JETS · #10"), ("12", "CORAL SPECIES · #13"),
            ("23", "INJURED · #8"), ("7", "KILLED · #4"), ("+31.5%", "NVIDIA MON · #36")]
REGIONS = [("EUROPE", 8, (70, 110, 170)), ("MIDEAST", 6, BURG), ("AFRICA", 5, (196, 148, 58)),
           ("AMERICAS", 4, (88, 148, 108)), ("ASIA", 2, (168, 90, 138)), ("S.ASIA", 2, (216, 128, 66)),
           ("ASIA-PAC", 2, (78, 158, 168)), ("OCEANIA", 2, SEA_D), ("WORLD", 6, INK)]
TIMELINE = ["OVERNIGHT · #4", "DAWN · #2", "MORNING · #3", "MIDDAY · #1", "EVENING · #36"]
WORLDMAP = [
"                                                ",
"     #####    #        #########  ######         ",
"   #########        #####################  ##    ",
"    #######  #     #########  ############       ",
"     #####        ######  #################      ",
"      ###  ##      ####    #####  ########  #    ",
"       #  ####      ##      ###    ######        ",
"         ######              ##     ####         ",
"          ####              ###      ##    ##    ",
"           ##         #    #####          ###    ",
"           ##        ##      ###           #     ",
"                        #     ##        #####    ",
"                                     #######     ",
"                                      #####      ",
"                                                ",
"                                                ",
]
PINS = {1: (24, 3), 2: (31, 7), 3: (30, 6), 4: (28, 7), 6: (26, 4), 8: (8, 9),
        10: (38, 6), 13: (42, 12), 14: (46, 12), 18: (20, 8), 23: (33, 6),
        25: (39, 9), 36: (5, 5)}

def badge(cv, x, y, txt, sx=1.6):
    w = text_w(txt, sx) + 10
    cv.rect(x, y, w, int(7 * sx) + 6, BURG)
    cv.text(x + 5, y + 3, txt, WHITE, sx, sx)
    return w

def fit_sx(txt, inner, options=(2.0, 1.8, 1.6, 1.4)):
    for sx in options:
        if text_w(txt, sx) <= inner:
            return sx
    return options[-1]

def draw_lead(cv, x, y, num):
    kick, head, deck, foot, chip = CARDS[num]
    cv.rect(x, y, 320, 296, CARD); cv.frame(x, y, 320, 296, INK, 1)
    cv.rect(x, y, 320, 4, BURG)
    cv.text(x + 10, y + 10, kick, BURG, 2, 2)
    hy = y + 28
    for ln in wrap(head.upper(), 16):
        cv.text(x + 10, hy, ln, INK, 3, 3); hy += 24
    sc = SCENES[num](300, 80)
    cv.blit(sc, x + 10, y + 104); cv.frame(x + 10, y + 104, 300, 80, INK, 1)
    badge(cv, x + 10, y + 104, chip, 1.6)
    dy = y + 192
    for ln in wrap(deck, 25):
        cv.text(x + 10, dy, ln, INK, 2, 2); dy += 15
    cv.rect(x + 10, y + 272, 300, 1, SILVER)
    cv.text(x + 10, y + 277, foot, MUTE, fit_sx(foot, 300), fit_sx(foot, 300))

def draw_grid(cv, x, y, num):
    kick, head, deck, foot, chip = CARDS[num]
    cv.rect(x, y, 189, 164, CARD); cv.frame(x, y, 189, 164, INK, 1)
    cv.rect(x, y, 22, 15, BURG); cv.text(x + 4, y + 3, str(num), WHITE, 1.4, 1.4)
    hy = y + 7
    for ln in wrap(head, 15)[:3]:
        cv.text(x + 27, hy, ln, INK, 1.9, 1.8); hy += 14
    sc = SCENES[num](173, 38)
    cv.blit(sc, x + 8, y + 51); cv.frame(x + 8, y + 51, 173, 38, INK, 1)
    badge(cv, x + 8, y + 51, chip, 1.2)
    dy = y + 94
    for ln in wrap(deck, 14)[:4]:
        cv.text(x + 8, dy, ln, INK, 2, 1.85); dy += 13.5
    cv.rect(x + 8, y + 149, 173, 1, SILVER)
    cv.text(x + 8, y + 152, foot, MUTE, 1.2, 1.2)

def render():
    cv = Canvas(W, H, PAPER)
    M = 22
    k = "37 STORIES FROM 9 REGIONS · EVERY FIGURE CHECKED BEFORE PRINT"
    cv.text((W - text_w(k, 2)) // 2, 12, k, BURG, 2, 2)
    cv.rect(M, 30, 980, 2, BURG); cv.rect(M, 34, 980, 1, SILVER)
    m = "THE SOUTHERN WIRE"
    cv.text((W - text_w(m, 7)) // 2, 38, m, BURG_D, 7, 7)
    cv.rect(M, 92, 980, 2, BURG); cv.rect(M, 96, 980, 1, SILVER)
    d = "TUESDAY 25 NOVEMBER 2026"
    cv.text((W - text_w(d, 4)) // 2, 102, d, BURG, 4, 4)
    # number strip
    cv.frame(M, 136, 980, 32, INK, 1)
    for i, (n, lab) in enumerate(NUMSTRIP):
        x = M + i * 140
        if i: cv.rect(x, 136, 1, 32, SILVER)
        cv.text(x + 7, 139, n, BURG, 2.6, 2.6)
        cv.text(x + 7, 159, lab, MUTE, 1, 1)
    # region strip
    cv.frame(M, 174, 980, 20, INK, 1)
    for i, (name, cnt, col) in enumerate(REGIONS):
        x = M + i * 109
        if i: cv.rect(x, 174, 1, 20, SILVER)
        cv.rect(x + 5, 180, 8, 8, col)
        cv.text(x + 17, 177, name + " " + str(cnt), INK, 1.8, 2)
    # timeline
    cv.frame(M, 200, 980, 20, INK, 1)
    for i, slot in enumerate(TIMELINE):
        x = M + i * 196
        if i: cv.rect(x, 200, 1, 20, SILVER)
        cv.rect(x + 6, 207, 5, 5, BURG)
        cv.text(x + 16, 203, slot, INK, 2, 2)
    # leads
    for i, num in enumerate(LEADS):
        draw_lead(cv, M + i * 330, 226, num)
    # grid 5 x 2
    for r, row in enumerate((GRID[:5], GRID[5:])):
        for cix, num in enumerate(row):
            draw_grid(cv, M + cix * 197, 530 + r * 168, num)
    # bottom: map + briefs
    by = 866
    cv.rect(M, by, 250, 128, (216, 212, 203)); cv.frame(M, by, 250, 128, INK, 1)
    cv.text(M + 8, by + 6, "WHERE THE WIRE RAN", BURG, 1.6, 1.6)
    for ri, rowtxt in enumerate(WORLDMAP):
        for ci, ch in enumerate(rowtxt):
            if ch == "#":
                cv.rect(M + 6 + ci * 5, by + 24 + ri * 5, 3, 3, (118, 112, 104))
    for num, (pc, pr) in PINS.items():
        px, py = M + 6 + pc * 5 - 4, by + 24 + pr * 5 - 3
        cv.rect(px, py, 12, 10, BURG)
        cv.text(px + 1, py + 1, str(num), WHITE, 0.85, 0.85)
    cv.text(M + 8, by + 112, "PINS = CARD NUMBERS", MUTE, 1.1, 1.1)
    bx = M + 264
    cv.text(bx, by, "ALSO ON THE WIRE — 24 MORE, NUMBERED TO 37", BURG, 2, 2)
    for i, (num, line) in enumerate(BRIEFS):
        col = i // 12; row = i % 12
        x = bx + col * 358; y = by + 18 + row * 9.5
        cv.text(x, y, str(num) + " · " + line, INK, 1.55, 1.2)
    dc = "DATE CHECK — HELD BACK: MERKURY (23 NOV) · COP31 OPENER · LIVERPOOL 4-0 · GTA VI TRAILER"
    cv.text(M, 1000, dc, BURG, 1.5, 1.5)
    ft = "SOURCES: RFE/RL · STARLIT DAILY · DW · AL JAZEERA · FORBES · WIRES — ALL FIGURES FROM THE WIRE POOL · ORIGINAL DRAWINGS BY THE SOUTHERN WIRE STUDIO"
    cv.text(M, 1014, ft, MUTE, fit_sx(ft, 980, (1.1, 1.0)), fit_sx(ft, 980, (1.1, 1.0)))
    # newsprint grain: deterministic speckle over the whole sheet
    px = cv.px
    for yy in range(H):
        base = yy * W * 3
        for xx in range(W):
            hh = (xx * 2654435761 + yy * 40503) & 0xffffffff
            hh ^= hh >> 13
            if hh % 5 == 0:
                i = base + xx * 3
                px[i] = px[i] * 86 // 100
                px[i + 1] = px[i + 1] * 86 // 100
                px[i + 2] = px[i + 2] * 86 // 100
    return png_bytes(cv.px)

def render_png():
    return render()
