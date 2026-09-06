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
SCALE = 1.75  # world scale up: rooms sized for the character
WORLD_LIFT = 24  # pre-scale studs: whole world sits on a platform at y=42
LIFT_OFF = False  # underground structures opt out of the lift


def part(name, size, pos, color, mat=PLASTIC, transparency=0.0,
         cancollide=True, shape=None, rotx=0.0, roty=0.0, rotz=0.0,
         cls="Part"):
    """One anchored part. Single-axis rotation only (rotx/roty/rotz degrees)."""
    lift = 0 if LIFT_OFF else WORLD_LIFT
    x, y, z = ((v + (lift if k == 1 else 0)) * SCALE
               for k, v in enumerate(pos))
    sx, sy, sz = (v * SCALE for v in size)
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


def f_dining(h, x, y, z, seats=6, w=7, mat=WOOD, color=DARKWOOD, roty=0):
    """Dining table + `seats` chairs around it."""
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))

    def r(dx, dz):
        return (x + dx * ca - dz * sa, z + dx * sa + dz * ca)

    H(h, part("DiningTable", (w, 0.35, 3.4), (x, y + 1.55, z), color, mat,
              roty=roty))
    H(h, part("DiningRunner", (w - 1.5, 0.12, 1.1), (x, y + 1.8, z),
              CARPET_CREAM, FABRIC, roty=roty, cancollide=False))
    for dx in (-w / 2 + 0.5, 0, w / 2 - 0.5):
        lx, lz = r(dx, 0)
        H(h, part("TableLeg", (0.35, 1.4, 0.35), (lx, y + 0.7, lz), color,
                  mat, roty=roty))
    for i in range(seats):
        side = -1 if i % 2 == 0 else 1
        idx = i // 2
        cx_, cz_ = r(- (w / 2 - 1) + idx * (w - 2) / max(seats // 2 - 1, 1),
                     side * 2.4)
        srot = roty if side == 1 else roty + 180
        H(h, part("ChairSeat", (1.3, 0.25, 1.3), (cx_, y + 1.0, cz_), color,
                  WOOD, roty=roty))
        H(h, part("ChairBack", (1.3, 1.6, 0.25), (cx_, y + 1.8, cz_ + side * 0.55),
                  color, WOOD, roty=roty))
        for lx in (-0.5, 0.5):
            for lz in (-0.5, 0.5):
                ox, oz = r(lx + (cx_ - x), lz + (cz_ - z))
                H(h, part("ChairLeg", (0.15, 0.9, 0.15), (ox, y + 0.45, oz),
                          color, WOOD, roty=roty))
        H(h, part("ChairCushion", (1.1, 0.12, 1.1), (cx_, y + 1.19, cz_),
                  CARPET_CREAM, FABRIC, roty=roty, cancollide=False))


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
    """Bathtub, toilet, sink, mirror + partition walls (back + both sides)
    with a frosted doorway — the set forms an enclosed ~11x5.5 room."""
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))

    def r(dx, dz):
        return (x + dx * ca - dz * sa, z + dx * sa + dz * ca)

    def wall(dx, dz, sx, sz):
        wx, wz = r(dx, dz)
        H(h, part("BathWall", (sx, 7, sz), (wx, y + 3.5, wz), MARBLEC,
                  PLASTIC, roty=roty))
    wall(0, 2.75, 11.5, 0.5)          # back
    wall(-5.5, 0, 0.5, 5.5)           # left
    wall(5.5, -0.5, 0.5, 4.5)         # right, doorway gap at its front end
    gdx, gdz = r(5.5, -2.2)
    H(h, part("BathDoorway", (0.35, 6, 2), (gdx, y + 3, gdz), (200, 225, 240),
              SMOOTH, transparency=0.55, roty=roty, cancollide=False))

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
    # shower over the tub (interactive via HouseLogic)
    sx2, sz2 = r(1.9, 0)
    H(h, part("Shower", (0.5, 0.5, 0.5), (sx2, y + 4.9, sz2), SILVER, METAL,
              roty=roty))
    H(h, part("ShowerPole", (0.25, 2.4, 0.25), (sx2, y + 3.6, sz2), SILVER,
              METAL, roty=roty, cancollide=False))


def f_stairs(h, x, y, z, steps=10, rise=1.1, run_=1.1, w=4, dirz=1,
             dirx=0, color=OFFWHITE):
    """Straight staircase rising `steps` steps toward +Z*dirz (+X*dirx)."""
    for i in range(steps):
        if dirx:
            H(h, part(f"Step{i}", (run_ + 0.25, 0.4, w),
                      (x + dirx * run_ * i, y + rise * (i + 0.5), z),
                      color, PLASTIC))
        else:
            H(h, part(f"Step{i}", (w, 0.4, run_ + 0.25),
                      (x, y + rise * (i + 0.5), z + dirz * run_ * i),
                      color, PLASTIC))
    if dirx:
        H(h, part("StairRail", (steps * run_ + 1, 0.25, 0.25),
                  (x + dirx * run_ * (steps - 1) / 2,
                   y + rise * steps * 0.55 + 2.6, z + w / 2 - 0.2),
                  DARKWOOD, WOOD, cancollide=False))
    else:
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


def f_door(h, x, y, z, w=4, hgt=7, color=DARKWOOD, roty=0):
    """Framed door: side posts + lintel + solid panel with knob (Lua swings)."""
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))
    ox, oz = -sa * 0.35, -ca * 0.35  # trim sits proud of the wall face
    for sx_ in (-1, 1):
        H(h, part("DoorPost", (0.5, hgt + 0.3, 0.9),
                  (x + sx_ * w / 2 * ca + ox, y + (hgt + 0.3) / 2,
                   z + sx_ * w / 2 * sa + oz), DARKWOOD, WOOD, roty=roty))
    H(h, part("DoorLintel", (w + 1, 0.5, 0.9), (x + ox, y + hgt + 0.25, z + oz),
              DARKWOOD, WOOD, roty=roty))
    H(h, part("Door", (w - 0.4, hgt - 0.3, 0.5), (x, y + (hgt - 0.3) / 2, z),
              color, WOOD, roty=roty))
    H(h, part("DoorKnob", (0.35, 0.35, 0.35), (x + (w / 2 - 0.6) * ca,
              y + hgt / 2, z + (w / 2 - 0.6) * sa), GOLD, FOIL, shape=BALL,
              cancollide=False))


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
    H(h, part("Pot", (1.2 * s, 1.4 * s, 1.2 * s), (x, y + 0.7 * s, z), POTC,
              WOOD, shape=CYL))
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


def f_fence(h, x, z, length, roty=0, y=0, color=OFFWHITE, gap=None):
    """Fence run along local X. gap=(center,width) leaves an opening and
    places a swinging Gate part inside it (auto-opens via HouseLogic)."""
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))

    def seg(sx, slength):
        if slength < 1.2:
            return
        n = max(int(slength // 3), 1)
        mx = x + sx * ca
        mz = z + sx * sa
        for i in range(n + 1):
            lx = -slength / 2 + i * (slength / n)
            px, pz = mx + lx * ca, mz + lx * sa
            H(h, part("FencePost", (0.4, 4, 0.4), (px, y + 2, pz), color,
                      WOOD, roty=roty))
        H(h, part("FenceRailA", (slength, 0.3, 0.2), (mx, y + 1.2, mz),
                  color, WOOD, roty=roty, cancollide=False))
        H(h, part("FenceRailB", (slength, 0.3, 0.2), (mx, y + 2.8, mz),
                  color, WOOD, roty=roty, cancollide=False))

    gap_list = gap if isinstance(gap, list) else ([gap] if gap else [])
    if gap_list:
        # segments between gaps, then one gate per gap
        edge = -length / 2
        for gc, gw in sorted(gap_list):
            seg(edge, (gc - gw / 2) - edge)
            edge = gc + gw / 2
        seg(edge, length / 2 - edge)
        for gc, gw in gap_list:
            H(h, part("Gate", (gw - 0.6, 4, 0.35),
                      (x + gc * ca, y + 2, z + gc * sa), color, PLANKS,
                      roty=roty))
    else:
        seg(0, length)


def f_trafficlight(h, x, z, idx, roty=0, y=0):
    """Working traffic light: pole + 3 lamps (red/yellow/green) animated by
    HouseLogic. idx offsets the phase so nearby lights alternate."""
    H(h, part("TLPole", (0.5, 13, 0.5), (x, y + 6.5, z), (40, 40, 44), METAL))
    H(h, part("TLHead", (2.4, 6, 1.6), (x, y + 10, z), (30, 30, 34), SMOOTH,
              roty=roty))
    H(h, part("TLVisor", (2.8, 0.5, 2.2), (x, y + 11.4, z), (30, 30, 34),
              SMOOTH, roty=roty, cancollide=False))
    lamp_colors = {"R": (255, 60, 60), "Y": (255, 200, 40),
                   "G": (60, 200, 90)}
    for nm, ly in (("R", 11.6), ("Y", 10), ("G", 8.4)):
        H(h, part(f"TLamp_{nm}{idx}", (1.3, 1.3, 0.5),
                  (x, y + ly, z), lamp_colors[nm], NEON,
                  roty=roty, cancollide=False))


def f_roadsign(h, x, z, kind, roty=0, y=0):
    """Traffic sign: dark post + colored sign board with simple markings.
    kind: 'stop' | 'yield' | 'noentry' | 'parking' | 'speed' | 'crossing'
    Board faces -Z at roty=0 (read from the front)."""
    H(h, part("SignPost", (0.35, 7, 0.35), (x, y + 3.5, z), (40, 40, 44),
              METAL))
    if kind == "stop":
        H(h, part("SignBoard", (3.6, 3.6, 0.25), (x, y + 6.4, z), (170, 30,
                  30), PLASTIC, shape=CYL, rotz=90))
        H(h, part("SignMark", (2.2, 0.5, 0.3), (x, y + 6.4, z - 0.16),
                  (240, 240, 240), PLASTIC, cancollide=False))
    elif kind == "yield":
        for i, (wy, ww) in enumerate(((7.0, 2.4), (6.2, 1.6), (5.4, 0.8))):
            H(h, part("SignMark", (ww, 0.4, 0.3), (x, y + wy, z - 0.16),
                      (240, 240, 240), PLASTIC, cancollide=False))
        H(h, part("SignBoard", (3.6, 3.6, 0.22), (x, y + 6.2, z), (240, 240,
                  240), PLASTIC, shape=CYL, rotz=90))
    elif kind == "noentry":
        H(h, part("SignBoard", (3.6, 3.6, 0.25), (x, y + 6.4, z), (240, 240,
                  240), PLASTIC, shape=CYL, rotz=90))
        H(h, part("SignMark", (2.6, 2.6, 0.3), (x, y + 6.4, z - 0.16), (200,
                  40, 40), PLASTIC, shape=CYL, rotz=90, cancollide=False))
        H(h, part("SignBar", (2.6, 0.55, 0.3), (x, y + 6.4, z - 0.2),
                  (240, 240, 240), PLASTIC, cancollide=False))
    elif kind == "parking":
        H(h, part("SignBoard", (3.4, 4.4, 0.25), (x, y + 6.4, z), (40, 90,
                  200), PLASTIC))
        H(h, part("SignMark", (2.4, 0.5, 0.3), (x, y + 7.2, z - 0.16),
                  (240, 240, 240), PLASTIC, cancollide=False))
        H(h, part("SignMark", (0.5, 2.2, 0.3), (x, y + 6.2, z - 0.16),
                  (240, 240, 240), PLASTIC, cancollide=False))
    elif kind == "speed":
        H(h, part("SignBoard", (3.6, 3.6, 0.25), (x, y + 6.4, z), (240, 240,
                  240), PLASTIC, shape=CYL, rotz=90))
        H(h, part("SignRing", (2.6, 2.6, 0.3), (x, y + 6.4, z - 0.16), (200,
                  40, 40), PLASTIC, shape=CYL, rotz=90, cancollide=False))
        H(h, part("SignMark", (1.4, 1.4, 0.3), (x, y + 6.4, z - 0.18), (30,
                  30, 34), PLASTIC, cancollide=False))
    elif kind == "crossing":
        H(h, part("SignBoard", (4.2, 3.4, 0.25), (x, y + 6.4, z), (240, 200,
                  40), PLASTIC))
        for i in range(3):
            H(h, part("SignMark", (0.5, 2, 0.3), (x - 0.7 + i * 0.7,
                      y + 6.2, z - 0.16), (30, 30, 34), PLASTIC,
                      cancollide=False))
    H(h, part("SignCap", (0.6, 0.3, 0.6), (x, y + 8.2, z), (40, 40, 44),
              METAL, cancollide=False))


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
    H(h, part("FountainPillar", (1.6, 3, 1.6), (x, y + 2.4, z), MARBLEC,
              MARBLE, shape=CYL))
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

LIFT_OFF = True
H("Shared", part("Ground", (1000, 1, 1000), (0, -0.5, 70), (106, 160, 80),
                 GRASS))
# CityPlatform pieces: two holes — stairs (x 71..79, z 1..13) and station
# lift (x 88..94, z 1..7)
H("Shared", part("CityPlatformN", (1040, 2, 507), (0, 23, 266.5), (140, 140,
                 146), CONCRETE))
H("Shared", part("CityPlatformS", (1040, 2, 521), (0, 23, -259.5), (140,
                 140, 146), CONCRETE))
H("Shared", part("CityPlatformW", (591, 2, 12), (-224.5, 23, 7), (140, 140,
                 146), CONCRETE))
H("Shared", part("CityPlatformMid", (9, 2, 12), (83.5, 23, 7), (140, 140,
                 146), CONCRETE))
H("Shared", part("CityPlatformE", (426, 2, 12), (307, 23, 7), (140, 140,
                 146), CONCRETE))
# support pillars under the platform
for px, pz in ((150, 150), (150, 400), (400, 150), (400, 400), (-150, 150),
               (-150, 400), (-400, 150), (-400, 400), (300, -100),
               (-300, -100), (0, -300), (0, 300), (250, 250), (-250, 250)):
    H("Shared", part("SupportPillar", (10, 22, 10), (px, 11, pz), (130, 130,
                     134), CONCRETE))
# underground METRO NETWORK: 4 stations on one east-west line at z=0
METRO_STATIONS = [
    ("Selatan", -170), ("Plaza", 0), ("Timur", 160), ("Utara", 330),
]
for st_name, st_x in METRO_STATIONS:
    H("Shared", part(f"MStationFloor_{st_name}", (94, 2, 54), (st_x, 1, 0),
                     (60, 60, 66), CONCRETE))
    H("Shared", part(f"MStationCeil_{st_name}", (94, 2, 54), (st_x, 21, 0),
                     (70, 70, 76), CONCRETE))
    H("Shared", part(f"MStationWallB_{st_name}", (94, 18, 2), (st_x, 11, 26),
                     (80, 80, 86), CONCRETE))
    H("Shared", part(f"MStationWallF_{st_name}", (94, 18, 2), (st_x, 11,
                     -26), (80, 80, 86), CONCRETE))
    # platform di KEDUA sisi jalur (rel lewat di tengah, z=0)
    H("Shared", part(f"MStationPlatform_{st_name}", (26, 2, 7),
                     (st_x - 25, 3, -7), (200, 200, 206), MARBLE))
    H("Shared", part(f"MStationPlatform2_{st_name}", (26, 2, 7),
                     (st_x - 25, 3, 7), (200, 200, 206), MARBLE))
    H("Shared", part(f"MStationLine_{st_name}", (26, 0.2, 0.6),
                     (st_x - 25, 4.15, -3.8), (240, 200, 40), PLASTIC,
                     cancollide=False))
    H("Shared", part(f"MStationLine2_{st_name}", (26, 0.2, 0.6),
                     (st_x - 25, 4.15, 3.8), (240, 200, 40), PLASTIC,
                     cancollide=False))
    # REL STASIUN: meneruskan jalur rel terowongan melewati stasiun
    H("Shared", part(f"MStationTrack_{st_name}", (94, 0.6, 7),
                     (st_x, 2.3, 0), (50, 50, 54), SLATE))
    H("Shared", part(f"MStationSignB_{st_name}", (20, 2.4, 0.4),
                     (st_x - 24, 15.5, -25.4), (30, 30, 34), SMOOTH))
    H("Shared", part(f"MStationSign2B_{st_name}", (20, 2.4, 0.4),
                     (st_x - 24, 15.5, 25.4), (30, 30, 34), SMOOTH))
    # waiting amenities per station: benches, ticket kiosk, vending
    for bx in (-36, -28):
        H("Shared", part(f"MBench_{st_name}_{bx}", (6, 0.4, 1.8),
                         (st_x + bx, 4.2, -10), (110, 52, 38), WOOD))
        for lx in (-2.4, 2.4):
            H("Shared", part("MBenchLeg", (0.4, 1.8, 1.6),
                             (st_x + bx + lx, 3.1, -10), (40, 40, 44),
                             METAL, cancollide=False))
        H("Shared", part(f"MBenchBack_{st_name}_{bx}", (6, 1.6, 0.3),
                         (st_x + bx, 5.4, -10.8), (110, 52, 38), WOOD,
                         cancollide=False))
    H("Shared", part(f"MKiosk_{st_name}", (4, 5, 3), (st_x - 40, 4.5, -20),
                     (90, 140, 90), PLASTIC))
    H("Shared", part(f"MKioskSign_{st_name}", (3, 1.2, 0.2),
                     (st_x - 40, 7.6, -20), (255, 200, 40), NEON,
                     cancollide=False))
    H("Shared", part(f"MVend_{st_name}", (2.4, 6.5, 2), (st_x + 40, 5.25,
                     -24), (200, 40, 40), SMOOTH))
    for si, ch in enumerate(st_name.upper()):
        H("Shared", part(f"MStationSignC_{st_name}_{si}", (1, 1.6, 0.2),
                         (st_x - 24 - (len(st_name) - 1) * 0.6
                          + si * 1.2, 15.5, -25.65), GOLD, NEON,
                         cancollide=False))
# tunnels between stations
for ti in range(len(METRO_STATIONS) - 1):
    a_x = METRO_STATIONS[ti][1] + 47
    b_x = METRO_STATIONS[ti + 1][1] - 47
    tlen = b_x - a_x
    tcx = (a_x + b_x) / 2
    H("Shared", part(f"MetroTunnelFloor{ti}", (tlen, 2, 20), (tcx, 1, 0),
                     (55, 55, 60), CONCRETE))
    H("Shared", part(f"MetroTunnelCeil{ti}", (tlen, 2, 20), (tcx, 21, 0),
                     (55, 55, 60), CONCRETE))
    H("Shared", part(f"MetroTunnelWallN{ti}", (tlen, 20, 2), (tcx, 11, 10),
                     (60, 60, 66), CONCRETE))
    H("Shared", part(f"MetroTunnelWallS{ti}", (tlen, 20, 2), (tcx, 11, -10),
                     (60, 60, 66), CONCRETE))
    H("Shared", part(f"MetroTunnelTrack{ti}", (tlen, 0.6, 7), (tcx, 2.3, 0),
                     (50, 50, 54), SLATE))

for i in range(3):
    H("Shared", part("TrainCar", (20, 6, 8), (47 + i * 21, 6.4, 0), (220,
                     220, 226), SMOOTH))
    for sgn in (-1, 1):
        H("Shared", part("TrainWindow", (16, 1.8, 0.4), (5 + i * 21, 7.6,
                         18 + sgn * 4.1), (140, 190, 230), GLASS,
                         transparency=0.3, cancollide=False))
    H(h if False else "Shared", part("TrainStripe", (20, 1, 0.5),
                     (47 + i * 21, 4.2, 4.1 if i % 2 == 0 else -4.1),
                     (220, 60, 60), PLASTIC, cancollide=False))
    # interior: floor, seats along walls, hand poles, ceiling lights, doors
    H("Shared", part("TrainFloorIn", (19, 0.4, 7), (47 + i * 21, 4.6, 0),
                     (90, 90, 96), SMOOTH))
    for sgn in (-1, 1):
        for row in range(4):
            H("Shared", part("TrainSeat", (3.4, 0.4, 1.4),
                             (47 + i * 21 - 6 + row * 4, 5.3, sgn * 2.6), (60, 90, 160), FABRIC,
                             cancollide=False))
            H("Shared", part("TrainSeatBack", (3.4, 1.6, 0.3),
                             (47 + i * 21 - 6 + row * 4, 6.3, sgn * 3.3), (60, 90, 160), FABRIC,
                             cancollide=False))
        for px in (-8, -2.6, 2.6, 8):
            H("Shared", part("TrainPole", (0.25, 2.6, 0.25),
                             (47 + i * 21 + px, 7.2, sgn * 3.2),
                             (200, 200, 210), METAL, cancollide=False))
    H("Shared", part("TrainCeil", (19, 0.3, 7), (47 + i * 21, 9, 0), (230,
                     230, 236), SMOOTH))
    for lx in (-6, 0, 6):
        H("Shared", part("TrainLamp", (3, 0.2, 1), (47 + i * 21 + lx, 8.8, 0), (255, 245, 220), NEON, cancollide=False))
    for dx in (-9.6, 9.6):
        H("Shared", part("TrainDoor", (0.4, 4.4, 1.8), (47 + i * 21 + dx, 6.8, 0), (70, 70, 76), SMOOTH))
    if i == 0:
        H("Shared", part("TrainCabWall", (0.4, 6, 7.6), (37.6, 6.4, 0),
                         (70, 70, 76), SMOOTH))
        H("Shared", part("TrainConsole", (2.4, 1.6, 3), (36.4, 6, 0),
                         (40, 40, 46), METAL))
        H("Shared", part("TrainConsoleScreen", (0.3, 1, 2.2), (35.2, 6.4, 0), (60, 200, 120), NEON, cancollide=False))
for pz in (-20, 20):
    H("Shared", part("StationPillar", (3, 18, 3), (-12, 11, pz), (110, 110,
                     116), CONCRETE))
    H("Shared", part("StationPillar", (3, 18, 3), (30, 11, pz), (110, 110,
                     116), CONCRETE))
for px in (-38, 0, 38):
    H("Shared", part("StationNeon", (50, 0.4, 1.4), (px, 19.4, 0), (255,
                     245, 220), NEON, cancollide=False))
# station interior: benches, kiosk, vending machines, clock, trash cans,
# route map, turnstiles, waiting area
for bx in (-34, -26, -14):
    H("Shared", part("StationBench", (6, 0.4, 1.8), (bx, 4.2, 8), (110, 52,
                     38), WOOD))
    for lx in (-2.4, 2.4):
        H("Shared", part("StationBenchLeg", (0.4, 1.8, 1.6), (bx + lx,
                         3.1, 8), (40, 40, 44), METAL, cancollide=False))
    H("Shared", part("StationBenchBack", (6, 1.6, 0.3), (bx, 5.4, 8.8),
                     (110, 52, 38), WOOD, cancollide=False))
H("Shared", part("StationKiosk", (5, 5, 4), (40, 4.5, -20), (90, 140, 90),
                 PLASTIC))
H(h if False else "Shared", part("StationKioskTop", (5.6, 0.4, 4.6),
                 (40, 7.2, -20), (110, 52, 38), WOOD))
H("Shared", part("StationKioskSign", (3.4, 1.4, 0.2), (40, 8.2, -20),
                 (255, 200, 40), NEON, cancollide=False))
for vx in (-38, -34):
    H("Shared", part("StationVending", (2.4, 6.5, 2), (vx, 5.25, -24),
                     (200, 40, 40) if vx == -38 else (40, 90, 200), SMOOTH))
    H(h if False else "Shared", part("StationVendGlass", (1.8, 4, 0.15),
                     (vx, 5.6, -25.1), (200, 225, 240), GLASS,
                     transparency=0.5, cancollide=False))
H("Shared", part("StationClock", (0.3, 4, 4), (-25, 17, 0), (240, 240, 245),
                 SMOOTH, cancollide=False))
H("Shared", part("StationClockFace", (0.2, 3.2, 3.2), (-25.3, 17, 0),
                 (255, 255, 255), PLASTIC, cancollide=False))
H("Shared", part("StationClockHand", (0.15, 0.3, 1.4), (-25.5, 17, 0),
                 (30, 30, 34), SMOOTH, cancollide=False))
for tx2 in (-36, 30):
    H("Shared", part("StationTrash", (1.4, 2.6, 1.4), (tx2, 3.3, 8), (60,
                     110, 70), SMOOTH))
H("Shared", part("StationMap", (0.3, 5, 9), (-45.6, 12, 0), (40, 90, 200),
                 PLASTIC, cancollide=False))
H("Shared", part("StationMapLine", (0.2, 0.4, 7), (-45.4, 12.6, 0), (240,
                 240, 240), PLASTIC, cancollide=False))
for stn in (-40, -30, -20, -10, 0, 10, 20):
    H("Shared", part("StationMapDot", (0.25, 1, 1), (-45.35, 12.6, stn),
                     (255, 200, 40), NEON, cancollide=False))
# turnstiles between platform and concourse
for tx3 in (-32, -28, -24, -20):
    H("Shared", part("TurnstileBody", (0.6, 3.4, 2.4), (tx3, 4.7, -2),
                     (90, 90, 96), METAL))
    H("Shared", part("TurnstileArm", (0.3, 0.3, 2), (tx3, 3.4, -3.4),
                     (220, 200, 40), METAL, cancollide=False))
# waiting-area chairs near the lift
for cx2 in (86, 89, 92):
    H("Shared", part("StationChair", (2.2, 0.35, 2), (cx2, 4.2, -20),
                     (50, 90, 160), PLASTIC))
    H("Shared", part("StationChairLeg", (0.3, 1.8, 1.6), (cx2, 3.1, -20),
                     (40, 40, 44), METAL, cancollide=False))
    H("Shared", part("StationChairBack", (2.2, 1.4, 0.25), (cx2, 5.2, -21),
                     (50, 90, 160), PLASTIC, cancollide=False))
H("Shared", part("StationSignBoard", (24, 3, 0.4), (0, 14, -25.4), (30, 30,
                 34), SMOOTH))
for i, ch in enumerate("STASIUN"):
    H("Shared", part("StationSignC", (1.4, 2, 0.2),
                     (-6.3 + i * 1.8, 14, -25.65), GOLD, NEON,
                     cancollide=False))
# stair shaft: platform (y 42) down into the station
H("Shared", part("ShaftWallW", (1, 24, 34), (70.5, 12, -4), (120, 120, 126),
                 CONCRETE))
H("Shared", part("ShaftWallE", (1, 24, 34), (79.5, 12, -4), (120, 120, 126),
                 CONCRETE))
H("Shared", part("ShaftWallS", (10, 24, 1), (75, 12, 12.5), (120, 120, 126),
                 CONCRETE))
f_stairs("Shared", 75, 2, -12, steps=22, rise=1.0, run_=1.0, w=6, dirz=1,
         color=(150, 150, 156))
# station elevator: glass shaft x 88..94, stops at station floor & platform
for px in (88, 94):
    H("Shared", part("LiftShaftWall", (0.4, 40, 6), (px, 22, 4), GLASSC,
                     GLASS, transparency=0.55))
H("Shared", part("LiftShaftBack", (6, 40, 0.4), (91, 22, 1), GLASSC, GLASS,
                 transparency=0.55))
H("Shared", part("LiftCab", (5.4, 0.5, 5), (91, 3.75, 4), (60, 60, 66),
                 METAL))
for dx, dz, sx_, sz_ in ((0, -2.4, 5.4, 0.2), (-2.4, 0, 0.2, 5),
                         (2.4, 0, 0.2, 5)):
    H("Shared", part("LiftCabWall", (sx_, 3, sz_), (91 + dx, 5.6, 4 + dz),
                     GLASSC, GLASS, transparency=0.3, cancollide=False))
LIFT_OFF = False
H("Shared", part("Plaza", (60, 0.3, 40), (0, 0.15, 0), MARBLEC, MARBLE))

# cobble main street X-axis at z=25
for i in range(26):
    H("Shared", part(f"Street{i}", (8, 0.2, 7), (-100 + i * 8, 0.1, 25), PATHC,
                     COBBLE))
# connectors north/south
for i in range(20):
    H("Shared", part(f"ConnN{i}", (7, 0.2, 8), (-76 + i * 8, 0.1, 31), PATHC,
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
    f'<Vector3 name="size"><X>15</X><Y>0.4</Y><Z>15</Z></Vector3>'
    f'<CoordinateFrame name="CFrame"><X>0</X><Y>42.4</Y><Z>21</Z>'
    f'<R00>1</R00><R01>0</R01><R02>0</R02><R10>0</R10><R11>1</R11><R12>0</R12>'
    f'<R20>0</R20><R21>0</R21><R22>1</R22></CoordinateFrame>'
    f'<token name="TopSurface">0</token><token name="BottomSurface">0</token>'
    f'</Properties></Item>')
H("Shared", spawn)


# ================================================================ HOUSE A
# ================= ModernCube builder =================
def build_ModernCube(cx, cz, FY, hname):
    global h
    h = hname

    H(h, part("Lot", (34, 0.2, 30), (cx, 0.1, cz), (150, 150, 148), CONCRETE))
    H(h, part("Floor", (24, 0.5, 18), (cx, FY - 0.25, cz), MARBLEC, MARBLE))
    # Floor2 with stairwell hole (left side, x -12..-8, z -7.5..1)
    H(h, part("Floor2Main", (20, 0.5, 18), (cx + 2, FY + 9.75, cz), MARBLEC,
              MARBLE))
    H(h, part("Floor2Front", (4, 0.5, 1.5), (cx - 10, FY + 9.75, cz - 8.25),
              MARBLEC, MARBLE))
    H(h, part("Floor2Back", (4, 0.5, 8), (cx - 10, FY + 9.75, cz + 5), MARBLEC,
              MARBLE))
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
    f_door(h, cx, FY, cz - 9, w=8, hgt=7)

    # gold accent beam
    H(h, part("GoldBeamF1", (24, 0.3, 0.3), (cx, FY + 8.8, cz - 8.7), GOLD, FOIL,
              cancollide=False))
    H(h, part("GoldBeamF2", (24, 0.3, 0.3), (cx, FY + 18.8, cz + 8.7), GOLD, FOIL,
              cancollide=False))

    # F1: living room
    f_rug(h, cx - 5, FY, cz, 10, 8, (70, 80, 95), border=(40, 48, 60))
    f_sofa(h, cx - 5.5, FY, cz - 2, SOFA_NAVY, roty=180)
    f_loveseat(h, cx - 10.4, FY, cz + 4.5, SOFA_NAVY, roty=90)
    f_coffee_table(h, cx - 5, FY, cz + 0.5)
    f_tv(h, cx - 5, FY, cz + 7.6, roty=0, w=4)
    f_bookshelf(h, cx + 11, FY, cz + 4, roty=-90, w=8, hgt=7)
    f_floorlamp(h, cx - 10, FY, cz + 7)
    f_plant(h, cx + 9.3, FY, cz - 4.5, big=True)
    f_painting(h, cx - 11.5, FY + 5.5, cz + 4, roty=90, color=(40, 70, 120))
    f_painting(h, cx + 11.5, FY + 5.5, cz - 4, roty=-90, color=(120, 60, 40))

    # F1: dining + kitchen (right half)
    f_dining(h, cx + 5, FY, cz + 5, seats=6, w=6)
    f_kitchen(h, cx + 6.4, FY, cz - 7.5, run=5)
    f_chandelier(h, cx + 5, FY + 8.4, cz + 5, 0.9, tiers=1, bulbs_per=4)

    # F2: mezzanine — stairs along right wall, master suite
    f_stairs(h, cx - 10, FY, cz - 6.5, steps=10, rise=1.0, run_=0.8, w=3.4,
             dirz=1)
    f_railing(h, cx - 8, FY + 9.7, cz - 3.25, length=8.5, roty=90)
    f_bed(h, cx - 4.2, FY + 10, cz + 4, roty=0, size=1.1, headcolor=MAHOGANY)
    f_nightstand(h, cx - 7.7, FY + 10, cz + 2)
    f_nightstand(h, cx - 0.7, FY + 10, cz + 1)
    f_wardrobe(h, cx + 3.2, FY + 10, cz + 7.6, w=8)
    f_rug(h, cx - 3.7, FY + 10, cz + 1, 7, 6, CARPET_CREAM, border=GOLD)
    f_armchair(h, cx - 6.5, FY + 10, cz - 5, roty=45)
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

    f_fence(h, cx, cz - 14, 34, y=0.2, gap=(0, 11))
    f_fence(h, cx, cz + 14.8, 32, y=0.2)
    f_tree(h, cx - 14, cz + 10, s=0.9)
    f_flowerbed(h, cx + 6, cz - 13, w=10, d=2.5)


    # ================================================================ HOUSE B

# ================= AFrame builder =================
def build_AFrame(cx, cz, FY, hname):
    global h
    h = hname

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
    f_door(h, cx, FY, cz - 9.8, w=4.2, hgt=6.5, color=DARKWOOD)
    f_window(h, cx - 4.5, FY + 1.8, cz + 2, w=2.6, hgt=3.5, roty=90, t=0.5)
    f_window(h, cx + 4.5, FY + 1.8, cz - 2, w=2.6, hgt=3.5, roty=90, t=0.5)

    # beams
    for bz in (-6, 0, 6):
        H(h, part(f"Beam{bz}", (5, 0.5, 0.5), (cx, FY + 10.5, cz + bz), DARKWOOD,
                  WOOD, cancollide=False))

    f_fireplace(h, cx + 2.5, FY, cz + 8.6, roty=0, w=3.5, chimney=False)
    H(h, part("Chimney", (1.5, 4, 1.2), (cx + 2.5, FY + 9, cz + 8.6), (95, 50, 44),
              BRICK))
    f_rug(h, cx - 1, FY, cz - 1, 9, 7, (120, 70, 40), border=(90, 52, 30))
    f_sofa(h, cx - 2.4, FY, cz - 2, (110, 75, 55), roty=90)
    f_armchair(h, cx + 2, FY, cz - 2, (110, 75, 55), roty=135)
    f_coffee_table(h, cx - 0.5, FY, cz - 2, w=3.5, mat=WOOD, color=WOODC, leg=BRONZE)
    f_tv(h, cx - 5.6, FY, cz - 2, roty=-90, w=4)
    f_bookshelf(h, cx + 3.3, FY, cz + 3, roty=-90, w=5, hgt=6)
    f_floorlamp(h, cx - 6.5, FY, cz - 5)
    f_plant(h, cx - 5.8, FY, cz - 6.5)
    f_dining(h, cx + 3.6, FY, cz - 5.8, seats=4, w=4.5, roty=90)
    f_chandelier(h, cx, FY + 13.6, cz, 0.8, tiers=1, bulbs_per=5)
    for bz in (-6, 0, 6):
        H(h, part(f"Antler{bz}", (2, 0.8, 0.4), (cx, FY + 12.6, cz + bz), BRONZE,
                  WOOD, cancollide=False))

    # ground-floor bedroom nook (vaulted ceiling)
    f_bed(h, cx - 4, FY, cz + 5.8, roty=180, size=0.95, headcolor=MAHOGANY)
    f_nightstand(h, cx - 0.55, FY, cz + 7.5)
    f_rug(h, cx - 4, FY, cz + 4, 6, 5, (140, 90, 55))
    f_painting(h, cx - 7.6, FY + 5, cz + 4, roty=90, color=(70, 110, 70))

    f_fence(h, cx, cz - 14, 28, y=0.2, gap=(0, 11))
    f_fence(h, cx, cz + 14.8, 28, y=0.2)
    f_tree(h, cx - 11, cz + 9, s=1.0)
    f_tree(h, cx + 11, cz + 10, s=0.8)
    f_flowerbed(h, cx - 5, cz - 13, w=8, d=2.5)
    f_flowerbed(h, cx + 5, cz - 13, w=8, d=2.5)


    # ================================================================ HOUSE C

# ================= Castle builder =================
def build_Castle(cx, cz, FY, hname):
    global h
    h = hname

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
    f_door(h, cx, FY, cz - 11, w=7, hgt=7, color=DARKWOOD)
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
    f_bookshelf(h, cx - 11.2, FY, cz + 7, roty=90, w=7, hgt=9)
    f_painting(h, cx - 13.4, FY + 8, cz, roty=90, w=4, hgt=3, color=(70, 50, 110))
    f_painting(h, cx + 13.4, FY + 8, cz, roty=-90, w=4, hgt=3, color=(110, 70, 40))

    # tower: hollow ring of 12 wall panels, 3 floors, spiral stairs, cone top
    tx, tz = cx + 19, cz + 6
    H(h, part("TowerPad", (14, 0.5, 14), (tx, FY - 0.2, tz), STONE, COBBLE))
    TR_, TH_ = 5.5, 24  # tower radius / height
    for k in range(12):
        a = math.radians(k * 30)
        if k == 6:  # front sector = doorway (lintel fills above)
            continue
        H(h, part(f"TowerWall{k}", (3.0, TH_, 0.6),
                  (tx + TR_ * math.sin(a), FY + TH_ / 2, tz + TR_ * math.cos(a)),
                  STONE, COBBLE, roty=math.degrees(a) + 90))
    H(h, part("TowerLintel", (3.0, TH_ - 6, 0.6), (tx, FY + 6 + (TH_ - 6) / 2,
              tz - TR_), STONE, COBBLE))
    H(h, part("TowerFloor1", (0.5, 7, 7), (tx, FY + 6, tz), (200, 200, 205),
              SLATE, shape=CYL, rotz=90))
    H(h, part("TowerFloor2", (0.5, 7, 7), (tx, FY + 12, tz), (200, 200, 205),
              SLATE, shape=CYL, rotz=90))
    H(h, part("TowerFloor3", (0.5, 7, 7), (tx, FY + 18, tz), (200, 200, 205),
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
    H(h, part("Door", (2.2, 5.2, 0.4), (tx, FY + 2.6, tz - TR_ + 0.3),
              DARKWOOD, WOOD))
    f_chandelier(h, tx, FY + 4.9, tz, 0.9, tiers=1, bulbs_per=5)
    f_chandelier(h, tx, FY + 10.5, tz, 0.9, tiers=1, bulbs_per=5)
    f_bed(h, tx, FY + 12.25, tz, round_=True, size=0.8, color=(180, 170, 160))
    f_painting(h, tx, FY + 15.5, tz - 4.8, color=(60, 60, 120))

    f_fence(h, cx, cz - 17, 38, y=0.2, color=DARKSTONE, gap=(0, 10))
    f_fence(h, cx - 3, cz + 17.8, 32, y=0.2, color=DARKSTONE)
    f_fence(h, cx + 17, cz + 17.8, 12, y=0.2, color=DARKSTONE)
    f_tree(h, cx - 15, cz - 12, s=1.0)
    f_tree(h, cx + 2, cz - 14, s=0.9)


    # ================================================================ HOUSE D

# ================= VillaL builder =================
def build_VillaL(cx, cz, FY, hname):
    global h
    h = hname

    H(h, part("Lot", (44, 0.2, 40), (cx, 0.1, cz), (150, 150, 148), CONCRETE))
    H(h, part("FloorA", (20, 0.5, 14), (cx, FY - 0.25, cz), MARBLEC, MARBLE))
    H(h, part("FloorB", (10, 0.5, 14), (cx + 14.5, FY - 0.25, cz + 7), MARBLEC,
              MARBLE))
    # FloorA2 with stairwell hole (x -0.5..9.5, z 4.25..7)
    H(h, part("FloorA2Left", (9.5, 0.5, 14), (cx - 5.25, FY + 9.75, cz),
              MARBLEC, MARBLE))
    H(h, part("FloorA2Front", (10, 0.5, 11.25), (cx + 4.5, FY + 9.75,
              cz - 1.375), MARBLEC, MARBLE))
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
    f_door(h, cx - 3, FY, cz - 7, w=4.2, hgt=7)
    f_door(h, cx + 14.5, FY, cz, w=4, hgt=6.5, roty=0)
    H(h, part("GoldBeamA", (20, 0.3, 0.3), (cx, FY + 8.7, cz - 6.7), GOLD, FOIL,
              cancollide=False))
    H(h, part("GoldBeamA2", (20, 0.3, 0.3), (cx, FY + 18.7, cz - 6.7), GOLD, FOIL,
              cancollide=False))

    # F1: open living + kitchen
    f_rug(h, cx - 5.5, FY, cz + 0.5, 10, 8, (185, 160, 110), border=(150, 128, 85))
    f_sofa(h, cx - 4.5, FY, cz + 0.5, (100, 105, 118), w=7, roty=90)
    f_coffee_table(h, cx - 6.8, FY, cz + 0.5, w=4)
    f_tv(h, cx - 8.4, FY, cz + 0.5, roty=-90, w=5)
    f_kitchen(h, cx + 8.1, FY, cz + 1.2, roty=-90, run=6, fridge=True)
    f_dining(h, cx + 2.5, FY, cz - 2.5, seats=6, w=6)
    f_chandelier(h, cx + 5, FY + 8.4, cz + 1, 1.0, tiers=2, bulbs_per=5)
    f_plant(h, cx + 9.5, FY, cz + 5.5, big=True)
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
    f_floorlamp(h, cx - 11, FY + 0.3, cz - 9)
    for i, lcx in enumerate((cx - 13.2, cx + 1.2)):
        H(h, part("LoungeChair", (2, 0.4, 5), (lcx, FY + 0.5,
                  cz - 11), OFFWHITE, FABRIC, roty=90 + i * 180))
        H(h, part("LoungeBack", (2, 2.2, 0.4), (lcx, FY + 1.5,
                  cz - 13), OFFWHITE, FABRIC, cancollide=False))

    # F2: stairs + bedrooms
    f_stairs(h, cx + 0.5, FY, cz + 6, steps=10, rise=1.0, run_=0.8, w=3.5,
             dirx=1)
    H(h, part("StairLanding", (1.8, 0.5, 2.75), (cx + 8.6, FY + 9.75,
              cz + 5.625), MARBLEC, MARBLE))
    f_railing(h, cx + 4.5, FY + 9.7, cz + 3.75, length=10, roty=0)
    f_railing(h, cx + 9.5, FY + 9.7, cz + 10.5, length=7, roty=90)
    f_bed(h, cx - 5, FY + 10, cz + 4.2, roty=180, size=1.05, headcolor=MAHOGANY)
    f_nightstand(h, cx - 8.5, FY + 10, cz + 2)
    f_rug(h, cx - 5, FY + 10, cz + 1, 8, 6, CARPET_CREAM, border=(170, 150, 120))
    f_bathroom(h, cx + 5, FY + 10, cz + 2.5)
    f_wardrobe(h, cx - 5, FY + 10, cz - 5.5, w=5)
    f_bed(h, cx + 15, FY + 10, cz + 9.8, roty=180, size=0.9, headcolor=MAHOGANY)
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

    f_fence(h, cx - 3, cz - 19, 42, y=0.2, gap=(0, 10))
    f_fence(h, cx, cz + 19.8, 42, y=0.2)
    f_tree(h, cx + 17, cz - 15, s=1.0)
    f_tree(h, cx - 17, cz + 15, s=0.85)
    f_flowerbed(h, cx + 10, cz - 18, w=12, d=2.5)


    # ================================================================ HOUSE E

# ================= Dome builder =================
def build_Dome(cx, cz, FY, hname):
    global h
    h = hname

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
    f_door(h, cx, FY, cz - 8.2, w=5.5, hgt=6, color=GLASSC)
    f_chandelier(h, cx, FY + 12.6, cz, 1.0, tiers=1, bulbs_per=6)
    f_rug(h, cx, FY, cz, 12, 12, (90, 60, 110), border=(60, 40, 80))
    f_bed(h, cx, FY, cz + 2.5, round_=True, size=1.15)
    f_nightstand(h, cx - 4.0, FY, cz + 0.5)
    f_nightstand(h, cx + 4.0, FY, cz + 0.5)
    f_armchair(h, cx - 3.2, FY, cz - 2.4, SOFA_BEIGE, roty=60)
    f_loveseat(h, cx + 3.2, FY, cz - 2.4, SOFA_BEIGE, roty=-60)
    f_coffee_table(h, cx, FY, cz - 3.5, w=3, mat=WOOD, color=DARKWOOD)
    f_plant(h, cx - 3.4, FY, cz - 5.6, big=True)
    f_plant(h, cx + 3.4, FY, cz - 5.6, big=True)
    f_bookshelf(h, cx + 3.6, FY, cz + 4.4, roty=-90, w=5, hgt=5)
    f_floorlamp(h, cx + 1.4, FY, cz - 6.8)
    f_painting(h, cx - 7.7, FY + 4.5, cz + 2, roty=90, color=(80, 120, 160))

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
    f_fence(h, cx, cz - 16, 32, y=0.2, gap=(0, 10))
    f_fence(h, cx - 8, cz + 16.8, 16, y=0.2)
    f_fence(h, cx + 8, cz + 16.8, 16, y=0.2)
    f_flowerbed(h, cx, cz - 15, w=10, d=2.5)


    # ================================================================ HOUSE F

# ================= ZenHouse builder =================
def build_ZenHouse(cx, cz, FY, hname):
    global h
    h = hname

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
        px = cx - 8 + k * 3.7
        H(h, part(f"Panel{k}", (3.6, 7, 0.25), (px, FY + 3.75, cz - 8.5), (150, 90,
                  70), WOOD, cancollide=False))
    H(h, part("Panel3", (3.4, 7, 0.25), (cx + 9.1, FY + 3.75, cz - 8.5), (150, 90,
              70), WOOD, cancollide=False))
    f_door(h, cx + 4.5, FY, cz - 8.5, w=4.2, hgt=6.5, color=(150, 90, 70))
    H(h, part("WallL", (0.5, 7, 17), (cx - 11, FY + 3.75, cz), (225, 218, 200),
              PLASTIC))
    H(h, part("WallR", (0.5, 7, 17), (cx + 11, FY + 3.75, cz), (225, 218, 200),
              PLASTIC))
    # stairs + walkway
    f_stairs(h, cx + 4.5, 0.2, cz - 13.9, steps=6, rise=0.38, run_=0.9,
             w=4, dirz=1, color=DARKWOOD)

    # interior: low table, cushions, bonsai, bed niche
    H(h, part("LowTable", (6, 0.4, 3), (cx - 4, FY + 1.2, cz - 1), DARKWOOD, WOOD))
    for dx in (-1.8, 1.8):
        H(h, part("TableLeg", (0.4, 1, 0.4), (cx - 4 + dx, FY + 0.6, cz - 1),
                  DARKWOOD, WOOD))
    for dx, dz in ((-2.2, -2.6), (2.2, -2.6), (-2.2, 1.4), (2.2, 1.4)):
        H(h, part("Cushion", (1.8, 0.4, 1.8), (cx - 4 + dx, FY + 0.5, cz - 1 + dz),
                  (170, 60, 60), FABRIC))
    f_bed(h, cx + 6.5, FY, cz + 4.5, roty=180, size=0.9, headcolor=DARKWOOD)
    f_rug(h, cx + 6.5, FY, cz + 2, 6, 5, (170, 60, 60), border=(120, 40, 40))
    f_bookshelf(h, cx + 9.8, FY, cz - 4, roty=-90, w=5, hgt=6)
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


    # ================================================================ HOUSE G

# ================= TinyHouse builder =================
def build_TinyHouse(cx, cz, FY, hname):
    global h
    h = hname

    H(h, part("Lot", (26, 0.2, 26), (cx, 0.1, cz), (150, 150, 148), CONCRETE))
    H(h, part("Floor", (12, 0.5, 12), (cx, FY - 0.25, cz), WOODC, PLANKS))
    H(h, part("Roof", (13.5, 0.5, 13.5), (cx, FY + 8.7, cz), (105, 70, 50), PLANKS))
    H(h, part("RoofRim", (13.5, 0.7, 13.5), (cx, FY + 8.2, cz), DARKWOOD, WOOD,
              cancollide=False))
    H(h, part("Porch", (8, 0.4, 4), (cx, FY - 0.1, cz - 8), DARKWOOD, PLANKS))
    for px in (cx - 3.5, cx + 3.5):
        H(h, part("PorchPost", (0.5, 7, 0.5), (px, FY + 3.5, cz - 9.7), DARKWOOD,
                  WOOD))
    H(h, part("PorchBeam", (8, 0.5, 0.5), (cx, FY + 7, cz - 9.7), DARKWOOD, WOOD))

    H(h, part("WallBack", (12, 8, 0.5), (cx, FY + 4, cz + 6), (225, 210, 185),
              PLASTIC))
    H(h, part("WallL", (0.5, 8, 12), (cx - 6, FY + 4, cz), (225, 210, 185),
              PLASTIC))
    H(h, part("WallR", (0.5, 8, 12), (cx + 6, FY + 4, cz), (225, 210, 185),
              PLASTIC))
    H(h, part("WallFrontL", (3.5, 8, 0.5), (cx - 4.25, FY + 4, cz - 6), (225, 210,
              185), PLASTIC))
    H(h, part("WallFrontR", (3.5, 8, 0.5), (cx + 4.25, FY + 4, cz - 6), (225, 210,
              185), PLASTIC))
    H(h, part("WallFrontTop", (5, 2.5, 0.5), (cx, FY + 6.75, cz - 6), (225, 210,
              185), PLASTIC))
    f_door(h, cx, FY, cz - 6, w=4, hgt=5.5, color=(140, 90, 60))
    f_window(h, cx - 4.25, FY + 4.2, cz - 6, w=2.6, hgt=3.2, t=0.45)
    f_window(h, cx + 4.25, FY + 4.2, cz - 6, w=2.6, hgt=3.2, t=0.45)
    f_window(h, cx - 5.7, FY + 4.2, cz + 2, w=2.6, hgt=3.2, roty=90, t=0.45)

    f_rug(h, cx - 1.5, FY, cz + 1, 5, 5, (160, 100, 60), border=(120, 75, 45))
    f_sofa(h, cx - 3, FY, cz + 2.5, (150, 110, 70), w=4)
    f_coffee_table(h, cx - 1.5, FY, cz, w=2.8, mat=WOOD, color=WOODC, leg=BRONZE)
    f_tv(h, cx - 2, FY, cz - 4.6, roty=180, w=3.2)
    f_bed(h, cx + 2.2, FY, cz + 2.0, roty=90, size=0.85, headcolor=DARKWOOD)
    f_nightstand(h, cx + 2.2, FY, cz - 0.6)
    f_kitchen(h, cx - 1, FY, cz + 4.9, run=8, fridge=False)
    f_plant(h, cx + 4.8, FY, cz - 4.8)
    f_lantern(h, cx - 5.5, cz - 9.5, y=FY)
    f_lantern(h, cx + 5.5, cz - 9.5, y=FY)
    f_fence(h, cx, cz - 12, 24, y=0.2, color=(120, 85, 60), gap=(0, 9))
    f_fence(h, cx, cz + 12.8, 24, y=0.2, color=(120, 85, 60))
    f_tree(h, cx - 9, cz + 8, s=0.7)
    f_flowerbed(h, cx + 4, cz - 11, w=8, d=2)


    # ================================================================ HOUSE H

# ================= Mansion builder =================
def build_Mansion(cx, cz, FY, hname):
    global h
    h = hname

    H(h, part("Lot", (56, 0.2, 48), (cx, 0.1, cz), (150, 150, 148), CONCRETE))
    H(h, part("Floor", (36, 0.5, 24), (cx, FY - 0.25, cz), MARBLEC, MARBLE))
    # F2 with stairwell hole (right band x 10..18, z -7.2..1.8)
    H(h, part("Floor2Main", (28, 0.5, 24), (cx - 4, FY + 11.75, cz), MARBLEC,
              MARBLE))
    H(h, part("Floor2FrontStrip", (8, 0.5, 4.8), (cx + 14, FY + 11.75, cz - 9.6),
              MARBLEC, MARBLE))
    H(h, part("Floor2MidStrip", (8, 0.5, 5.45), (cx + 14, FY + 11.75, cz + 4.525),
              MARBLEC, MARBLE))
    H(h, part("Floor2BackStrip", (8, 0.5, 4.75), (cx + 14, FY + 11.75, cz + 9.625),
              MARBLEC, MARBLE))
    H(h, part("Roof", (38, 0.5, 26), (cx, FY + 22.2, cz), (222, 205, 180), SMOOTH))

    H(h, part("WallBack", (36, 22, 0.8), (cx, FY + 11, cz + 12), (225, 218, 200),
              SMOOTH))
    H(h, part("WallL", (0.8, 22, 24), (cx - 18, FY + 11, cz), (225, 218, 200),
              SMOOTH))
    H(h, part("WallR", (0.8, 22, 24), (cx + 18, FY + 11, cz), (225, 218, 200),
              SMOOTH))
    # front: wall segments around 3 doors, tall glass between
    H(h, part("WallFrontLOuter", (2.5, 22, 0.8), (cx - 16.75, FY + 11, cz - 12),
              (225, 218, 200), SMOOTH))
    H(h, part("WallFrontROuter", (2.5, 22, 0.8), (cx + 16.75, FY + 11, cz - 12),
              (225, 218, 200), SMOOTH))
    H(h, part("EntryGlassL", (4.5, 22, 0.4), (cx - 5.75, FY + 11, cz - 12),
              GLASSC, GLASS, transparency=0.42))
    H(h, part("EntryGlassR", (4.5, 22, 0.4), (cx + 5.75, FY + 11, cz - 12),
              GLASSC, GLASS, transparency=0.42))
    # grand columns
    for px in (cx - 15, cx - 7, cx + 7, cx + 15):
        for pz in (cz - 14.5,):
            H(h, part("Column", (1.8, 22, 1.8), (px, FY + 11, pz), (240, 235, 225),
                      MARBLE))
    H(h, part("Portico", (38, 1, 6), (cx, FY + 22.5, cz - 14.5), (222, 205, 180),
              SMOOTH))
    H(h, part("PorticoStep", (30, 0.4, 3), (cx, FY + 0.2, cz - 14.5), MARBLEC,
              MARBLE))
    H(h, part("BalconySlab", (16, 0.5, 5), (cx, FY + 11.5, cz - 14.5), MARBLEC,
              MARBLE))

    f_door(h, cx, FY, cz - 12, w=7, hgt=8, color=DARKWOOD)
    f_door(h, cx - 13, FY, cz - 12, w=5, hgt=7, color=GLASSC)
    f_door(h, cx + 13, FY, cz - 12, w=5, hgt=7, color=GLASSC)
    for wx in (-16, 16):
        f_window(h, cx + wx, FY + 5, cz - 12, w=4, hgt=6, t=0.42)
        f_window(h, cx + wx, FY + 17, cz - 12, w=4, hgt=6, t=0.42)
        f_window(h, cx + wx, FY + 5, cz + 12, w=4, hgt=6, t=0.42)
        f_window(h, cx + wx, FY + 17, cz + 12, w=4, hgt=6, t=0.42)

    # F1: grand ballroom (left) + formal dining (right)
    f_rug(h, cx - 9, FY, cz, 14, 16, CARPET_RED, border=GOLD)
    f_chandelier(h, cx - 9, FY + 21.4, cz, 2.0, tiers=3, bulbs_per=8)
    f_chandelier(h, cx + 9, FY + 21.4, cz, 1.6, tiers=2, bulbs_per=6)
    f_sofa(h, cx - 13.5, FY, cz - 2, SOFA_BEIGE, roty=90, w=7)
    f_sofa(h, cx - 4.5, FY, cz - 2, SOFA_BEIGE, roty=-90, w=7)
    f_coffee_table(h, cx - 9, FY, cz - 1, w=5)
    f_fireplace(h, cx - 9, FY, cz + 10.2, roty=0, w=6, chimney=True)
    f_painting(h, cx - 17.4, FY + 12, cz - 4, roty=90, w=5, hgt=3.5,
               color=(70, 50, 110))
    f_painting(h, cx - 17.4, FY + 12, cz + 4, roty=90, w=5, hgt=3.5,
               color=(110, 70, 40))
    f_plant(h, cx - 15.5, FY, cz + 8.5, big=True)
    f_plant(h, cx - 2.5, FY, cz + 8.5, big=True)
    f_dining(h, cx + 8, FY, cz + 4, seats=8, w=9)
    f_kitchen(h, cx + 9.4, FY, cz + 10.3, roty=0, run=10)
    f_bookshelf(h, cx + 16.4, FY, cz + 4, roty=-90, w=7, hgt=9)

    # F2: 3 suites (stairs at right, 11 steps land flush on F2 floor)
    f_stairs(h, cx + 14, FY, cz - 6.55, steps=11, rise=1.09, run_=0.76, w=4, dirz=1)
    f_railing(h, cx + 10, FY + 11.7, cz - 2.7, length=9, roty=90)
    f_bed(h, cx - 12, FY + 12, cz + 6.4, roty=180, size=1.15, headcolor=MAHOGANY)
    f_nightstand(h, cx - 15.5, FY + 12, cz + 5)
    f_nightstand(h, cx - 8.5, FY + 12, cz + 5)
    f_rug(h, cx - 12, FY + 12, cz + 4, 9, 8, CARPET_CREAM, border=GOLD)
    f_wardrobe(h, cx - 12, FY + 12, cz + 1.2, w=9)
    f_bathroom(h, cx + 2, FY + 12, cz - 8.2)
    f_bed(h, cx + 2, FY + 12, cz + 7.6, roty=180, size=1.0, headcolor=MAHOGANY)
    f_rug(h, cx + 2, FY + 12, cz + 4, 8, 7, CARPET_PURPLE)
    f_bookshelf(h, cx + 16.4, FY + 12, cz + 8, roty=-90, w=6, hgt=7)
    f_bed(h, cx - 6.5, FY + 12, cz - 4.5, roty=0, size=0.95, headcolor=DARKWOOD)
    f_chandelier(h, cx - 12, FY + 21.6, cz + 2, 1.3, tiers=2, bulbs_per=6)
    f_painting(h, cx, FY + 17, cz - 12.4, color=(90, 40, 90))

    # yard: fountain, hedges, gazebo
    f_fountain(h, cx, cz - 22)
    for hx, hz in ((-20, -16), (20, -16), (-20, 16), (20, 16)):
        H(h, part("Hedge", (6, 3, 2), (cx + hx, FY + 1.5, cz + hz), (50, 110, 60),
                  GRASS))
    f_fence(h, cx, cz - 23, 54, y=0.2,
            gap=[(-13, 9), (0, 10), (13, 9)])
    f_fence(h, cx - 12, cz + 23.8, 30, y=0.2)
    f_fence(h, cx + 12, cz + 23.8, 30, y=0.2)
    f_tree(h, cx - 22, cz + 18, s=1.1)
    f_tree(h, cx + 22, cz + 18, s=1.1)
    f_flowerbed(h, cx - 12, cz - 21, w=10, d=2.5)
    f_flowerbed(h, cx + 12, cz - 21, w=10, d=2.5)


# ================================================================ HOUSE I
# Penthouse — owner/developer flagship. Single unit, not for sale.
# 3 floors + rooftop, central glass elevator shaft (cab animated in Lua).
def build_Penthouse(cx, cz, FY, hname):
    global h
    h = hname

    H(h, part("Lot", (44, 0.2, 40), (cx, 0.1, cz), (40, 40, 44), CONCRETE))
    for fl in range(3):
        top = fl == 2
        # floor slabs (F2/F3 with elevator shaft hole at (cx, cz+8) 7.5x7.5)
        if fl == 0:
            H(h, part(f"Slab{fl}", (30, 0.5, 26), (cx, FY - 0.25, cz), MARBLEC,
                      MARBLE))
        else:
            zc = cz + 8
            H(h, part(f"Slab{fl}Front", (30, 0.5, 17.25), (cx, FY + fl * 12
                      - 0.25, cz - 4.375), MARBLEC, MARBLE))
            H(h, part(f"Slab{fl}Back", (30, 0.5, 1.25), (cx, FY + fl * 12
                      - 0.25, zc + 6.375), MARBLEC, MARBLE))
            H(h, part(f"Slab{fl}L", (11.25, 0.5, 7.5), (cx - 9.375, FY + fl
                      * 12 - 0.25, zc), MARBLEC, MARBLE))
            H(h, part(f"Slab{fl}R", (11.25, 0.5, 7.5), (cx + 9.375, FY + fl
                      * 12 - 0.25, zc), MARBLEC, MARBLE))
        # walls per floor: glass sides/back, gold-mullion front
        wy = FY + fl * 12 + 5.5
        H(h, part(f"WallBack{fl}", (30, 11, 0.5), (cx, wy, cz + 13), WHITE,
                  SMOOTH))
        H(h, part(f"GlassBack{fl}", (28, 10, 0.4), (cx, wy, cz + 12.6),
                  GLASSC, GLASS, transparency=0.4, cancollide=False))
        H(h, part(f"WallL{fl}", (0.5, 11, 26), (cx - 15, wy, cz), WHITE,
                  SMOOTH))
        H(h, part(f"GlassL{fl}", (0.4, 10, 24), (cx - 14.6, wy, cz), GLASSC,
                  GLASS, transparency=0.4, cancollide=False))
        H(h, part(f"WallR{fl}", (0.5, 11, 26), (cx + 15, wy, cz), WHITE,
                  SMOOTH))
        H(h, part(f"GlassR{fl}", (0.4, 10, 24), (cx + 14.6, wy, cz), GLASSC,
                  GLASS, transparency=0.4, cancollide=False))
        if not top:
            if fl == 0:  # entrance level: 10-wide opening for the gold door
                H(h, part(f"GlassFront{fl}L", (10, 11, 0.4), (cx - 10, wy,
                          cz - 13), GLASSC, GLASS, transparency=0.4))
                H(h, part(f"GlassFront{fl}R", (10, 11, 0.4), (cx + 10, wy,
                          cz - 13), GLASSC, GLASS, transparency=0.4))
                H(h, part(f"GlassFront{fl}Top", (10, 3, 0.4), (cx,
                          FY + 9.5, cz - 13), GLASSC, GLASS,
                          transparency=0.4))
            else:
                H(h, part(f"GlassFront{fl}", (30, 11, 0.4), (cx, wy,
                          cz - 13), GLASSC, GLASS, transparency=0.4))
            H(h, part(f"GoldBeam{fl}", (30, 0.4, 0.4), (cx, FY + fl * 12
                      + 10.8, cz - 12.8), GOLD, FOIL, cancollide=False))
        else:
            # rooftop parapet
            H(h, part(f"ParapetF{fl}", (30, 2.5, 0.5), (cx, FY + 24.5
                      + 1.25, cz - 13), WHITE, SMOOTH))
            H(h, part(f"ParapetB{fl}", (30, 2.5, 0.5), (cx, FY + 24.5
                      + 1.25, cz + 13), WHITE, SMOOTH))
            H(h, part(f"ParapetL{fl}", (0.5, 2.5, 26), (cx - 15, FY + 24.5
                      + 1.25, cz), WHITE, SMOOTH))
            H(h, part(f"ParapetR{fl}", (0.5, 2.5, 26), (cx + 15, FY + 24.5
                      + 1.25, cz), WHITE, SMOOTH))
            H(h, part(f"RoofTrim{fl}", (31, 0.6, 27), (cx, FY + 24.5
                      + 0.1, cz), GOLD, FOIL, cancollide=False))
    H(h, part("RoofSlab", (31, 0.5, 27), (cx, FY + 24.25, cz), MARBLEC, MARBLE))

    # elevator shaft: corner columns + glass, front openings each floor
    sx, sz = cx, cz + 8
    for px in (-3.5, 3.5):
        for pz in (-3.5, 3.5):
            H(h, part("ShaftColumn", (0.8, 36, 0.8), (sx + px, FY + 18,
                      sz + pz), WHITE, SMOOTH))
    for fl in range(3):
        wy = FY + fl * 12 + 5.5
        H(h, part(f"ShaftBack{fl}", (7.4, 11, 0.4), (sx, wy, sz + 3.5),
                  GLASSC, GLASS, transparency=0.55))
        H(h, part(f"ShaftL{fl}", (0.4, 11, 7.4), (sx - 3.5, wy, sz), GLASSC,
                  GLASS, transparency=0.55))
        H(h, part(f"ShaftR{fl}", (0.4, 11, 7.4), (sx + 3.5, wy, sz), GLASSC,
                  GLASS, transparency=0.55))
        H(h, part(f"ShaftJamL{fl}", (1.7, 11, 0.4), (sx - 2.85, wy, sz - 3.5),
                  GLASSC, GLASS, transparency=0.55))
        H(h, part(f"ShaftJamR{fl}", (1.7, 11, 0.4), (sx + 2.85, wy, sz - 3.5),
                  GLASSC, GLASS, transparency=0.55))
        # guard rails around shaft hole on upper slabs
        if fl > 0:
            ry = FY + fl * 12 + 0.2
            # front edge split — center gap for the elevator cab opening
            f_railing(h, sx - 2.9, ry, sz - 3.9, length=2.2, roty=0,
                      color=GOLD)
            f_railing(h, sx + 2.9, ry, sz - 3.9, length=2.2, roty=0,
                      color=GOLD)
            f_railing(h, sx, ry, sz + 3.9, length=8, roty=0, color=GOLD)
            f_railing(h, sx - 3.9, ry, sz, length=8, roty=90, color=GOLD)
            f_railing(h, sx + 3.9, ry, sz, length=8, roty=90, color=GOLD)
    # elevator cab (animated by HouseLogic): base + 3 low glass shields
    H(h, part("ElevatorBase", (7, 0.5, 7), (sx, FY + 0.25, sz), (60, 60, 66),
              METAL))
    for dx, dz, ex, ez in ((0, 3.3, 6.6, 0.2), (-3.3, 0, 0.2, 6.6),
                           (3.3, 0, 0.2, 6.6)):
        H(h, part("ElevatorShield", (ex, 3.4, ez), (sx + dx, FY + 2.2,
                  sz + dz), GLASSC, GLASS, transparency=0.3,
                  cancollide=False))

    # ---- F1: grand lobby ----
    H(h, part("Carpet", (6, 0.15, 20), (cx, FY + 0.07, cz - 3), CARPET_RED,
              FABRIC, cancollide=False))
    for px in (-8, 8):
        for pz in (-4, 4):
            H(h, part("LobbyColumn", (1.3, 11, 1.3), (cx + px, FY + 5.5,
                      cz + pz), (240, 235, 225), MARBLE))
            H(h, part("ColumnTrim", (1.7, 0.5, 1.7), (cx + px, FY + 10.8,
                      cz + pz), GOLD, FOIL))
    f_chandelier(h, cx - 7, FY + 11.4, cz - 2, 1.5, tiers=2, bulbs_per=6)
    f_chandelier(h, cx + 7, FY + 11.4, cz - 2, 1.5, tiers=2, bulbs_per=6)
    f_sofa(h, cx - 8, FY, cz - 8, (120, 90, 60), w=5)
    f_sofa(h, cx + 8, FY, cz - 8, (120, 90, 60), w=5, roty=180)
    f_coffee_table(h, cx, FY, cz - 8, w=4)
    f_plant(h, cx - 12.5, FY, cz - 11, big=True)
    f_plant(h, cx + 12.5, FY, cz - 11, big=True)
    f_door(h, cx, FY, cz - 13, w=6, hgt=8, color=GOLD)
    H(h, part("GoldEntrance", (8, 0.5, 0.5), (cx, FY + 8.4, cz - 12.8), GOLD,
              FOIL, cancollide=False))

    # ---- F2: sky suite ----
    f_bed(h, cx - 9, FY + 12, cz + 9, roty=180, size=1.1, headcolor=MAHOGANY)
    f_nightstand(h, cx - 12.3, FY + 12, cz + 8.5)
    f_nightstand(h, cx - 5.7, FY + 12, cz + 8.5)
    f_rug(h, cx - 9, FY + 12, cz + 5, 9, 7, CARPET_PURPLE, border=GOLD)
    f_wardrobe(h, cx - 10.5, FY + 12, cz + 1, w=8)
    f_bathroom(h, cx + 9.5, FY + 12, cz + 8)
    f_sofa(h, cx + 6, FY + 12, cz + 1, SOFA_BEIGE, roty=180, w=6)
    f_coffee_table(h, cx + 6, FY + 12, cz - 0.5, w=3.5)
    f_chandelier(h, cx, FY + 23.4, cz - 4, 1.4, tiers=2, bulbs_per=6)
    f_painting(h, cx - 14.6, FY + 17, cz, roty=90, w=5, hgt=3.5,
               color=(90, 40, 90))

    # ---- F3: rooftop lounge (open sky) — kept clear of the shaft hole ----
    H(h, part("PoolDeck", (14, 0.4, 9), (cx - 8, FY + 24.4, cz - 6), MARBLEC,
              MARBLE))
    H(h, part("PoolBasin", (11, 1.2, 6), (cx - 8, FY + 24.6, cz - 6),
              (200, 205, 210), PLASTIC))
    H(h, part("PoolWater", (10.4, 1, 5.4), (cx - 8, FY + 24.75, cz - 6),
              POOL_WATER, GLASS, transparency=0.3))
    H(h, part("Helipad", (0.3, 12, 12), (cx + 9, FY + 24.6, cz - 5.5), (70,
              70, 74), CONCRETE, shape=CYL, rotz=90))
    for hd, hl in ((0, 5), (-1.3, 2.5), (1.3, 2.5)):
        H(h, part("HelipadH", (hl if hl < 4 else 1, 0.15,
                  1 if hl < 4 else 5), (cx + 9 + hd, FY + 24.85, cz - 5.5),
                  WHITE, SMOOTH, cancollide=False))
    H(h, part("BarCounter", (9, 3, 1.5), (cx + 9.5, FY + 25.5, cz - 10),
              DARKWOOD, WOOD))
    H(h, part("BarTop", (9.6, 0.3, 2), (cx + 9.5, FY + 27.1, cz - 10), GOLD,
              FOIL))
    for bx in (-3, 0, 3):
        H(h, part("BarStool", (0.9, 2.4, 0.9), (cx + 9.5 + bx, FY + 26.2,
                  cz - 8.2), (110, 52, 38), PLASTIC, shape=CYL, rotz=90))
    f_sofa(h, cx - 1, FY + 24.5, cz + 1, (150, 120, 60), w=6)
    f_coffee_table(h, cx - 1, FY + 24.5, cz - 1.2, w=3.5, mat=FOIL,
                   color=GOLD)
    H(h, part("FireRing", (3.4, 0.6, 3.4), (cx + 2, FY + 24.9, cz - 10.5),
              (70, 70, 74), SLATE, shape=CYL, rotz=90))
    H(h, part("Fire", (1.6, 1, 1.6), (cx + 2, FY + 25.6, cz - 10.5), FLAME,
              NEON, shape=BALL, cancollide=False))

    # owner sign (physical, like sale signs but static)
    H(h, part("OwnerSignPost", (0.6, 5, 0.6), (cx + 12, FY + 2.5, cz - 15),
              (60, 42, 30), WOOD))
    H(h, part("OwnerSign", (6, 3, 0.4), (cx + 12, FY + 6, cz - 15), (30, 22,
              16), WOOD))
    H(h, part("OwnerSignPlate", (5.6, 2.6, 0.15), (cx + 12, FY + 6, cz
              - 15.25), GOLD, FOIL, cancollide=False))



# ================================================================ CITY BLOCK
# East of plaza: car shop, cafe, grocery, hospital, police HQ, pizza place.


def _city_shell(h, x, z, w, d, color, name, sign_text, fy):
    """Generic shop shell: floor, walls w/ storefront, roof, lit sign."""
    H(h, part(f"{name}Lot", (w + 10, 0.2, d + 10), (x, 0.1, z), (150, 150,
              148), CONCRETE))
    H(h, part(f"{name}Floor", (w, 0.5, d), (x, fy - 0.25, z), MARBLEC,
              MARBLE))
    H(h, part(f"{name}WallBack", (w, 10, 0.5), (x, fy + 5, z + d / 2), color,
              SMOOTH))
    H(h, part(f"{name}WallL", (0.5, 10, d), (x - w / 2, fy + 5, z), color,
              SMOOTH))
    H(h, part(f"{name}WallR", (0.5, 10, d), (x + w / 2, fy + 5, z), color,
              SMOOTH))
    gw = (w - 14) / 2
    H(h, part(f"{name}StoreL", (gw, 9, 0.4), (x - 7 - gw / 2, fy + 4.5,
              z - d / 2), GLASSC, GLASS, transparency=0.35))
    H(h, part(f"{name}StoreR", (gw, 9, 0.4), (x + 7 + gw / 2, fy + 4.5,
              z - d / 2), GLASSC, GLASS, transparency=0.4))
    H(h, part(f"{name}Header", (w, 1, 0.5), (x, fy + 9.5, z - d / 2), color,
              SMOOTH))
    H(h, part(f"{name}Roof", (w + 1, 0.6, d + 1), (x, fy + 10.2, z), (120,
              120, 126), SMOOTH))
    H(h, part(f"{name}SignBoard", (w - 6, 2.2, 0.3), (x, fy + 8.1,
              z - d / 2 - 0.3), (30, 30, 34), SMOOTH))
    for i, ch in enumerate(sign_text):
        H(h, part(f"{name}SignC{i}", (0.8, 1.2, 0.2),
                  (x - (len(sign_text) - 1) * 0.45 + i * 0.9, fy + 8.1,
                   z - d / 2 - 0.5), GOLD, NEON, cancollide=False))
    f_door(h, x, fy, z - d / 2, w=6, hgt=7, color=DARKWOOD)


def f_streetlight(h, x, z):
    H(h, part("StreetLightPole", (0.4, 16, 0.4), (x, 8, z), (40, 40, 44),
              METAL))
    H(h, part("StreetLightArm", (0.4, 0.4, 3), (x, 15.8, z - 1.5), (40, 40,
              44), METAL, cancollide=False))
    H(h, part("StreetLightHead", (1, 0.5, 1.6), (x, 15.4, z - 2.8), (40, 40,
              44), METAL, cancollide=False))
    H(h, part("StreetLightBulb", (0.8, 0.3, 1.2), (x, 15.05, z - 2.8),
              (255, 235, 170), NEON, cancollide=False))


def f_busstop(h, x, z, roty=0):
    ca, sa = math.cos(math.radians(roty)), math.sin(math.radians(roty))

    def r(dx, dz):
        return (x + dx * ca, z + dx * sa)
    px, pz = r(-2.5, 0)
    H(h, part("BusStopPole", (0.35, 9, 0.35), (px, 4.5, pz), (40, 40, 44),
              METAL))
    H(h, part("BusStopSign", (2.6, 3, 0.3), (px, 7.6, pz), (40, 90, 200),
              PLASTIC, roty=roty))
    H(h, part("BusStopMark", (1.4, 0.5, 0.35), (px, 8.2, pz), (240, 240,
              240), PLASTIC, roty=roty, cancollide=False))
    bx, bz = r(1.5, 0)
    H(h, part("BusStopBench", (4, 0.4, 1.6), (bx, 1.6, bz), (110, 52, 38),
              WOOD, roty=roty))
    for lx in (-1.7, 1.7):
        H(h, part("BusStopLeg", (0.3, 1.4, 1.4), (bx + lx, 0.7, bz), (40,
                  40, 44), METAL, cancollide=False))


def f_npc(h, x, z, roty, shirt, pants, skin):
    H(h, part("NPCLeg", (1.2, 2.6, 1.2), (x - 0.65, 1.3, z), pants, FABRIC))
    H(h, part("NPCLeg", (1.2, 2.6, 1.2), (x + 0.65, 1.3, z), pants, FABRIC))
    H(h, part("NPCTorso", (2.8, 2.8, 1.4), (x, 4, z), shirt, FABRIC))
    H(h, part("NPCHead", (2, 2, 2), (x, 6.4, z), skin, PLASTIC))
    H(h, part("NPCFace", (1.2, 0.5, 0.2), (x, 6.6, z - 1.05), (30, 30, 30),
              SMOOTH, cancollide=False))
    H(h, part("NPCArm", (1.1, 2.6, 1.1), (x + 2.1, 4, z), shirt, FABRIC))
    H(h, part("NPCArm", (1.1, 2.6, 1.1), (x - 2.1, 4, z), shirt, FABRIC))


def build_city():
    global h
    h = "CityBlock"
    fy = 0.5
    _city_shell(h, 60, -18, 30, 20, (250, 210, 120), "CarShop", "TOKO MOBIL", fy)
    for px in (-6, 6):
        H(h, part(f"ShopPad{px}", (9, 0.3, 15), (60 + px, fy + 0.15, -18),
                  (70, 70, 74), SMOOTH))
        f_carport_car(h, 60 + px, fy, -18,
                      color=(200, 60, 60) if px < 0 else (60, 90, 200))
    H(h, part("ShopCounter", (10, 3, 1.5), (60, fy + 1.5, -22), DARKWOOD,
              WOOD))
    H(h, part("ShopCounterTop", (10.6, 0.3, 2), (60, fy + 3.1, -22), GOLD,
              FOIL))

    _city_shell(h, 105, -18, 24, 18, (150, 100, 70), "Cafe", "KAFE KOTA", fy)
    H(h, part("CafeCounter", (8, 3, 1.5), (105, fy + 1.5, -20), DARKWOOD,
              WOOD))
    H(h, part("CafeTop", (8.6, 0.3, 2), (105, fy + 3.1, -20), (150, 100, 70),
              WOOD))
    for px in (-2.5, 0, 2.5):
        H(h, part("CafeStool", (0.9, 2.4, 0.9), (105 + px, fy + 1.2, -17.5),
                  (110, 52, 38), PLASTIC, shape=CYL, rotz=90))
    for px in (-6, 0, 6):
        f_sofa(h, 105 + px, fy, 2, (120, 90, 60), w=4)
        f_coffee_table(h, 105 + px, fy, 0, w=2.6, mat=WOOD, color=WOODC,
                       leg=BRONZE)

    _city_shell(h, 148, -18, 24, 18, (90, 140, 90), "Grocery",
                "TOKO KELONTONG", fy)
    for px in (-7, -3.5, 0, 3.5, 7):
        H(h, part("GroceryShelf", (3, 5, 1.5), (148 + px, fy + 2.5, -20),
                  (70, 70, 76), PLASTIC))
        for r in range(3):
            H(h, part("GroceryItem", (2.4, 0.7, 1.2), (148 + px,
                      fy + 1.6 + r * 1.4, -20.4), BOOK_COLORS[r % 8],
                      PLASTIC, cancollide=False))
    H(h, part("GroceryCounter", (6, 3, 1.5), (148, fy + 1.5, -16), DARKWOOD,
              WOOD))

    _city_shell(h, 60, 24, 28, 20, (240, 240, 245), "Hospital", "RUMAH SAKIT", fy)
    H(h, part("HospCrossV", (1.2, 4.5, 0.3), (60, fy + 8.4, 14.2),
              (220, 40, 40), NEON, cancollide=False))
    H(h, part("HospCrossH", (4.5, 1.2, 0.3), (60, fy + 8.4, 14.2),
              (220, 40, 40), NEON, cancollide=False))
    for px in (-6, 6):
        H(h, part("HospBed", (3, 1.2, 6.5), (60 + px, fy + 0.6, 24),
                  (240, 240, 250), PLASTIC))
        H(h, part("HospBedHead", (3, 2.2, 0.4), (60 + px, fy + 1.7, 27),
                  (200, 200, 210), PLASTIC, cancollide=False))
    H(h, part("HospDesk", (8, 3, 1.5), (60, fy + 1.5, 18), MARBLEC, MARBLE))

    _city_shell(h, 105, 24, 26, 20, (70, 80, 150), "PoliceHQ",
                "KANTOR POLISI", fy)
    H(h, part("HQGaragePad", (12, 0.3, 16), (105, fy + 0.15, 24), (70, 70,
              74), SMOOTH))
    H(h, part("HQDesk", (8, 3, 1.5), (105, fy + 1.5, 18), (40, 40, 46),
              METAL))
    for px in (-5, 5):
        H(h, part("HQLocker", (2.5, 7, 1.5), (105 + px, fy + 3.5, 26),
                  (50, 60, 90), METAL))

    _city_shell(h, 148, 24, 24, 18, (180, 80, 50), "PizzaPlace", "PIZZA KOTA", fy)
    H(h, part("PizzaOven", (4, 4.5, 3), (140, fy + 2.25, 26), (80, 40, 36),
              BRICK))
    H(h, part("PizzaOvenFire", (2.6, 1, 0.4), (140, fy + 2, 24.4), FLAME,
              NEON, cancollide=False))
    H(h, part("PizzaCounter", (8, 3, 1.5), (148, fy + 1.5, 18), DARKWOOD,
              WOOD))
    for px in (-2, 0, 2):
        H(h, part("PizzaBox", (1.8, 0.5, 1.8), (148 + px, fy + 3.4, 18),
                  (200, 170, 110), PLASTIC, cancollide=False))

    # ---- south row: gas station, bank, workshop, hotel ----
    # gas station: canopy + 2 pumps + shop
    _city_shell(h, 60, -60, 22, 16, (230, 60, 50), "GasStation", "POM BENSIN", fy)
    H(h, part("GasCanopy", (26, 0.8, 14), (60, fy + 7.5, -71), (230, 60, 50),
              SMOOTH))
    for px in (-10, 10):
        for pz in (-77, -65):
            H(h, part("GasCanopyPost", (0.8, 7, 0.8), (60 + px, fy + 3.5,
                      pz), (120, 120, 126), METAL))
    for px in (-4, 4):
        H(h, part("GasPump", (1.6, 4.5, 2.2), (60 + px, fy + 2.25, -71),
                  (220, 60, 50), SMOOTH))
        H(h, part("GasPumpScreen", (1, 1.4, 0.2), (60 + px, fy + 3.2,
                  -72.2), (40, 200, 90), NEON, cancollide=False))
    H(h, part("GasPad", (18, 0.3, 12), (60, fy + 0.15, -71), (70, 70, 74),
              SMOOTH))

    _city_shell(h, 105, -60, 22, 16, (190, 160, 90), "Bank", "BANK KOTA", fy)
    H(h, part("BankATM", (2, 4.5, 1), (98, fy + 2.25, -66), (40, 90, 200),
              SMOOTH))
    H(h, part("BankATMScreen", (1.4, 1, 0.2), (98, fy + 3, -66.7), (60, 200,
              120), NEON, cancollide=False))
    H(h, part("BankVault", (6, 7, 4), (105, fy + 3.5, -62), (90, 90, 96),
              METAL))
    H(h, part("BankVaultDoor", (0.5, 5.5, 5.5), (105, fy + 2.75, -59.8),
              GOLD, FOIL))

    _city_shell(h, 148, -60, 22, 16, (160, 120, 60), "Workshop", "BENGKEL", fy)
    H(h, part("WorkshopPad", (12, 0.3, 10), (148, fy + 0.15, -64), (70, 70,
              74), SMOOTH))
    H(h, part("WorkshopTool", (4, 3, 1.5), (142, fy + 1.5, -62), (60, 60,
              66), METAL))
    H(h, part("WorkshopLift", (8, 0.6, 8), (152, fy + 2, -62), (160, 160,
              166), METAL))
    for px in (-3, 3):
        H(h, part("WorkshopLiftLeg", (0.8, 2, 0.8), (152 + px, fy + 1,
                  -62), (90, 90, 96), METAL))

    _city_shell(h, 195, -60, 24, 18, (120, 90, 160), "Hotel", "HOTEL KOTA", fy)
    for fl in (1, 2):
        H(h, part(f"HotelWall2F{fl}", (24, 10, 0.5), (195, fy + fl * 10
                  - 5, -68.75), (120, 90, 160), SMOOTH))
        H(h, part(f"HotelGlass2F{fl}", (22, 9, 0.4), (195, fy + fl * 10
                  - 5, -68.55), GLASSC, GLASS, transparency=0.4,
                  cancollide=False))
    H(h, part("HotelRoof", (25, 0.6, 19), (195, fy + 20.3, -60), (90, 65,
              120), SMOOTH))
    H(h, part("HotelDesk", (8, 3, 1.5), (195, fy + 1.5, -66), DARKWOOD,
              WOOD))
    for px in (-6, 6):
        H(h, part("HotelSofa", (4, 1.8, 2.2), (195 + px, fy + 0.9, -62),
                  (120, 90, 160), FABRIC))

    # road connector: main street -> south row (z -75)
    for i in range(12):
        H(h, part(f"SouthRoad{i}", (9, 0.2, 9), (60, 0.1, 20 - i * 9),
                  PATHC, COBBLE))
    H(h, part("SouthRoadEW", (180, 0.2, 9), (105, 0.1, -75), PATHC, COBBLE))
    f_streetlight(h, 45, -70)
    f_streetlight(h, 130, -70)
    f_streetlight(h, 180, -70)

    # NPCs for the south row
    f_npc(h, 53, -73.5, 0, (230, 60, 50), (60, 60, 70), (255, 204, 170))
    f_npc(h, 100, -73.5, 0, (190, 160, 90), (50, 50, 60), (255, 204, 170))
    f_npc(h, 143, -73.5, 0, (160, 120, 60), (60, 60, 66), (255, 204, 170))
    f_npc(h, 190, -73.5, 0, (120, 90, 160), (70, 70, 80), (255, 204, 170))


build_city()

for i in range(6):
    f_streetlight("Shared", -84, 80 + i * 130)
for i in range(4):
    f_streetlight("Shared", -80 - i * 60, 33)
for i in range(3):
    f_streetlight("Shared", 30 + i * 60, 33)

f_busstop("Shared", 24, 12, 180)
f_busstop("Shared", -70, 40, 90)
f_busstop("Shared", 190, 88, 0)
f_busstop("Shared", 246, 200, 0)
f_busstop("Shared", 338, 312, 0)

f_npc("Shared", 100, -15.5, 180, (150, 100, 70), (60, 60, 70),
      (255, 204, 170))
f_npc("Shared", 143, -15.5, 180, (90, 140, 90), (50, 50, 60),
      (255, 204, 170))
f_npc("Shared", 55, 20.5, 0, (240, 240, 250), (180, 220, 230),
      (255, 204, 170))
f_npc("Shared", 100, 20.5, 0, (40, 50, 100), (40, 50, 100), (255, 204, 170))
f_npc("Shared", 143, 20.5, 0, (180, 80, 50), (60, 60, 60), (255, 204, 170))
f_npc("Shared", 10, 8, 180, (200, 60, 60), (80, 80, 90), (255, 204, 170))
f_npc("Shared", -10, 8, 0, (60, 110, 200), (70, 70, 80), (255, 204, 170))


# ================================================================ complexes
# 8 complexes x 5 units = 40 houses. Each complex = row of 5 same-type lots
# along +X, unit pitch >= lot size so lots never overlap; rows stack along +Z.
# single-unit owner house (excluded from complexes & PRICES)
assert os.environ.get("WITH_PENTHOUSE", "1") == "1"

# HILLS=1 (default): north complexes (Castle, Mansion rows) sit on a stepped
# hill; HILLS=0: flat world. Revert anytime:  HILLS=0 python generate_houses.py
HILLS = os.environ.get("HILLS", "1") == "1"

BUILDERS = [
    ("TinyHouse", build_TinyHouse, 0.5, 26),
    ("ZenHouse", build_ZenHouse, 2.5, 40),
    ("AFrame", build_AFrame, 0.5, 32),
    ("ModernCube", build_ModernCube, 0.5, 44),
    ("Dome", build_Dome, 0.5, 36),
    ("VillaL", build_VillaL, 0.5, 46),
    ("Castle", build_Castle, 0.5, 56),
    ("Mansion", build_Mansion, 0.5, 62),
]
UNITS = 5

# owner/developer flagship: one unit, south of plaza facing spawn
build_Penthouse(-140, 95, 0.5, "Penthouse")

complex_names = []              # folder names, e.g. "Castle#3"
hill_lift = {}                  # row index -> (dx, dz, lift)
for base, fn, fy, pitch in BUILDERS:
    ri = [b[0] for b in BUILDERS].index(base)
    row_z = 60 + 56 * ri
    if HILLS and ri >= 6:  # Castle (6), Mansion (7): hill terraces
        hill_lift[ri] = (ri - 5) * 14
    for u in range(UNITS):
        lift = hill_lift.get(ri, 0)
        fn(-60 + u * pitch, row_z, fy + lift, f"{base}#{u + 1}")
        complex_names.append(f"{base}#{u + 1}")

# hill under the north complexes: two terraces + access ramps (HILLS only)
if HILLS:
    for terr, (z0, lift) in enumerate(((396, 14), (452, 28))):
        H("Shared", part(f"HillPlateau{terr}", (220, lift, 64),
                         (0, lift / 2 - 0.5, z0), (98, 148, 78), GRASS))
        H("Shared", part(f"HillSlope{terr}", (220, 1, 30), (0,
                          lift / 2 - 1, z0 - 46), (98, 148, 78), GRASS,
                          rotx=24))
    # ramp roads up the front slopes
    H("Shared", part("HillRoadRamp", (16, 0.4, 82), (-6, 7.2, 350), PATHC,
                     COBBLE, rotx=15))
    H("Shared", part("HillRoadRamp2", (16, 0.4, 82), (-6, 21.2, 406), PATHC,
                     COBBLE, rotx=15))
    H("Shared", part("HillRoadTop", (160, 0.4, 10), (0, 49.1, 490), PATHC,
                     COBBLE))

# roads: N-S spine west of all complexes + east-west lane to each row front
ROAD = (PATHC, COBBLE)
ROW_ZS = [60 + 56 * i for i in range(8)]
# spine x=-94 (west of every lot), z from -150 up past Mansion row
for i in range(52):
    H("Shared", part(f"RoadNS{i}", (9, 0.2, 9), (-94, 0.09, 20 + i * 9),
                     *ROAD))
# traffic signs along the road network
# stop: plaza exits & complex entries; yield: lane merges; noentry: hill
# one-ways; parking: near carports; speed: long straights; crossing: plaza
# working traffic lights at the main intersection (alternate phases)
f_trafficlight("Shared", -88, 32, 1, roty=180, y=0.3)
f_trafficlight("Shared", -101, 56, 2, roty=0, y=0.3)

SIGNS = [
    (-91, 34, "stop", 0), (-97, 16, "crossing", 0), (-88, 60, "speed", 0),
    (-88, 116, "speed", 0), (-100, 30, "noentry", 90),
    (-82, 148, "yield", 0), (-82, 204, "parking", 0),
    (-88, 260, "speed", 0), (-82, 316, "yield", 0),
    (-88, 372, "stop", 0), (-82, 428, "parking", 0),
    (-20, 43, "crossing", 180), (40, 43, "speed", 180),
    (110, 43, "crossing", 180),
    (33, 47, "stop", 180), (89, 47, "stop", 180),
    (18, 38, "parking", 0), (74, 38, "parking", 0),
    (61, -30, "noentry", 180), (61, 500, "noentry", 0),
]
for sx_, sz_, kind_, rot_ in SIGNS:
    f_roadsign("Shared", sx_, sz_, kind_, roty=rot_, y=0.3)

# one long lane in front of each complex (row_z - 28: clear of lots/fences,
# touching the spine at its west end)
for rz in ROW_ZS:
    bi = ROW_ZS.index(rz)
    xe = -60 + 4 * BUILDERS[bi][3] + BUILDERS[bi][3] / 2 + 6
    length = xe - (-90)
    H("Shared", part(f"RoadLane{BUILDERS[bi][0]}", (length, 0.2, 8),
                     ((xe + -90) / 2, 0.11, rz - 28), *ROAD))

order = ["Shared", "Penthouse"] + complex_names
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
assert n_houses == 41, n_houses
lines_gen = sum(1 for _ in open(__file__, encoding="utf-8"))
print(f"OK {out}: {os.path.getsize(out)} bytes, {n_items} items, "
      f"{n_doors} doors, {n_houses} houses, generator {lines_gen} lines")
