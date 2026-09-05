#!/usr/bin/env python3
"""Generate houses.rbxlx v2 — Luxury Houses: 6 homes, multi-floor, full furniture library.
Pure stdlib. ~2K lines generator, 1000+ parts."""

import math
import os

R = 0


def ref():
    global R
    R += 1
    return f"RBX{R}"


def pack(r, g, b):
    return (255 << 24) | (r << 16) | (g << 8) | b


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- materials
PLASTIC = 256
SMOOTH = 272
NEON = 288
WOOD = 512
PLANKS = 528
MARBLE = 784
SLATE = 800
CONCRETE = 816
GRANITE = 832
BRICK = 848
COBBLE = 880
FABRIC = 1312
FOIL = 1072
GLASS = 1568
GRASS = 1280
METAL = 1088
SAND = 1296

# ---------------------------------------------------------------- palette
WHITE = (237, 237, 237)
OFFWHITE = (225, 222, 215)
GLASSC = (200, 225, 240)
WOODC = (133, 94, 66)
DARKWOOD = (87, 60, 42)
MAHOGANY = (110, 52, 38)
STONE = (130, 130, 134)
DARKSTONE = (95, 95, 100)
GOLD = (212, 175, 55)
SILVER = (192, 194, 200)
BRONZE = (140, 100, 60)
CARPET_RED = (150, 30, 35)
CARPET_PURPLE = (90, 60, 110)
CARPET_CREAM = (210, 195, 170)
MARBLEC = (235, 235, 240)
SOFA_GREY = (90, 95, 105)
SOFA_NAVY = (50, 60, 85)
SOFA_BEIGE = (190, 175, 150)
PATHC = (180, 178, 170)
POOL_WATER = (60, 160, 220)
WARM = (255, 220, 160)
FLAME = (255, 130, 40)
PLANTC = (60, 140, 70)
PLANT_DARK = (40, 100, 55)
FLOWER_RED = (220, 60, 60)
FLOWER_YELLOW = (235, 200, 60)
FLOWER_PINK = (230, 120, 160)
POTC = (140, 90, 60)
ROCKC = (120, 118, 112)
TRUNK = (100, 72, 48)
CAR_RED = (170, 40, 40)
CAR_BLACK = (25, 25, 28)
TIRE = (35, 35, 38)
TV_DARK = (20, 20, 24)
TV_SCREEN = (10, 60, 90)
BOOK_COLORS = [(160, 40, 40), (40, 80, 160), (40, 130, 70), (200, 160, 50),
               (130, 60, 140), (200, 200, 205), (90, 90, 95), (220, 130, 60)]

houses = {}  # name -> [xml]


def H(house, xml):
    houses.setdefault(house, []).append(xml)


# ---------------------------------------------------------------- core part
def part(name, size, pos, color, mat=PLASTIC, transparency=0.0,
         cancollide=True, shape=None, rotx=0.0, roty=0.0, rotz=0.0,
         cls="Part"):
    """One anchored part. Single-axis rotation only (rotx/roty/rotz degrees)."""
    x, y, z = pos
    sx, sy, sz = size
    if rotx:
        c, s = math.cos(math.radians(rotx)), math.sin(math.radians(rotx))
        m = ((1, 0, 0), (0, c, -s), (0, s, c))
    elif roty:
        c, s = math.cos(math.radians(roty)), math.sin(math.radians(roty))
        m = ((c, 0, s), (0, 1, 0), (-s, 0, c))
    elif rotz:
        c, s = math.cos(math.radians(rotz)), math.sin(math.radians(rotz))
        m = ((c, -s, 0), (s, c, 0), (0, 0, 1))
    else:
        m = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    (r00, r01, r02), (r10, r11, r12), (r20, r21, r22) = m
    shape_tok = ""
    if cls == "Part" and shape is not None:
        shape_tok = f'<token name="Shape">{shape}</token>'
    return (f'<Item class="{cls}" referent="{ref()}"><Properties>'
            f'<string name="Name">{esc(name)}</string>'
            f'<bool name="Anchored">true</bool>'
            f'<bool name="CanCollide">{str(cancollide).lower()}</bool>'
            f'<token name="Material">{mat}</token>'
            f'<Color3uint8 name="Color3uint8">{pack(*color)}</Color3uint8>'
            f'<float name="Transparency">{transparency}</float>'
            f'{shape_tok}'
            f'<Vector3 name="size"><X>{sx}</X><Y>{sy}</Y><Z>{sz}</Z></Vector3>'
            f'<CoordinateFrame name="CFrame"><X>{x}</X><Y>{y}</Y><Z>{z}</Z>'
            f'<R00>{r00:.6f}</R00><R01>{r01:.6f}</R01><R02>{r02:.6f}</R02>'
            f'<R10>{r10:.6f}</R10><R11>{r11:.6f}</R11><R12>{r12:.6f}</R12>'
            f'<R20>{r20:.6f}</R20><R21>{r21:.6f}</R21><R22>{r22:.6f}</R22>'
            f'</CoordinateFrame>'
            f'<token name="TopSurface">0</token>'
            f'<token name="BottomSurface">0</token>'
            f'</Properties></Item>')


BALL = 0
BLOCK = 1
CYL = 2


# ================================================================ FURNITURE
# Every builder appends to house `h`. Convention: y = floor surface height.

def f_sofa(h, x, y, z, color=SOFA_GREY, roty=0, w=6):
    """3-seat sofa: base, back, arms, cushions."""
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))

    def r(dx, dz):
        return (x + dx * ca - dz * sa, z + dx * sa + dz * ca)

    px, pz = r(0, 0)
    H(h, part("SofaBase", (w, 1, 2.2), (px, y + 0.5, pz), color, FABRIC, roty=roty))
    bx, bz = r(0, 1.0)
    H(h, part("SofaBack", (w, 2, 0.5), (bx, y + 2, bz), color, FABRIC, roty=roty))
    lx, lz = r(-w / 2 + 0.35, 0)
    rx, rz = r(w / 2 - 0.35, 0)
    H(h, part("SofaArmL", (0.7, 1.6, 2.2), (lx, y + 0.8, lz), color, FABRIC, roty=roty))
    H(h, part("SofaArmR", (0.7, 1.6, 2.2), (rx, y + 0.8, rz), color, FABRIC, roty=roty))
    for i in range(3):
        cx_, cz_ = r(-w / 2 + 1.1 + i * (w - 2.2) / 2, -0.05)
        H(h, part("SofaCushion", (w / 3 - 0.4, 0.35, 1.8),
                  (cx_, y + 1.15, cz_), (min(color[0] + 25, 255),
                                         min(color[1] + 25, 255),
                                         min(color[2] + 25, 255)),
                  FABRIC, roty=roty, cancollide=False))


def f_loveseat(h, x, y, z, color=SOFA_BEIGE, roty=0):
    f_sofa(h, x, y, z, color, roty, w=3.6)


def f_armchair(h, x, y, z, color=SOFA_NAVY, roty=0):
    f_sofa(h, x, y, z, color, roty, w=2.4)


def f_coffee_table(h, x, y, z, w=4, mat=GLASS, color=GLASSC, leg=GOLD):
    H(h, part("CoffeeTable", (w, 0.3, 2.2), (x, y + 1.1, z), color, mat))
    for dx in (-w / 2 + 0.3, w / 2 - 0.3):
        for dz in (-0.8, 0.8):
            H(h, part("TableLeg", (0.3, 1, 0.3), (x + dx, y + 0.5, z + dz),
                      leg, FOIL))
    H(h, part("TableShelf", (w - 0.6, 0.15, 1.8), (x, y + 0.45, z),
              DARKWOOD, WOOD, cancollide=False))


def f_dining(h, x, y, z, seats=6, w=7, mat=WOOD, color=DARKWOOD):
    """Dining table + `seats` chairs around it."""
    H(h, part("DiningTable", (w, 0.35, 3.4), (x, y + 1.55, z), color, mat))
    H(h, part("DiningRunner", (w - 1.5, 0.12, 1.1), (x, y + 1.8, z),
              CARPET_CREAM, FABRIC, cancollide=False))
    for dx in (-w / 2 + 0.5, 0, w / 2 - 0.5):
        H(h, part("TableLeg", (0.35, 1.4, 0.35), (x + dx, y + 0.7, z), color, mat))
    for i in range(seats):
        side = -1 if i % 2 == 0 else 1
        idx = i // 2
        cx_ = x - (w / 2 - 1) + idx * (w - 2) / max(seats // 2 - 1, 1)
        cz_ = z + side * 2.4
        H(h, part("ChairSeat", (1.3, 0.25, 1.3), (cx_, y + 1.0, cz_), color, WOOD))
        H(h, part("ChairBack", (1.3, 1.6, 0.25), (cx_, y + 1.8, cz_ + side * 0.55),
                  color, WOOD))
        for lx in (-0.5, 0.5):
            for lz in (-0.5, 0.5):
                H(h, part("ChairLeg", (0.15, 0.9, 0.15),
                          (cx_ + lx, y + 0.45, cz_ + lz), color, WOOD))
        H(h, part("ChairCushion", (1.1, 0.12, 1.1), (cx_, y + 1.19, cz_),
                  CARPET_CREAM, FABRIC, cancollide=False))


def f_chandelier(h, x, y, z, scale=1.0, tiers=2, bulbs_per=3):
    """Hanging chandelier, `tiers` rings of bulbs."""
    H(h, part("ChanRod", (0.2 * scale, 1.5 * scale, 0.2 * scale),
              (x, y + 0.75 * scale, z), GOLD, FOIL, cancollide=False))
    for t in range(tiers):
        rad = (1.2 + t * 0.9) * scale
        yy = y - t * 0.8 * scale
        H(h, part(f"ChanRing{t}", (0.12 * scale, 0.12 * scale, rad * 2),
                  (x, yy, z), GOLD, FOIL, roty=90, cancollide=False))
        H(h, part(f"ChanRingX{t}", (rad * 2, 0.12 * scale, 0.12 * scale),
                  (x, yy, z), GOLD, FOIL, cancollide=False))
        for i in range(bulbs_per):
            a = 2 * math.pi * i / bulbs_per
            H(h, part(f"ChanBulb{t}_{i}", (0.55 * scale, 0.55 * scale, 0.55 * scale),
                      (x + rad * math.cos(a), yy - 0.45 * scale,
                       z + rad * math.sin(a)), WARM, NEON, shape=BALL,
                      cancollide=False))


def f_rug(h, x, y, z, w=8, d=6, color=CARPET_RED, border=None):
    if border:
        H(h, part("RugBorder", (w + 0.6, 0.06, d + 0.6), (x, y + 0.03, z),
                  border, FABRIC, cancollide=False))
    H(h, part("Rug", (w, 0.08, d), (x, y + 0.06, z), color, FABRIC,
              cancollide=False))
    H(h, part("RugInlay", (w * 0.5, 0.06, d * 0.5), (x, y + 0.1, z),
              border or color, FABRIC, cancollide=False))


def f_tv(h, x, y, z, roty=0, w=5, on=True):
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))
    px, pz = x + sa * 0.15, z + ca * 0.15
    H(h, part("TVStand", (w, 1, 1.6), (x, y + 0.5, z), DARKWOOD, WOOD, roty=roty))
    H(h, part("TV", (w * 0.9, 3, 0.3), (px, y + 3.2, pz), TV_DARK, SMOOTH,
              roty=roty, cancollide=False))
    if on:
        sx, sz = x - sa * 0.1, z - ca * 0.1
        H(h, part("TVPanel", (w * 0.82, 2.7, 0.1), (sx, y + 3.2, sz),
                  TV_SCREEN, NEON, roty=roty, cancollide=False))


def f_bed(h, x, y, z, roty=0, round_=False, size=1.0, color=MARBLEC,
          headcolor=DARKWOOD):
    """Bed: base, mattress, pillows, headboard. size scales length/width."""
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))

    def r(dx, dz):
        return (x + dx * ca - dz * sa, z + dx * sa + dz * ca)

    if round_:
        H(h, part("BedBase", (0.9 * size, 5 * size, 5 * size),
                  (x, y + 0.45 * size, z), color, FABRIC, shape=CYL, rotz=90))
        H(h, part("BedPillow", (0.5, 2.2 * size, 2.2 * size),
                  (x, y + 1.15 * size, z - 1.2 * size), (250, 250, 250),
                  FABRIC, shape=CYL, cancollide=False))
        return
    w, d = 4.5 * size, 6.5 * size
    px, pz = r(0, 0)
    H(h, part("BedBase", (w, 0.9, d), (px, y + 0.45, pz), color, FABRIC, roty=roty))
    H(h, part("BedMattress", (w - 0.4, 0.5, d - 0.4), (px, y + 1.1, pz),
              (245, 245, 250), FABRIC, roty=roty, cancollide=False))
    H(h, part("BedBlanket", (w - 0.2, 0.25, d * 0.62), (px, y + 1.4, pz),
              CARPET_PURPLE, FABRIC, roty=roty, cancollide=False))
    hx, hz = r(0, -d / 2 + 1.2)
    H(h, part("BedPillow", (w - 1.5, 0.7, 1.4), (hx, y + 1.55, hz),
              (255, 255, 255), FABRIC, roty=roty, cancollide=False))
    bx, bz = r(0, -d / 2 - 0.15)
    H(h, part("BedHead", (w, 2.8, 0.35), (bx, y + 1.75, bz), headcolor, WOOD,
              roty=roty))


def f_nightstand(h, x, y, z, roty=0):
    H(h, part("Nightstand", (1.8, 1.6, 1.4), (x, y + 0.8, z), DARKWOOD, WOOD,
              roty=roty))
    H(h, part("NightstandDrawer", (1.5, 0.5, 0.1), (x, y + 1.1, z), GOLD, FOIL,
              cancollide=False))
    H(h, part("NightstandLamp", (0.25, 1.2, 0.25), (x, y + 2.2, z), GOLD, FOIL,
              cancollide=False))
    H(h, part("NightstandShade", (0.9, 0.9, 0.9), (x, y + 3, z), WARM, NEON,
              shape=BALL, cancollide=False))


def f_wardrobe(h, x, y, z, roty=0, w=5):
    H(h, part("Wardrobe", (w, 8, 2), (x, y + 4, z), DARKWOOD, WOOD, roty=roty))
    H(h, part("WardrobeDoorL", (w / 2 - 0.15, 7.2, 0.15), (x, y + 4, z), MAHOGANY,
              WOOD, cancollide=False))
    H(h, part("WardrobeDoorR", (w / 2 - 0.15, 7.2, 0.15), (x, y + 4, z), MAHOGANY,
              WOOD, cancollide=False))
    H(h, part("WardrobeHandle", (0.15, 1.2, 0.15), (x, y + 4, z), GOLD, FOIL,
              cancollide=False))


def f_bookshelf(h, x, y, z, roty=0, w=6, hgt=8):
    """Bookshelf frame + shelf rows + colored book rows."""
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))

    def r(dx, dz):
        return (x + dx * ca - dz * sa, z + dx * sa + dz * ca)

    px, pz = r(0, 0)
    H(h, part("Bookshelf", (w, hgt, 1.2), (px, y + hgt / 2, pz), DARKWOOD, WOOD,
              roty=roty))
    rows = max(int(hgt // 1.6), 2)
    for s in range(rows):
        yy = y + 0.9 + s * (hgt - 1) / rows
        H(h, part(f"ShelfBoard{s}", (w - 0.4, 0.15, 0.9), (px, yy, pz),
                  MAHOGANY, WOOD, roty=roty, cancollide=False))
        for b in range(int(w) - 1):
            bx_, bz_ = r(-w / 2 + 0.8 + b, -0.1)
            col = BOOK_COLORS[(s * 7 + b) % len(BOOK_COLORS)]
            bh = 0.8 + ((s + b) % 3) * 0.15
            H(h, part(f"Book{s}_{b}", (0.55, bh, 0.5), (bx_, yy + bh / 2, bz_),
                      col, PLASTIC, roty=roty, cancollide=False))


def f_fireplace(h, x, y, z, roty=0, w=4, chimney=False):
    """Brick fireplace w/ glowing fire, optional chimney column."""
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))

    def r(dx, dz):
        return (x + dx * ca - dz * sa, z + dx * sa + dz * ca)

    px, pz = r(0, 0)
    H(h, part("Fireplace", (w, 5, 1.4), (px, y + 2.5, pz), (110, 60, 50), BRICK,
              roty=roty))
    hx, hz = r(0, -0.4)
    H(h, part("Firebox", (w - 1.6, 2.2, 0.8), (hx, y + 1.4, hz), (30, 20, 18),
              PLASTIC, roty=roty))
    fx, fz = r(0, -0.6)
    H(h, part("Fire", (w - 2, 1.1, 0.5), (fx, y + 0.85, fz), FLAME, NEON,
              roty=roty, cancollide=False))
    H(h, part("Mantel", (w + 0.8, 0.4, 1.8), (px, y + 5.2, pz), DARKWOOD, WOOD,
              roty=roty))
    mx, mz = r(-1, -0.7)
    H(h, part("MantelClock", (0.8, 1, 0.4), (mx, y + 5.9, mz), GOLD, FOIL,
              roty=roty, cancollide=False))
    if chimney:
        H(h, part("Chimney", (w - 1, 8, 1.2), (px, y + 9, pz), (95, 50, 44),
                  BRICK, roty=roty))


def f_kitchen(h, x, y, z, roty=0, run=14, fridge=True):
    """Kitchen counter run: cabinets, granite top, sink, stove, fridge."""
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))

    def r(dx, dz):
        return (x + dx * ca - dz * sa, z + dx * sa + dz * ca)

    for i in range(int(run // 2)):
        dx = -run / 2 + 1 + i * 2
        px, pz = r(dx, 0)
        H(h, part(f"Cabinet{i}", (1.9, 2.4, 1.6), (px, y + 1.2, pz),
                  (60, 60, 66), PLASTIC, roty=roty))
    tx, tz = r(0, -0.1)
    H(h, part("CounterTop", (run, 0.25, 1.8), (tx, y + 2.5, tz), (35, 35, 40),
              GRANITE, roty=roty))
    for i in range(int(run // 2)):
        dx = -run / 2 + 1 + i * 2
        px, pz = r(dx, -0.8)
        H(h, part(f"CabHandle{i}", (1.2, 0.12, 0.12), (px, y + 2.1, pz),
                  SILVER, FOIL, roty=roty, cancollide=False))
    for i in range(int(run // 2)):
        dx = -run / 2 + 1 + i * 2
        px, pz = r(dx, 0.1)
        H(h, part(f"UpperCab{i}", (1.9, 2, 1.2), (px, y + 5.6, pz), (60, 60, 66),
                  PLASTIC, roty=roty, cancollide=False))
    sx, sz = r(-run / 2 + 3, -0.5)
    H(h, part("Sink", (2.4, 0.4, 1.3), (sx, y + 2.45, sz), SILVER, FOIL, roty=roty))
    H(h, part("Faucet", (0.2, 1, 0.2), (sx, y + 3.2, sz), SILVER, FOIL, roty=roty,
              cancollide=False))
    hx, hz = r(1, -0.5)
    H(h, part("Stove", (2.6, 0.35, 1.7), (hx, y + 2.55, hz), (25, 25, 28),
              METAL, roty=roty))
    for bx in (-0.6, 0.6):
        for bz in (-0.35, 0.35):
            bx_, bz_ = r(1 + bx, -0.5 + bz)
            H(h, part("Burner", (0.12, 0.7, 0.7), (bx_, y + 2.8, bz_), (15, 15, 15),
                      PLASTIC, shape=CYL, rotz=90, cancollide=False))
    if fridge:
        fx_, fz_ = r(run / 2 + 1.1, 0)
        H(h, part("Fridge", (2.6, 6, 2.2), (fx_, y + 3, fz_), SILVER, FOIL, roty=roty))
        H(h, part("FridgeHandle", (0.15, 2.4, 0.15), (fx_, y + 3.4, fz_),
                  (60, 60, 66), METAL, roty=roty, cancollide=False))


def f_bathroom(h, x, y, z, roty=0):
    """Bathtub, toilet, sink, mirror — compact corner set."""
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))

    def r(dx, dz):
        return (x + dx * ca - dz * sa, z + dx * sa + dz * ca)

    tx, tz = r(-3.4, 0)
    H(h, part("TubOuter", (4.2, 1.6, 2.4), (tx, y + 0.8, tz), MARBLEC, PLASTIC,
              roty=roty))
    H(h, part("TubWater", (3.6, 0.35, 1.8), (tx, y + 1.1, tz), POOL_WATER,
              GLASS, transparency=0.35, roty=roty, cancollide=False))
    H(h, part("Faucet", (0.2, 0.9, 0.2), (tx + 1.9, y + 1.9, tz), SILVER, FOIL,
              roty=roty, cancollide=False))
    wx, wz = r(1.6, -0.6)
    H(h, part("ToiletBase", (1.6, 1, 2), (wx, y + 0.5, wz), MARBLEC, PLASTIC,
              roty=roty))
    H(h, part("ToiletSeat", (1.4, 0.25, 1.6), (wx, y + 1.1, wz), MARBLEC, PLASTIC,
              roty=roty, cancollide=False))
    H(h, part("ToiletTank", (1.6, 1.4, 0.5), (wx, y + 1.9, wz + 0.7), MARBLEC,
              PLASTIC, roty=roty, cancollide=False))
    vx, vz = r(4.2, -0.4)
    H(h, part("SinkPedestal", (0.8, 2, 0.8), (vx, y + 1, vz), MARBLEC, PLASTIC,
              roty=roty))
    H(h, part("SinkBasin", (2, 0.5, 1.4), (vx, y + 2.2, vz), MARBLEC, PLASTIC,
              roty=roty))
    mx, mz = r(4.2, 0.3)
    H(h, part("Mirror", (2.2, 3, 0.15), (mx, y + 4.2, mz), GLASSC, GLASS,
              transparency=0.25, roty=roty, cancollide=False))
    H(h, part("MirrorFrame", (2.5, 3.3, 0.1), (mx, y + 4.2, mz + 0.05), GOLD,
              FOIL, roty=roty, cancollide=False))


def f_stairs(h, x, y, z, steps=10, rise=1.1, run_=1.1, w=4, dirz=1, color=OFFWHITE):
    """Straight staircase rising `steps` steps toward +Z*dirz."""
    for i in range(steps):
        H(h, part(f"Step{i}", (w, 0.4, run_ + 0.25),
                  (x, y + rise * (i + 0.5), z + dirz * run_ * i), color, PLASTIC))
    H(h, part("StairRail", (0.25, 0.25, steps * run_ + 1),
              (x + w / 2 - 0.2, y + rise * steps * 0.55 + 2.6,
               z + dirz * run_ * (steps - 1) / 2), DARKWOOD, WOOD, rotx=0,
              cancollide=False))


def f_railing(h, x, y, z, length=8, roty=0, color=DARKWOOD):
    """Balcony/loft railing: top rail + balusters."""
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))
    px, pz = x, z
    H(h, part("RailTop", (length, 0.25, 0.25), (px, y + 3.2, pz), color, WOOD,
              roty=roty))
    H(h, part("RailMid", (length, 0.15, 0.15), (px, y + 1.9, pz), color, WOOD,
              roty=roty, cancollide=False))
    for i in range(int(length * 2)):
        lx = -length / 2 + 0.25 + i * 0.5
        bx, bz = x + lx * ca, z + lx * sa
        H(h, part("Baluster", (0.15, 3.2, 0.15), (bx, y + 1.6, bz), color, WOOD,
                  roty=roty, cancollide=False))


def f_door(h, x, y, z, w=4, hgt=7, color=GLASSC, roty=0):
    H(h, part("Door", (w, hgt, 0.7), (x, y + hgt / 2, z), color, SMOOTH,
              transparency=0.25, roty=roty))


def f_window(h, x, y, z, w=4, hgt=4, roty=0, color=GLASSC, t=0.45):
    H(h, part("Window", (w, hgt, 0.3), (x, y, z), color, GLASS,
              transparency=t, roty=roty, cancollide=False))
    bw = 0.3
    H(h, part("WindowFrameTop", (w + 0.6, bw, 0.55), (x, y + hgt / 2 + bw / 2,
              z), WHITE, SMOOTH, roty=roty, cancollide=False))
    H(h, part("WindowFrameBot", (w + 0.6, bw, 0.55), (x, y - hgt / 2 - bw / 2,
              z), WHITE, SMOOTH, roty=roty, cancollide=False))
    H(h, part("WindowFrameL", (bw, hgt, 0.55), (x - w / 2 - bw / 2, y, z),
              WHITE, SMOOTH, roty=roty, cancollide=False))
    H(h, part("WindowFrameR", (bw, hgt, 0.55), (x + w / 2 + bw / 2, y, z),
              WHITE, SMOOTH, roty=roty, cancollide=False))


def f_painting(h, x, y, z, roty=0, w=3, hgt=2.2, color=(60, 90, 140)):
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))
    H(h, part("PaintingFrame", (w + 0.4, hgt + 0.4, 0.2), (x, y, z), GOLD, FOIL,
              roty=roty, cancollide=False))
    H(h, part("Painting", (w, hgt, 0.15), (x - sa * 0.1, y, z - ca * 0.1), color,
              PLASTIC, roty=roty, cancollide=False))


def f_plant(h, x, y, z, big=False):
    s = 1.6 if big else 1.0
    H(h, part("Pot", (1.4 * s, 1.2 * s, 1.2 * s), (x, y + 0.7 * s, z), POTC,
              WOOD, shape=CYL, rotz=90))
    H(h, part("PlantStem", (0.3, 1.2 * s, 0.3), (x, y + 1.9 * s, z), PLANT_DARK,
              GRASS, cancollide=False))
    H(h, part("PlantLeaves", (2 * s, 2.2 * s, 2 * s), (x, y + 2.9 * s, z),
              PLANTC, GRASS, shape=BALL, cancollide=False))


def f_floorlamp(h, x, y, z):
    H(h, part("LampBase", (1, 0.2, 1), (x, y + 0.1, z), GOLD, FOIL))
    H(h, part("LampStand", (0.25, 4, 0.25), (x, y + 2.1, z), GOLD, FOIL,
              cancollide=False))
    H(h, part("LampShade", (1.5, 1.5, 1.5), (x, y + 4.4, z), WARM, NEON,
              shape=BALL, cancollide=False))


def f_curtable_lamp(h, x, y, z):
    H(h, part("DeskLamp", (0.2, 1.2, 0.2), (x, y + 0.6, z), GOLD, FOIL,
              cancollide=False))
    H(h, part("DeskShade", (0.7, 0.7, 0.7), (x, y + 1.4, z), WARM, NEON,
              shape=BALL, cancollide=False))


def f_tree(h, x, z, y=0, s=1.0):
    H(h, part("TreeTrunk", (6 * s, 0.9 * s, 0.9 * s), (x, y + 3 * s, z), TRUNK,
              WOOD, shape=CYL, rotz=90))
    H(h, part("TreeLeaves", (5.5 * s, 4.5 * s, 5.5 * s), (x, y + 7.2 * s, z),
              PLANTC, GRASS, shape=BALL, cancollide=False))
    H(h, part("TreeLeavesTop", (3.8 * s, 3 * s, 3.8 * s), (x, y + 9.6 * s, z),
              PLANT_DARK, GRASS, shape=BALL, cancollide=False))


def f_flowerbed(h, x, z, w=6, d=2, y=0):
    H(h, part("BedSoil", (w, 0.5, d), (x, y + 0.25, z), (90, 62, 44), SAND))
    for i in range(int(w * d / 1.5)):
        fx = x - w / 2 + 0.6 + (i * 1.3) % (w - 1)
        fz = z - d / 2 + 0.5 + ((i * 0.7) % (d - 0.8))
        col = (FLOWER_RED, FLOWER_YELLOW, FLOWER_PINK)[i % 3]
        H(h, part("Flower", (0.5, 0.7, 0.5), (fx, y + 0.85, fz), col, PLASTIC,
                  shape=BALL, cancollide=False))


def f_fence(h, x, z, length, roty=0, y=0, color=OFFWHITE):
    """Fence run: posts + slats along local X axis."""
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))
    n = max(int(length // 3), 1)
    for i in range(n + 1):
        lx = -length / 2 + i * (length / n)
        px, pz = x + lx * ca, z + lx * sa
        H(h, part("FencePost", (0.4, 4, 0.4), (px, y + 2, pz), color, WOOD,
              roty=roty))
    H(h, part("FenceRailA", (length, 0.3, 0.2), (x, y + 1.2, z), color, WOOD,
              roty=roty, cancollide=False))
    H(h, part("FenceRailB", (length, 0.3, 0.2), (x, y + 2.8, z), color, WOOD,
              roty=roty, cancollide=False))


def f_carport_car(h, x, y, z, roty=0, color=CAR_RED):
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))

    def r(dx, dz):
        return (x + dx * ca - dz * sa, z + dx * sa + dz * ca)

    px, pz = r(0, 0)
    H(h, part("CarBody", (4.2, 1.1, 8), (px, y + 1.35, pz), color, SMOOTH,
              roty=roty))
    cx_, cz_ = r(0, -0.4)
    H(h, part("CarCabin", (3.4, 1.1, 3.6), (cx_, y + 2.4, cz_), color, SMOOTH,
              roty=roty))
    gx, gz = r(0, -0.4)
    H(h, part("CarGlass", (3.5, 0.8, 3.7), (gx, y + 2.5, gz), GLASSC, GLASS,
              transparency=0.4, roty=roty, cancollide=False))
    for wx in (-2.1, 2.1):
        for wz in (-2.6, 2.6):
            wx_, wz_ = r(wx, wz)
            H(h, part("CarWheel", (0.5, 1.4, 1.4), (wx_, y + 0.7, wz_), TIRE,
                      PLASTIC, shape=CYL))


def f_fountain(h, x, z, y=0):
    H(h, part("FountainBase", (1, 12, 12), (x, y + 0.5, z), MARBLEC, MARBLE,
              shape=CYL, rotz=90))
    H(h, part("FountainWater", (0.7, 10.5, 10.5), (x, y + 1.1, z), POOL_WATER,
              GLASS, transparency=0.3, shape=CYL, rotz=90, cancollide=False))
    H(h, part("FountainPillar", (3, 1.6, 1.6), (x, y + 2.4, z), MARBLEC, MARBLE,
              shape=CYL, rotz=90))
    H(h, part("FountainTop", (0.5, 3.4, 3.4), (x, y + 4, z), MARBLEC, MARBLE,
              shape=CYL, rotz=90))
    H(h, part("FountainOrb", (1.4, 1.4, 1.4), (x, y + 4.9, z), GOLD, FOIL,
              shape=BALL, cancollide=False))


def f_lantern(h, x, z, y=0):
    H(h, part("LanternPost", (0.35, 5, 0.35), (x, y + 2.5, z), (40, 40, 44),
              METAL))
    H(h, part("LanternGlass", (1, 1.3, 1), (x, y + 5.4, z), WARM, NEON,
              cancollide=False))
    H(h, part("LanternCap", (1.3, 0.3, 1.3), (x, y + 6.2, z), (40, 40, 44),
              METAL, cancollide=False))


# ================================================================ SHARED
cx0 = 0

H("Shared", part("Ground", (420, 1, 420), (0, -0.5, 70), (106, 160, 80), GRASS))
H("Shared", part("Plaza", (60, 0.3, 40), (0, 0.15, 0), MARBLEC, MARBLE))

# cobble main street X-axis at z=25
for i in range(26):
    H("Shared", part(f"Street{i}", (8, 0.2, 7), (-100 + i * 8, 0.1, 25), PATHC,
                     COBBLE))
# connectors north/south
for i in range(20):
    H("Shared", part(f"ConnN{i}", (7, 0.2, 8), (-76 + i * 8, 0.1, 55), PATHC,
                     COBBLE))
for i in range(12):
    H("Shared", part(f"ConnS{i}", (7, 0.2, 8), (-44 + i * 8, 0.1, -8), PATHC,
                     COBBLE))

f_fountain("Shared", 0, 0)

for lx, lz in ((-14, 14), (14, 14), (-14, -14), (14, -14)):
    f_lantern("Shared", lx, lz)

for tx, tz in ((-45, -20), (45, -20), (-80, 60), (80, 60), (-20, 110),
               (20, 110), (-90, 0), (90, 0), (-60, -30), (60, -30),
               (-90, 100), (90, 100), (0, -35)):
    f_tree("Shared", tx, tz, s=1.1)

for bx, bz in ((-30, -22, ), (30, -22), (-70, 40), (70, 40), (-30, 100),
               (30, 100)):
    f_flowerbed("Shared", bx, bz, w=8, d=3)

spawn = (
    f'<Item class="SpawnLocation" referent="{ref()}"><Properties>'
    f'<string name="Name">Spawn</string><bool name="Anchored">true</bool>'
    f'<bool name="Neutral">true</bool><float name="Duration">0</float>'
    f'<token name="Material">{MARBLE}</token>'
    f'<Color3uint8 name="Color3uint8">{pack(*MARBLEC)}</Color3uint8>'
    f'<Vector3 name="size"><X>10</X><Y>0.4</Y><Z>10</Z></Vector3>'
    f'<CoordinateFrame name="CFrame"><X>0</X><Y>0.4</Y><Z>14</Z>'
    f'<R00>1</R00><R01>0</R01><R02>0</R02><R10>0</R10><R11>1</R11><R12>0</R12>'
    f'<R20>0</R20><R21>0</R21><R22>1</R22></CoordinateFrame>'
    f'<token name="TopSurface">0</token><token name="BottomSurface">0</token>'
    f'</Properties></Item>')
H("Shared", spawn)


# ================================================================ HOUSE A
# Modern Cube — 2 floors, mezzanine, glass, white, gold accents
h = "ModernCube"
cx, cz = -52, 55
FY = 0.5

H(h, part("Lot", (34, 0.2, 30), (cx, 0.1, cz), (150, 150, 148), CONCRETE))
H(h, part("Floor", (24, 0.5, 18), (cx, FY - 0.25, cz), MARBLEC, MARBLE))
H(h, part("Floor2", (24, 0.5, 18), (cx, FY + 9.75, cz), MARBLEC, MARBLE))
H(h, part("Roof", (25, 0.5, 19), (cx, FY + 19.2, cz), WHITE, SMOOTH))

H(h, part("WallL", (0.6, 19, 18), (cx - 12, FY + 9.5, cz), WHITE, SMOOTH))
H(h, part("WallR", (0.6, 19, 18), (cx + 12, FY + 9.5, cz), WHITE, SMOOTH))
H(h, part("WallBackF1", (24, 9, 0.6), (cx, FY + 4.5, cz + 9), WHITE, SMOOTH))
for px_ in (-10.5, 10.5):
    H(h, part("WallBackF2Pillar", (3, 9, 0.6), (cx + px_, FY + 14.5, cz + 9),
              WHITE, SMOOTH))
H(h, part("WallBackF2Center", (6, 9, 0.6), (cx, FY + 14.5, cz + 9), WHITE,
          SMOOTH))
for px_ in (-10.75, 10.75):
    H(h, part("WallFrontF2Pillar", (2.5, 9, 0.6), (cx + px_, FY + 14.5,
              cz - 9), WHITE, SMOOTH))
for px_ in (-3, 3):
    H(h, part("WallFrontF2Mullion", (1.5, 9, 0.6), (cx + px_, FY + 14.5,
              cz - 9), WHITE, SMOOTH))
H(h, part("WallFrontF2Header", (24, 1.5, 0.6), (cx, FY + 18.25, cz - 9),
          WHITE, SMOOTH))
H(h, part("GlassFrontF1L", (8, 9, 0.4), (cx - 8, FY + 4.5, cz - 9), GLASSC,
          GLASS, transparency=0.42))
H(h, part("GlassFrontF1R", (8, 9, 0.4), (cx + 8, FY + 4.5, cz - 9), GLASSC,
          GLASS, transparency=0.42))
H(h, part("HeaderF1", (8, 1.4, 0.4), (cx, FY + 8.3, cz - 9), WHITE, SMOOTH))
H(h, part("GlassBackF2L", (6, 9, 0.4), (cx - 6, FY + 14.5, cz + 9), GLASSC,
          GLASS, transparency=0.42))
H(h, part("GlassBackF2R", (6, 9, 0.4), (cx + 6, FY + 14.5, cz + 9), GLASSC,
          GLASS, transparency=0.42))
for wx in (-6, 0, 6):
    f_window(h, cx + wx, FY + 14.5, cz - 9, w=4.5, hgt=6, t=0.42)
f_door(h, cx, FY, cz - 9, w=5, hgt=8)

# gold accent beam
H(h, part("GoldBeamF1", (24, 0.3, 0.3), (cx, FY + 8.8, cz - 8.7), GOLD, FOIL,
          cancollide=False))
H(h, part("GoldBeamF2", (24, 0.3, 0.3), (cx, FY + 18.8, cz + 8.7), GOLD, FOIL,
          cancollide=False))

# F1: living room
f_rug(h, cx - 4, FY, cz - 1, 10, 8, (70, 80, 95), border=(40, 48, 60))
f_sofa(h, cx - 5, FY, cz + 3, SOFA_NAVY)
f_loveseat(h, cx - 10.2, FY, cz - 1, SOFA_NAVY, roty=90)
f_coffee_table(h, cx - 5, FY, cz - 1)
f_tv(h, cx - 5, FY, cz - 8.2, roty=180, w=6)
f_bookshelf(h, cx + 8.8, FY, cz + 4, roty=-90, w=8, hgt=7)
f_floorlamp(h, cx - 10, FY, cz + 6)
f_plant(h, cx + 10, FY, cz - 6, big=True)
f_painting(h, cx - 11.5, FY + 5.5, cz + 4, roty=90, color=(40, 70, 120))
f_painting(h, cx - 11.5, FY + 5.5, cz - 4, roty=90, color=(120, 60, 40))

# F1: dining + kitchen (right half)
f_dining(h, cx + 5, FY, cz + 5, seats=6, w=6)
f_kitchen(h, cx + 4, FY, cz - 7.5, run=10)
f_chandelier(h, cx + 5, FY + 8.4, cz + 5, 0.9, tiers=1, bulbs_per=4)

# F2: mezzanine — stairs along right wall, master suite
f_stairs(h, cx + 10, FY, cz - 5.5, steps=9, rise=1.05, run_=1.05, w=3.4, dirz=1)
f_railing(h, cx + 8.7, FY + 9.7, cz + 4.5, length=6, roty=0)
f_bed(h, cx - 5, FY + 10, cz + 4, roty=0, size=1.1, headcolor=MAHOGANY)
f_nightstand(h, cx - 8.5, FY + 10, cz + 1)
f_nightstand(h, cx - 1.5, FY + 10, cz + 1)
f_wardrobe(h, cx + 2, FY + 10, cz + 7.6, w=8)
f_rug(h, cx - 5, FY + 10, cz + 1, 8, 6, CARPET_CREAM, border=GOLD)
f_armchair(h, cx - 8, FY + 10, cz - 5, roty=45)
f_painting(h, cx, FY + 15, cz - 8.8, color=(90, 40, 90))
f_bathroom(h, cx + 6, FY + 10, cz - 6)
f_chandelier(h, cx - 5, FY + 18.6, cz + 2, 1.1, tiers=2, bulbs_per=6)

# carport
H(h, part("CarportRoof", (12, 0.4, 10), (cx + 20, FY + 8, cz), (70, 70, 74),
          SMOOTH))
for px in (cx + 15, cx + 25):
    for pz in (cz - 4, cz + 4):
        H(h, part("CarportPost", (0.5, 8, 0.5), (px, FY + 4, pz), (70, 70, 74),
                  METAL))
f_carport_car(h, cx + 20, FY, cz, color=CAR_RED)

f_fence(h, cx - 16, cz - 14, 34, y=0.2)
f_fence(h, cx + 16, cz - 14, 34, y=0.2)
f_fence(h, cx, cz + 14.8, 32, y=0.2)
f_tree(h, cx - 14, cz + 10, s=0.9)
f_flowerbed(h, cx + 6, cz - 13, w=10, d=2.5)


# ================================================================ HOUSE B
# A-Frame Chalet — loft, fireplace w/ chimney, wood everywhere
h = "AFrame"
cx, cz = 0, 58
FY = 0.5

H(h, part("Lot", (30, 0.2, 30), (cx, 0.1, cz), (150, 150, 148), CONCRETE))
H(h, part("Floor", (16, 0.5, 20), (cx, FY - 0.25, cz), DARKWOOD, PLANKS))

H(h, part("SlopeL", (0.5, 17, 20), (cx - 4.2, FY + 7, cz), WOODC, PLANKS, rotz=-28))
H(h, part("SlopeR", (0.5, 17, 20), (cx + 4.2, FY + 7, cz), WOODC, PLANKS, rotz=28))
H(h, part("Ridge", (0.6, 0.6, 20), (cx, FY + 14.4, cz), DARKWOOD, WOOD))
for gy_, gw_ in ((8.3, 6), (10.6, 4), (12.7, 2)):
    H(h, part(f"GableGlass{gy_}", (gw_, 1.6, 0.4), (cx, FY + gy_, cz + 9.8),
              GLASSC, GLASS, transparency=0.5))
H(h, part("GableFrameBack", (0.6, 0.6, 19), (cx, FY + 14, cz + 9.8), DARKWOOD,
          WOOD, cancollide=False))
H(h, part("FrontGlassL", (3.5, 4, 0.4), (cx - 3.9, FY + 2.5, cz - 9.8),
          GLASSC, GLASS, transparency=0.5))
H(h, part("FrontGlassR", (3.5, 4, 0.4), (cx + 3.9, FY + 2.5, cz - 9.8),
          GLASSC, GLASS, transparency=0.5))
f_door(h, cx, FY, cz - 9.8, w=4.5, hgt=7, color=DARKWOOD)
f_window(h, cx - 4.5, FY + 1.8, cz + 2, w=2.6, hgt=3.5, roty=90, t=0.5)
f_window(h, cx + 4.5, FY + 1.8, cz - 2, w=2.6, hgt=3.5, roty=90, t=0.5)

# beams
for bz in (-6, 0, 6):
    H(h, part(f"Beam{bz}", (5, 0.5, 0.5), (cx, FY + 10.5, cz + bz), DARKWOOD,
              WOOD, cancollide=False))

f_fireplace(h, cx + 2.5, FY, cz + 7.5, roty=180, w=3.5, chimney=False)
H(h, part("Chimney", (1.5, 4, 1.2), (cx + 1.5, FY + 7.5, cz + 7.5), (95, 50, 44),
          BRICK))
f_rug(h, cx, FY, cz + 1, 9, 7, (120, 70, 40), border=(90, 52, 30))
f_sofa(h, cx - 3, FY, cz + 1.5, (110, 75, 55), roty=0)
f_armchair(h, cx + 2, FY, cz - 1, (110, 75, 55), roty=-135)
f_coffee_table(h, cx, FY, cz - 1, w=3.5, mat=WOOD, color=WOODC, leg=BRONZE)
f_tv(h, cx, FY, cz - 9, roty=180, w=4)
f_bookshelf(h, cx + 5.5, FY, cz + 3, roty=-90, w=5, hgt=6)
f_floorlamp(h, cx - 6.5, FY, cz - 5)
f_plant(h, cx + 6.5, FY, cz - 4)
f_dining(h, cx, FY, cz - 6, seats=4, w=4.5)
f_chandelier(h, cx, FY + 13.6, cz, 0.8, tiers=1, bulbs_per=5)
for bz in (-6, 0, 6):
    H(h, part(f"Antler{bz}", (2, 0.8, 0.4), (cx, FY + 12.6, cz + bz), BRONZE,
              WOOD, cancollide=False))

# ground-floor bedroom nook (vaulted ceiling)
f_bed(h, cx - 4, FY, cz + 5.8, roty=180, size=0.95, headcolor=MAHOGANY)
f_nightstand(h, cx + 0.5, FY, cz + 7)
f_rug(h, cx - 4, FY, cz + 4, 6, 5, (140, 90, 55))
f_painting(h, cx - 7.6, FY + 5, cz + 4, roty=90, color=(70, 110, 70))

f_fence(h, cx - 14, cz - 14, 28, y=0.2)
f_fence(h, cx + 14, cz - 14, 28, y=0.2)
f_fence(h, cx, cz + 14.8, 28, y=0.2)
f_tree(h, cx - 11, cz + 9, s=1.0)
f_tree(h, cx + 11, cz + 10, s=0.8)
f_flowerbed(h, cx - 5, cz - 13, w=8, d=2.5)
f_flowerbed(h, cx + 5, cz - 13, w=8, d=2.5)


# ================================================================ HOUSE C
# Castle — stone keep, 3-floor tower w/ spiral stairs, throne hall
h = "Castle"
cx, cz = 52, 58
FY = 0.5

H(h, part("Lot", (52, 0.2, 36), (cx, 0.1, cz), (150, 150, 148), CONCRETE))
H(h, part("Floor", (26, 0.5, 22), (cx, FY - 0.25, cz), (200, 200, 205), SLATE))
H(h, part("CarpetHall", (10, 0.1, 20), (cx, FY + 0.05, cz - 4), CARPET_RED,
          FABRIC, cancollide=False))

H(h, part("WallL", (1, 12, 22), (cx - 13, FY + 6, cz), STONE, COBBLE))
H(h, part("WallR", (1, 12, 22), (cx + 13, FY + 6, cz), STONE, COBBLE))
H(h, part("WallBackBelow", (26, 5.5, 1), (cx, FY + 3.25, cz + 11), STONE,
          COBBLE))
H(h, part("WallBackAbove", (26, 2, 1), (cx, FY + 11, cz + 11), STONE, COBBLE))
for sx_ in (-1, 1):
    H(h, part(f"WallBack{'L' if sx_ < 0 else 'R'}Out", (2.75, 4, 1),
              (cx + sx_ * 11.625, FY + 8, cz + 11), STONE, COBBLE))
H(h, part("WallBackMid", (15.5, 4, 1), (cx, FY + 8, cz + 11), STONE, COBBLE))
for sx_ in (-1, 1):
    nm_ = 'L' if sx_ < 0 else 'R'
    H(h, part(f"WallFront{nm_}Out", (2.75, 12, 1), (cx + sx_ * 11.625, FY + 6,
              cz - 11), STONE, COBBLE))
    H(h, part(f"WallFront{nm_}In", (3.75, 12, 1), (cx + sx_ * 5.875, FY + 6,
              cz - 11), STONE, COBBLE))
    H(h, part(f"WallFront{nm_}Below", (2.5, 5.5, 1), (cx + sx_ * 9, FY + 3.25,
              cz - 11), STONE, COBBLE))
    H(h, part(f"WallFront{nm_}Above", (2.5, 2, 1), (cx + sx_ * 9, FY + 11,
              cz - 11), STONE, COBBLE))
H(h, part("HeaderFront", (8, 4, 1), (cx, FY + 10, cz - 11), STONE, COBBLE))
for i in range(7):
    H(h, part(f"CrenFront{i}", (2, 1.6, 1), (cx - 12 + i * 4, FY + 12.8,
              cz - 11), STONE, COBBLE))
for i in range(7):
    H(h, part(f"CrenBack{i}", (2, 1.6, 1), (cx - 12 + i * 4, FY + 12.8,
              cz + 11), STONE, COBBLE))
for i in range(4):
    H(h, part(f"CrenL{i}", (1, 1.6, 2), (cx - 13, FY + 12.8, cz - 9 + i * 6),
              STONE, COBBLE))
    H(h, part(f"CrenR{i}", (1, 1.6, 2), (cx + 13, FY + 12.8, cz - 9 + i * 6),
              STONE, COBBLE))
f_door(h, cx, FY, cz - 11, w=6, hgt=7.5, color=DARKWOOD)
for wx in (-9, 9):
    H(h, part(f"WinGlassF{wx}", (2.5, 4, 0.4), (cx + wx, FY + 8, cz - 11),
              GLASSC, GLASS, transparency=0.5, cancollide=False))
    H(h, part(f"WinGlassB{wx}", (2.5, 4, 0.4), (cx + wx, FY + 8, cz + 11),
              GLASSC, GLASS, transparency=0.5, cancollide=False))

# banners
for bx in (-4, 4):
    H(h, part(f"Banner{bx}", (2.4, 6, 0.15), (cx + bx, FY + 7, cz - 10.4),
              (120, 30, 40), FABRIC, cancollide=False))
    H(h, part(f"BannerGold{bx}", (1.2, 1.2, 0.1), (cx + bx, FY + 8, cz - 10.3),
              GOLD, FOIL, cancollide=False))

# throne dais + gold throne
H(h, part("Dais", (8, 0.8, 6), (cx, FY + 0.4, cz + 6.5), MARBLEC, MARBLE))
H(h, part("Dais2", (5, 0.8, 4), (cx, FY + 1.2, cz + 7), MARBLEC, MARBLE))
H(h, part("ThroneSeat", (2.6, 1, 2.4), (cx, FY + 2.6, cz + 7), GOLD, FOIL))
H(h, part("ThroneBack", (2.6, 4.5, 0.5), (cx, FY + 4.8, cz + 8), GOLD, FOIL))
H(h, part("ThroneCrown", (1, 0.8, 0.4), (cx, FY + 7.3, cz + 8), GOLD, FOIL,
          cancollide=False))
H(h, part("ThroneArmL", (0.5, 1.6, 2.4), (cx - 1.55, FY + 3.4, cz + 7), GOLD,
          FOIL))
H(h, part("ThroneArmR", (0.5, 1.6, 2.4), (cx + 1.55, FY + 3.4, cz + 7), GOLD,
          FOIL))
f_chandelier(h, cx, FY + 11.4, cz - 3, 1.6, tiers=3, bulbs_per=8)
f_chandelier(h, cx, FY + 11.4, cz + 4, 1.2, tiers=2, bulbs_per=6)
for px, pz, roty in ((-11, -8, 90), (11, -8, -90)):
    H(h, part("TorchPole", (0.3, 4, 0.3), (cx + px, FY + 2, cz + pz), (40, 40, 44),
              METAL, roty=roty, cancollide=False))
    H(h, part("TorchFlame", (0.9, 1.1, 0.9), (cx + px, FY + 4.4, cz + pz), FLAME,
              NEON, cancollide=False))
f_plant(h, cx - 11, FY, cz + 2, big=True)
f_plant(h, cx + 11, FY, cz + 2, big=True)
f_bookshelf(h, cx - 12.2, FY, cz + 7, roty=90, w=7, hgt=9)
f_painting(h, cx - 13.4, FY + 8, cz, roty=90, w=4, hgt=3, color=(70, 50, 110))
f_painting(h, cx + 13.4, FY + 8, cz, roty=-90, w=4, hgt=3, color=(110, 70, 40))

# tower: cylinder 3 floors + spiral stairs + cone top
tx, tz = cx + 19, cz + 6
H(h, part("TowerShaft", (24, 11, 11), (tx, FY + 12, tz), STONE, COBBLE,
          shape=CYL, rotz=90))
H(h, part("TowerFloor1", (0.5, 10.4, 10.4), (tx, FY + 6, tz), (200, 200, 205),
          SLATE, shape=CYL, rotz=90))
H(h, part("TowerFloor2", (0.5, 10.4, 10.4), (tx, FY + 12, tz), (200, 200, 205),
          SLATE, shape=CYL, rotz=90))
H(h, part("TowerCone", (13, 9, 13), (tx, FY + 28.5, tz), (70, 90, 140), SLATE,
          shape=BALL))
H(h, part("TowerFlagPole", (0.25, 5, 0.25), (tx, FY + 36, tz), (40, 40, 44),
          METAL, cancollide=False))
H(h, part("TowerFlag", (3, 1.6, 0.12), (tx + 1.6, FY + 37.6, tz), (150, 30, 40),
          FABRIC, cancollide=False))
for fl in range(3):
    a0 = fl * 120
    for s in range(10):
        a = math.radians(a0 + s * 36)
        sx_ = tx + 3.4 * math.cos(a)
        sz_ = tz + 3.4 * math.sin(a)
        H(h, part(f"Spiral{fl}_{s}", (2.6, 0.4, 1.6),
                  (sx_, FY + fl * 6 + 0.7 + s * 0.53, sz_), (200, 200, 205),
                  SLATE, roty=math.degrees(a) + 90))
H(h, part("TowerDoor", (3, 6, 0.3), (tx, FY + 3, tz - 5.2), DARKWOOD, WOOD))
f_chandelier(h, tx, FY + 5.6, tz, 0.9, tiers=1, bulbs_per=5)
f_chandelier(h, tx, FY + 11.6, tz, 0.9, tiers=1, bulbs_per=5)
f_bed(h, tx, FY + 12.5, tz, round_=True, size=0.9, color=(180, 170, 160))
f_painting(h, tx, FY + 15.5, tz - 4.8, color=(60, 60, 120))

f_fence(h, cx - 19, cz - 17, 38, y=0.2, color=DARKSTONE)
f_fence(h, cx + 19, cz - 17, 38, y=0.2, color=DARKSTONE)
f_fence(h, cx - 3, cz + 17.8, 32, y=0.2, color=DARKSTONE)
f_fence(h, cx + 17, cz + 17.8, 12, y=0.2, color=DARKSTONE)
f_tree(h, cx - 15, cz - 12, s=1.0)
f_tree(h, cx + 2, cz - 14, s=0.9)


# ================================================================ HOUSE D
# Villa L — 2 floors, pool, glass walls, carport, outdoor dining
h = "VillaL"
cx, cz = -34, 110
FY = 0.5

H(h, part("Lot", (44, 0.2, 40), (cx, 0.1, cz), (150, 150, 148), CONCRETE))
H(h, part("FloorA", (20, 0.5, 14), (cx, FY - 0.25, cz), MARBLEC, MARBLE))
H(h, part("FloorB", (10, 0.5, 14), (cx + 14.5, FY - 0.25, cz + 7), MARBLEC,
          MARBLE))
H(h, part("FloorA2", (20, 0.5, 14), (cx, FY + 9.75, cz), MARBLEC, MARBLE))
H(h, part("FloorB2", (10, 0.5, 14), (cx + 14.5, FY + 9.75, cz + 7), MARBLEC,
          MARBLE))
H(h, part("RoofA", (21, 0.5, 15), (cx, FY + 19.2, cz), WHITE, SMOOTH))
H(h, part("RoofB", (11, 0.5, 15), (cx + 14.5, FY + 19.45, cz + 7), WHITE, SMOOTH))

# ground floor walls: glass front, white back
H(h, part("WallABack", (20, 9, 0.6), (cx, FY + 4.5, cz + 7), WHITE, SMOOTH))
H(h, part("WallAL", (0.6, 9, 14), (cx - 10, FY + 4.5, cz), WHITE, SMOOTH))
H(h, part("GlassAFrontL", (4.5, 9, 0.4), (cx - 7.75, FY + 4.5, cz - 7),
          GLASSC, GLASS, transparency=0.42))
H(h, part("GlassAFrontR", (10.5, 9, 0.4), (cx + 4.75, FY + 4.5, cz - 7),
          GLASSC, GLASS, transparency=0.42))
H(h, part("WallBBack", (0.6, 9, 14), (cx + 19.5, FY + 4.5, cz + 7), WHITE,
          SMOOTH))
H(h, part("WallBOuter", (10, 9, 0.6), (cx + 14.5, FY + 4.5, cz + 14), WHITE,
          SMOOTH))
H(h, part("WallBInnerL", (3, 9, 0.6), (cx + 11, FY + 4.5, cz), WHITE, SMOOTH))
H(h, part("WallBInnerR", (3, 9, 0.6), (cx + 18, FY + 4.5, cz), WHITE, SMOOTH))
# second floor: glass band
H(h, part("GlassA2Front", (20, 9, 0.4), (cx, FY + 14.5, cz - 7), GLASSC, GLASS,
          transparency=0.42))
H(h, part("GlassA2Back", (20, 9, 0.4), (cx, FY + 14.5, cz + 7), GLASSC, GLASS,
          transparency=0.42))
H(h, part("WallA2L", (0.6, 9, 14), (cx - 10, FY + 14.5, cz), WHITE, SMOOTH))
H(h, part("GlassB2Front", (10, 9, 0.4), (cx + 14.5, FY + 14.5, cz), GLASSC,
          GLASS, transparency=0.42))
H(h, part("GlassB2Back", (10, 9, 0.4), (cx + 14.5, FY + 14.5, cz + 14), GLASSC,
          GLASS, transparency=0.42))
H(h, part("WallB2Outer", (0.6, 9, 14), (cx + 19.5, FY + 14.5, cz + 7), WHITE,
          SMOOTH))
f_door(h, cx - 3, FY, cz - 7, w=5, hgt=8)
f_door(h, cx + 14.5, FY, cz, w=4, hgt=7, roty=0)
H(h, part("GoldBeamA", (20, 0.3, 0.3), (cx, FY + 8.7, cz - 6.7), GOLD, FOIL,
          cancollide=False))
H(h, part("GoldBeamA2", (20, 0.3, 0.3), (cx, FY + 18.7, cz - 6.7), GOLD, FOIL,
          cancollide=False))

# F1: open living + kitchen
f_rug(h, cx - 4, FY, cz + 1, 10, 8, (185, 160, 110), border=(150, 128, 85))
f_sofa(h, cx - 5, FY, cz + 3.5, (100, 105, 118), w=7)
f_coffee_table(h, cx - 5, FY, cz, w=4)
f_tv(h, cx - 5, FY, cz - 6, roty=180, w=5)
f_kitchen(h, cx + 5, FY, cz - 6, run=10)
f_dining(h, cx + 5, FY, cz + 2, seats=6, w=6)
f_chandelier(h, cx + 5, FY + 8.4, cz + 2, 1.0, tiers=2, bulbs_per=5)
f_plant(h, cx - 9, FY, cz + 5, big=True)
f_painting(h, cx - 9.6, FY + 5, cz - 2, roty=90, color=(200, 140, 60))

# pool deck (front-left)
H(h, part("PoolDeck", (16, 0.3, 10), (cx - 6, FY + 0.15, cz - 13), MARBLEC,
          MARBLE))
H(h, part("PoolBasin", (11, 1.2, 6.5), (cx - 6, FY + 0.5, cz - 13), (200, 205,
          210), PLASTIC))
H(h, part("PoolWater", (10.4, 1.05, 5.9), (cx - 6, FY + 0.6, cz - 13),
          POOL_WATER, GLASS, transparency=0.32))
for lx in (cx - 11, cx - 1):
    f_lantern(h, lx, cz - 17, y=FY + 0.3)
f_floorlamp(h, cx - 11, FY + 0.3, cz - 9.5)
for i, lcx in enumerate((cx - 13.2, cx + 1.2)):
    H(h, part("LoungeChair", (2, 0.4, 5), (lcx, FY + 0.5,
              cz - 11), OFFWHITE, FABRIC, roty=90 + i * 180))
    H(h, part("LoungeBack", (2, 2.2, 0.4), (lcx, FY + 1.5,
              cz - 13), OFFWHITE, FABRIC, cancollide=False))

# F2: stairs + bedrooms
f_stairs(h, cx + 8, FY, cz + 4.5, steps=9, rise=1.05, run_=1.05, w=3.5, dirz=1)
f_railing(h, cx + 8, FY + 9.7, cz + 12.4, length=8, roty=0)
f_bed(h, cx - 5, FY + 10, cz + 3, size=1.05, headcolor=MAHOGANY)
f_nightstand(h, cx - 8.5, FY + 10, cz)
f_rug(h, cx - 5, FY + 10, cz, 8, 6, CARPET_CREAM, border=(170, 150, 120))
f_bathroom(h, cx + 5, FY + 10, cz + 2.5)
f_wardrobe(h, cx + 1.5, FY + 10, cz + 5.8, w=5)
f_bed(h, cx + 15, FY + 10, cz + 10, roty=180, size=0.9, headcolor=MAHOGANY)
f_rug(h, cx + 15, FY + 10, cz + 7, 6, 5, CARPET_PURPLE)
f_painting(h, cx + 9.7, FY + 15, cz + 7, roty=-90, color=(40, 90, 130))

# carport + car
H(h, part("CarportRoof", (12, 0.4, 10), (cx - 16, FY + 8, cz + 2), (70, 70, 74),
          SMOOTH))
for px in (cx - 21, cx - 11):
    for pz in (cz - 2, cz + 6):
        H(h, part("CarportPost", (0.5, 8, 0.5), (px, FY + 4, pz), (70, 70, 74),
                  METAL))
f_carport_car(h, cx - 16, FY, cz + 2, color=(40, 60, 110))

f_fence(h, cx - 21, cz - 19, 42, y=0.2)
f_fence(h, cx + 21, cz - 19, 42, y=0.2)
f_fence(h, cx, cz + 19.8, 42, y=0.2)
f_tree(h, cx + 17, cz - 15, s=1.0)
f_tree(h, cx - 17, cz + 15, s=0.85)
f_flowerbed(h, cx + 10, cz - 18, w=12, d=2.5)


# ================================================================ HOUSE E
# Glass Dome — octagon glass, round bed, zen garden ring
h = "Dome"
cx, cz = 30, 110
FY = 0.5

H(h, part("Lot", (34, 0.2, 34), (cx, 0.1, cz), (150, 150, 148), CONCRETE))
H(h, part("Floor", (0.5, 17, 17), (cx, FY - 0.25, cz), MARBLEC, MARBLE,
          shape=CYL, rotz=90))
for k in range(8):
    if k == 4:
        continue
    a = math.radians(k * 45)
    px, pz = cx + 8.2 * math.sin(a), cz + 8.2 * math.cos(a)
    H(h, part(f"WallPanel{k}", (6.9, 7, 0.4), (px, FY + 3.5, pz), GLASSC, GLASS,
              transparency=0.4, roty=math.degrees(a)))
H(h, part("Ring", (0.5, 17.0, 17.0), (cx, FY + 7.45, cz), WHITE, SMOOTH,
          shape=CYL, rotz=90))
H(h, part("DomeRoof", (16.4, 16.4, 16.4), (cx, FY + 7.5, cz), GLASSC, GLASS,
          transparency=0.35, shape=BALL))
H(h, part("ApexRing", (0.3, 2.8, 2.8), (cx, FY + 15.6, cz), WARM, NEON,
          shape=CYL, rotz=90, cancollide=False))
f_door(h, cx, FY, cz - 8.2, w=5, hgt=5.5, color=GLASSC)
f_chandelier(h, cx, FY + 12.6, cz, 1.0, tiers=1, bulbs_per=6)
f_rug(h, cx, FY, cz, 12, 12, (90, 60, 110), border=(60, 40, 80))
f_bed(h, cx, FY, cz + 2.5, round_=True, size=1.15)
f_nightstand(h, cx - 3.5, FY, cz + 0.5)
f_nightstand(h, cx + 3.5, FY, cz + 0.5)
f_armchair(h, cx - 3.2, FY, cz - 2.4, SOFA_BEIGE, roty=60)
f_loveseat(h, cx + 3.2, FY, cz - 2.4, SOFA_BEIGE, roty=-60)
f_coffee_table(h, cx, FY, cz - 3.5, w=3, mat=WOOD, color=DARKWOOD)
f_plant(h, cx - 4.8, FY, cz + 1, big=True)
f_plant(h, cx + 4.8, FY, cz + 1, big=True)
f_bookshelf(h, cx + 5.8, FY, cz + 4.5, roty=-90, w=5, hgt=5)
f_floorlamp(h, cx + 5, FY, cz - 5.5)
f_painting(h, cx - 8.1, FY + 4.5, cz + 2, roty=63, color=(80, 120, 160))

# zen ring: rocks + mini trees around dome
for i in range(10):
    a = math.radians(i * 36 + 18)
    rx, rz = cx + 12.5 * math.cos(a), cz + 12.5 * math.sin(a)
    H(h, part("ZenRock", (1 + (i % 3) * 0.4, 0.8 + (i % 2) * 0.4,
              1 + (i % 3) * 0.4), (rx, FY + 0.5, rz), ROCKC, SLATE,
              roty=i * 36))
f_tree(h, cx - 13, cz - 12, s=0.7)
f_tree(h, cx + 13, cz + 12, s=0.7)
f_lantern(h, cx - 10, cz, y=FY)
f_lantern(h, cx + 10, cz, y=FY)
f_fence(h, cx - 16, cz - 16, 32, y=0.2)
f_fence(h, cx + 16, cz - 16, 32, y=0.2)
f_fence(h, cx - 8, cz + 16.8, 16, y=0.2)
f_fence(h, cx + 8, cz + 16.8, 16, y=0.2)
f_flowerbed(h, cx, cz - 15, w=10, d=2.5)


# ================================================================ HOUSE F
# Zen Pavilion — stilts, sliding panels, tatami, rock garden, koi pond
h = "ZenHouse"
cx, cz = -30, -28
FY = 2.5

H(h, part("Lot", (36, 0.2, 36), (cx, 0.1, cz), (150, 150, 148), CONCRETE))
# stilts
for sx in (-8, -2.5, 2.5, 8):
    for sz in (-6, 0, 6):
        H(h, part("Stilt", (0.8, FY, 0.8), (cx + sx, FY / 2, cz + sz), DARKWOOD,
                  WOOD))
H(h, part("Platform", (22, 0.5, 17), (cx, FY - 0.25, cz), (190, 170, 130),
          PLANKS))
H(h, part("TatamiMain", (12, 0.15, 15), (cx - 4, FY + 0.08, cz), (215, 200,
          150), FABRIC, cancollide=False))
H(h, part("TatamiSide", (8, 0.15, 15), (cx + 7, FY + 0.08, cz), (215, 200, 150),
          FABRIC, cancollide=False))
H(h, part("Roof", (25, 0.6, 20), (cx, FY + 10.5, cz), (60, 70, 75), SLATE))
H(h, part("RoofRim", (25, 0.8, 20), (cx, FY + 9.9, cz), DARKWOOD, WOOD,
          cancollide=False))
H(h, part("BeamF", (22, 0.5, 0.5), (cx, FY + 7.5, cz - 8.5), DARKWOOD, WOOD))
H(h, part("BeamB", (22, 0.5, 0.5), (cx, FY + 7.5, cz + 8.5), DARKWOOD, WOOD))
H(h, part("WallBack", (22, 7, 0.5), (cx, FY + 3.75, cz + 8.5), (225, 218, 200),
          PLASTIC))
for k in range(3):
    px = cx - 8 + k * 4
    H(h, part(f"Panel{k}", (3.6, 7, 0.25), (px, FY + 3.75, cz - 8.5), (150, 90,
              70), WOOD, cancollide=False))
f_door(h, cx + 4, FY, cz - 8.5, w=4, hgt=7, color=(150, 90, 70))
H(h, part("WallL", (0.5, 7, 17), (cx - 11, FY + 3.75, cz), (225, 218, 200),
          PLASTIC))
H(h, part("WallR", (0.5, 7, 17), (cx + 11, FY + 3.75, cz), (225, 218, 200),
          PLASTIC))
# stairs + walkway
f_stairs(h, cx + 12.5, 0.2, cz + 2, steps=6, rise=0.42, run_=0.95, w=4, dirz=-1,
         color=DARKWOOD)
H(h, part("Walkway", (4, 0.4, 10), (cx + 14.5, FY - 0.45, cz - 8), DARKWOOD,
          PLANKS))

# interior: low table, cushions, bonsai, bed niche
H(h, part("LowTable", (6, 0.4, 3), (cx - 4, FY + 1.2, cz - 1), DARKWOOD, WOOD))
for dx in (-1.8, 1.8):
    H(h, part("TableLeg", (0.4, 1, 0.4), (cx - 4 + dx, FY + 0.6, cz - 1),
              DARKWOOD, WOOD))
for dx, dz in ((-2.2, -2.6), (2.2, -2.6), (-2.2, 1.4), (2.2, 1.4)):
    H(h, part("Cushion", (1.8, 0.4, 1.8), (cx - 4 + dx, FY + 0.5, cz - 1 + dz),
              (170, 60, 60), FABRIC))
f_bed(h, cx + 6.5, FY, cz + 4.5, roty=0, size=0.9, headcolor=DARKWOOD)
f_rug(h, cx + 6.5, FY, cz + 2, 6, 5, (170, 60, 60), border=(120, 40, 40))
f_bookshelf(h, cx + 10.6, FY, cz - 4, roty=-90, w=5, hgt=6)
f_plant(h, cx - 9, FY, cz + 5, big=True)
H(h, part("BonsaiPot", (1.6, 0.9, 1.6), (cx - 4, FY + 1.65, cz - 1), (110, 70,
          50), WOOD))
H(h, part("BonsaiTrunk", (0.3, 1.2, 0.3), (cx - 4, FY + 2.6, cz - 1), TRUNK,
          WOOD, cancollide=False))
H(h, part("BonsaiCrown", (2, 1.1, 2), (cx - 4, FY + 3.5, cz - 1), PLANT_DARK,
          GRASS, shape=BALL, cancollide=False))
f_painting(h, cx, FY + 4.5, cz + 8.2, w=4, hgt=2.6, color=(90, 110, 80))
f_lantern(h, cx - 13, cz - 11)
f_lantern(h, cx + 13, cz - 11)

# koi pond + rock garden + bridge
H(h, part("PondBasin", (12, 0.8, 8), (cx - 2, 0.4, cz + 16), (110, 100, 90),
          SLATE))
H(h, part("PondWater", (11, 0.55, 7), (cx - 2, 0.5, cz + 16), POOL_WATER, GLASS,
          transparency=0.3))
for i in range(5):
    H(h, part("Koi", (0.8, 0.3, 1.6), (cx - 5 + (i * 2.2) % 9, 0.75,
              cz + 14 + (i * 1.7) % 5), (240, 120, 40) if i % 2 else (250, 250,
              250), PLASTIC, roty=i * 53, cancollide=False))
H(h, part("PondRock1", (1.6, 1.2, 1.6), (cx + 4, 0.7, cz + 15), ROCKC, SLATE,
          roty=30))
H(h, part("PondRock2", (1.2, 0.9, 1.2), (cx - 7, 0.6, cz + 17), ROCKC, SLATE,
          roty=70))
H(h, part("Bridge", (3, 0.3, 8), (cx + 5, 0.9, cz + 14), DARKWOOD, WOOD, rotx=-12))
for bx in (cx + 3.7, cx + 6.3):
    H(h, part("BridgeRail", (0.2, 0.2, 7.4), (bx, 2, cz + 14), DARKWOOD, WOOD,
              rotx=-12, cancollide=False))
for i in range(7):
    a = math.radians(i * 51)
    H(h, part("GardenRock", (1 + (i % 3) * 0.5, 0.7 + (i % 2) * 0.5,
              1 + (i % 3) * 0.5), (cx - 10 + 5.5 * math.cos(a), 0.45,
              cz + 16.5 + 2.2 * math.sin(a)), ROCKC, SLATE, roty=i * 51))
f_tree(h, cx + 12, cz + 16, s=0.75)
f_tree(h, cx - 14, cz + 13, s=0.8)


# ================================================================ assemble
order = ["Shared", "ModernCube", "AFrame", "Castle", "VillaL", "Dome",
         "ZenHouse"]
inner = ""
for name in order:
    inner += (f'<Item class="Folder" referent="{ref()}"><Properties>'
              f'<string name="Name">{name}</string></Properties>'
              + "".join(houses.get(name, [])) + "</Item>")

with open(os.path.join(os.path.dirname(__file__), "HouseLogic.lua"),
          encoding="utf-8") as f:
    lua = f.read()
assert "]]>" not in lua

script_xml = (f'<Item class="Script" referent="{ref()}"><Properties>'
              f'<string name="Name">HouseLogic</string>'
              f'<bool name="Disabled">false</bool>'
              f'<ProtectedString name="Source"><![CDATA[{lua}]]></ProtectedString>'
              f'</Properties></Item>')

lighting = (
    f'<Item class="Lighting" referent="{ref()}"><Properties>'
    f'<Color3uint8 name="Ambient">{pack(120, 118, 122)}</Color3uint8>'
    f'<Color3uint8 name="OutdoorAmbient">{pack(160, 150, 140)}</Color3uint8>'
    f'<float name="Brightness">2.8</float><float name="ClockTime">14.5</float>'
    f'<Color3uint8 name="FogColor">{pack(200, 210, 225)}</Color3uint8>'
    f'<float name="FogStart">300</float><float name="FogEnd">1200</float>'
    f'<bool name="GlobalShadows">true</bool>'
    f'</Properties></Item>')

doc = ('<roblox version="4">'
       f'<Item class="Workspace" referent="{ref()}"><Properties>'
       f'<string name="Name">Workspace</string></Properties>{inner}</Item>'
       f'<Item class="ServerScriptService" referent="{ref()}"><Properties>'
       f'<string name="Name">ServerScriptService</string></Properties>{script_xml}</Item>'
       + lighting + "</roblox>")

out = os.path.join(os.path.dirname(__file__), "houses.rbxlx")
with open(out, "w", encoding="utf-8") as f:
    f.write(doc)

import xml.etree.ElementTree as ET
ET.parse(out)
n_items = doc.count("<Item class=")
n_doors = doc.count(">Door<")
n_houses = sum(1 for name in order[1:] if houses.get(name))
assert n_doors >= 6, n_doors
assert n_houses == 6, n_houses
lines_gen = sum(1 for _ in open(__file__, encoding="utf-8"))
print(f"OK {out}: {os.path.getsize(out)} bytes, {n_items} items, "
      f"{n_doors} doors, {n_houses} houses, generator {lines_gen} lines")
