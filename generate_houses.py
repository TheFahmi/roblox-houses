#!/usr/bin/env python3
"""Generate houses.rbxlx — Luxury Houses showcase: 5 unique homes, rich interiors. Pure stdlib."""

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


def part(name, size, pos, color, mat=256, transparency=0.0, cancollide=True,
         shape=None, rotx=0.0, roty=0.0, rotz=0.0, values=None):
    x, y, z = pos
    sx, sy, sz = size
    # single-axis rotation matrix (ponytail: no multi-axis compose; enough for roofs/domes)
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
    shape_tok = f'<token name="Shape">{shape}</token>' if shape is not None else ""
    children = "".join(
        f'<Item class="StringValue" referent="{ref()}"><Properties>'
        f'<string name="Name">{esc(k)}</string>'
        f'<string name="Value">{esc(v)}</string></Properties></Item>'
        for k, v in (values or {}).items()
    )
    return (f'<Item class="Part" referent="{ref()}"><Properties>'
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
            f'</Properties>{children}</Item>')


# materials
PLASTIC, SMOOTH, NEON = 256, 272, 288
WOOD, PLANKS, MARBLE, SLATE = 512, 528, 784, 800
CONCRETE, GRANITE, BRICK, COBBLE = 816, 832, 848, 880
FABRIC, FOIL, GLASS, GRASS = 1312, 1072, 1568, 1280

WHITE = (237, 237, 237)
GLASSC = (200, 225, 240)
WOODC = (133, 94, 66)
DARKWOOD = (87, 60, 42)
STONE = (130, 130, 134)
GOLD = (212, 175, 55)
CARPET = (150, 30, 35)
MARBLEC = (235, 235, 240)
SOFA = (90, 95, 105)
PATHC = (180, 178, 170)
POOL = (60, 160, 220)
WARM = (255, 220, 160)
PLANT = (60, 140, 70)
POT = (140, 90, 60)

houses = {}  # name -> [xml]


def H(house, xml):
    houses.setdefault(house, []).append(xml)


# ---------- shared ground / street ----------
H("Shared", part("Ground", (400, 1, 400), (0, -0.5, 60), (106, 160, 80), GRASS))

for i in range(10):  # main street along X at z=10
    H("Shared", part(f"Path{i}", (8, 0.2, 6), (-36 + i * 8, 0.1, 10), PATHC, COBBLE))
for i in range(6):  # connector path z=10..45
    H("Shared", part(f"PathB{i}", (8, 0.2, 6), (-30 + i * 8, 0.1, 32), PATHC, COBBLE))
for i in range(6):  # back row path z=70..90
    H("Shared", part(f"PathC{i}", (8, 0.2, 6), (-26 + i * 8, 0.1, 76), PATHC, COBBLE))

for lx in (-24, 0, 24):  # street lamps
    H("Shared", part(f"LampPole{lx}", (0.4, 7, 0.4), (lx, 3.5, 16), (40, 40, 44), METAL := 1088))
    H("Shared", part(f"LampBulb{lx}", (1.2, 1.2, 1.2), (lx, 7.2, 16), WARM, NEON, shape=0, cancollide=False))

spawn = (
    f'<Item class="SpawnLocation" referent="{ref()}"><Properties>'
    f'<string name="Name">Spawn</string><bool name="Anchored">true</bool>'
    f'<bool name="Neutral">true</bool><float name="Duration">0</float>'
    f'<token name="Material">{MARBLE}</token>'
    f'<Color3uint8 name="Color3uint8">{pack(*MARBLEC)}</Color3uint8>'
    f'<Vector3 name="size"><X>10</X><Y>1</Y><Z>10</Z></Vector3>'
    f'<CoordinateFrame name="CFrame"><X>0</X><Y>0.5</Y><Z>-8</Z>'
    f'<R00>1</R00><R01>0</R01><R02>0</R02><R10>0</R10><R11>1</R11><R12>0</R12>'
    f'<R20>0</R20><R21>0</R21><R22>1</R22></CoordinateFrame>'
    f'<token name="TopSurface">0</token><token name="BottomSurface">0</token>'
    f'</Properties></Item>')
H("Shared", spawn)


# ---------- furniture helpers ----------
def sofa(h, x, y, z, color=SOFA, roty=0):
    H(h, part("SofaBase", (6, 1, 2.2), (x, y + 0.5, z), color, FABRIC, roty=roty))
    H(h, part("SofaBack", (6, 2, 0.5), (x, y + 2, z + 1.0 * (1 if roty == 0 else -1)), color, FABRIC, roty=roty))
    H(h, part("SofaArmL", (0.5, 1.6, 2.2), (x - 2.75, y + 0.8, z), color, FABRIC, roty=roty))
    H(h, part("SofaArmR", (0.5, 1.6, 2.2), (x + 2.75, y + 0.8, z), color, FABRIC, roty=roty))


def table(h, x, y, z, w=4, mat=GLASS, color=GLASSC, transparency=0.4):
    H(h, part("Table", (w, 0.3, 2.2), (x, y + 1, z), color, mat, transparency=transparency))
    for dx in (-w / 2 + 0.3, w / 2 - 0.3):
        H(h, part("TableLeg", (0.3, 1, 0.3), (x + dx, y + 0.5, z), GOLD, FOIL))


def chandelier(h, x, y, z, scale=1.0):
    H(h, part("ChanRod", (0.2 * scale, 1.5 * scale, 0.2 * scale), (x, y + 0.75 * scale, z), GOLD, FOIL, cancollide=False))
    for i, (dx, dz) in enumerate(((-0.8, 0), (0.8, 0), (0, 0))):
        H(h, part(f"ChanBulb{i}", (0.7 * scale, 0.7 * scale, 0.7 * scale),
                  (x + dx * scale, y - 0.4 * scale, z + dz * scale), WARM, NEON,
                  shape=0, cancollide=False))


def rug(h, x, y, z, w=8, d=6, color=CARPET):
    H(h, part("Rug", (w, 0.08, d), (x, y + 0.04, z), color, FABRIC, cancollide=False))


def tv(h, x, y, z, roty=0):
    H(h, part("TV", (5, 3, 0.3), (x, y + 3.5, z), (20, 20, 24), SMOOTH, roty=roty, cancollide=False))
    H(h, part("TVPanel", (5.4, 3.4, 0.1), (x, y + 3.5, z - 0.2 * (1 if roty == 0 else -1)),
              (10, 60, 90), NEON, roty=roty, cancollide=False))


def bed(h, x, y, z, roty=0, round_=False):
    if round_:
        H(h, part("BedBase", (0.8, 5, 5), (x, y + 0.4, z), MARBLEC, FABRIC, shape=2, rotz=90))
        H(h, part("BedPillow", (0.5, 2.4, 1.6), (x, y + 1.1, z), (250, 250, 250), FABRIC, shape=2, rotz=90, cancollide=False))
    else:
        H(h, part("BedBase", (4.5, 0.9, 6.5), (x, y + 0.45, z), MARBLEC, FABRIC, roty=roty))
        H(h, part("BedMattress", (4.1, 0.5, 6.1), (x, y + 1.1, z), (245, 245, 250), FABRIC, roty=roty, cancollide=False))
        H(h, part("BedPillow", (3, 0.7, 1.4), (x, y + 1.5, z - 2.2), (255, 255, 255), FABRIC, roty=roty, cancollide=False))
        H(h, part("BedHead", (4.5, 2.5, 0.4), (x, y + 1.8, z - 3.4), DARKWOOD, WOOD, roty=roty))


def door(h, x, y, z, w=4, hgt=7, color=GLASSC, roty=0):
    H(h, part("Door", (w, hgt, 0.4), (x, y + hgt / 2, z), color, SMOOTH,
              transparency=0.25, roty=roty))


def plant(h, x, y, z):
    H(h, part("Pot", (1.2, 1.4, 1.2), (x, y + 0.7, z), POT, WOOD, shape=2, rotz=90))
    H(h, part("Plant", (1.8, 1.8, 1.8), (x, y + 2.2, z), PLANT, GRASS, shape=0, cancollide=False))


def lamp_floor(h, x, y, z):
    H(h, part("LampStand", (0.25, 4, 0.25), (x, y + 2, z), GOLD, FOIL, cancollide=False))
    H(h, part("LampShade", (1.4, 1.4, 1.4), (x, y + 4.3, z), WARM, NEON, shape=0, cancollide=False))


# ---------- House A: Modern Cube (glass + white) ----------
cx, cz = -45, 30
H("ModernCube", part("Floor", (20, 0.5, 16), (cx, 0.25, cz), MARBLEC, MARBLE))
H("ModernCube", part("WallL", (0.5, 9, 16), (cx - 10, 4.75, cz), WHITE, SMOOTH))
H("ModernCube", part("WallR", (0.5, 9, 16), (cx + 10, 4.75, cz), WHITE, SMOOTH))
H("ModernCube", part("WallBack", (20, 9, 0.5), (cx, 4.75, cz + 8), WHITE, SMOOTH))
H("ModernCube", part("GlassL", (8, 9, 0.4), (cx - 6, 4.75, cz - 8), GLASSC, GLASS, transparency=0.45))
H("ModernCube", part("GlassR", (8, 9, 0.4), (cx + 6, 4.75, cz - 8), GLASSC, GLASS, transparency=0.45))
H("ModernCube", part("Header", (4, 2, 0.4), (cx, 8, cz - 8), WHITE, SMOOTH))
H("ModernCube", part("Roof", (21, 0.5, 17), (cx, 9.5, cz), WHITE, SMOOTH))
door("ModernCube", cx, 0.25, cz - 8)
sofa("ModernCube", cx - 4, 0.5, cz + 3)
table("ModernCube", cx - 4, 0.5, cz)
rug("ModernCube", cx - 4, 0.5, cz, 9, 7, (70, 80, 95))
tv("ModernCube", cx - 4, 0.5, cz + 7.4)
chandelier("ModernCube", cx + 4, 8.6, cz)
lamp_floor("ModernCube", cx + 8, 0.5, cz + 5)
plant("ModernCube", cx + 8, 0.5, cz - 5)

# ---------- House B: A-Frame Chalet (wood + fireplace) ----------
cx, cz = 0, 32
H("AFrame", part("Floor", (14, 0.5, 18), (cx, 0.25, cz), DARKWOOD, PLANKS))
H("AFrame", part("SlopeL", (0.4, 14, 18), (cx - 3.5, 6, cz), WOODC, PLANKS, rotz=30))
H("AFrame", part("SlopeR", (0.4, 14, 18), (cx + 3.5, 6, cz), WOODC, PLANKS, rotz=-30))
H("AFrame", part("Ridge", (0.5, 0.5, 18), (cx, 12.2, cz), DARKWOOD, WOOD))
H("AFrame", part("BackWall", (14, 9, 0.4), (cx, 4.75, cz + 9), GLASSC, GLASS, transparency=0.5))
H("AFrame", part("FrontGlassL", (4.5, 9, 0.4), (cx - 4.75, 4.75, cz - 9), GLASSC, GLASS, transparency=0.5))
H("AFrame", part("FrontGlassR", (4.5, 9, 0.4), (cx + 4.75, 4.75, cz - 9), GLASSC, GLASS, transparency=0.5))
door("AFrame", cx, 0.25, cz - 9, color=DARKWOOD)
H("AFrame", part("Fireplace", (3, 4.5, 1), (cx + 4, 2.75, cz + 8), (110, 60, 50), BRICK))
H("AFrame", part("Fire", (1.4, 1, 0.6), (cx + 4, 1.2, cz + 7.6), (255, 130, 40), NEON, cancollide=False))
bed("AFrame", cx - 4, 0.5, cz + 4)
rug("AFrame", cx, 0.5, cz + 1, 8, 6, (120, 70, 40))
table("AFrame", cx, 0.5, cz - 3, 3, WOOD, WOODC, 0)
lamp_floor("AFrame", cx - 5.5, 0.5, cz - 6)
plant("AFrame", cx + 5.5, 0.5, cz - 2)

# ---------- House C: Castle (stone + throne) ----------
cx, cz = 45, 32
H("Castle", part("Floor", (22, 0.5, 18), (cx, 0.25, cz), (200, 200, 205), SLATE))
H("Castle", part("WallL", (0.8, 10, 18), (cx - 11, 5.25, cz), STONE, COBBLE))
H("Castle", part("WallR", (0.8, 10, 18), (cx + 11, 5.25, cz), STONE, COBBLE))
H("Castle", part("WallBack", (22, 10, 0.8), (cx, 5.25, cz + 9), STONE, COBBLE))
H("Castle", part("WallFrontL", (8, 10, 0.8), (cx - 7, 5.25, cz - 9), STONE, COBBLE))
H("Castle", part("WallFrontR", (8, 10, 0.8), (cx + 7, 5.25, cz - 9), STONE, COBBLE))
H("Castle", part("Header", (6, 3, 0.8), (cx, 8.75, cz - 9), STONE, COBBLE))
for i in range(6):  # crenellations
    H("Castle", part(f"Cren{i}", (2, 1.5, 0.8), (cx - 10 + i * 4, 10.75, cz - 9), STONE, COBBLE))
H("Castle", part("Tower", (14, 6, 6), (cx + 11, 7, cz + 9), STONE, COBBLE, shape=2, rotz=90))
H("Castle", part("TowerTop", (6.6, 6.6, 6.6), (cx + 11, 15.5, cz + 9), (70, 90, 140), SLATE, shape=0))
door("Castle", cx, 0.25, cz - 9, w=5, hgt=8, color=DARKWOOD)
H("Castle", part("Dais", (5, 0.5, 4), (cx, 0.75, cz + 5.5), MARBLEC, MARBLE))
H("Castle", part("ThroneSeat", (2.2, 0.9, 2.2), (cx, 1.7, cz + 5.5), GOLD, FOIL))
H("Castle", part("ThroneBack", (2.2, 3.5, 0.4), (cx, 3.4, cz + 6.4), GOLD, FOIL))
H("Castle", part("ThroneArmL", (0.4, 1.4, 2.2), (cx - 1.3, 2.4, cz + 5.5), GOLD, FOIL))
H("Castle", part("ThroneArmR", (0.4, 1.4, 2.2), (cx + 1.3, 2.4, cz + 5.5), GOLD, FOIL))
rug("Castle", cx, 0.5, cz, 5, 14, CARPET)
chandelier("Castle", cx, 9.4, cz - 3, 1.4)
plant("Castle", cx - 8, 0.5, cz - 6)
plant("Castle", cx + 8, 0.5, cz - 6)

# ---------- House D: Villa L (pool + dining) ----------
cx, cz = -30, 92
H("VillaL", part("FloorA", (18, 0.5, 12), (cx, 0.25, cz), MARBLEC, MARBLE))
H("VillaL", part("FloorB", (8, 0.5, 12), (cx + 13, 0.25, cz + 6), MARBLEC, MARBLE))
H("VillaL", part("WallAL", (0.5, 8, 12), (cx - 9, 4.25, cz), WHITE, SMOOTH))
H("VillaL", part("WallABack", (18, 8, 0.5), (cx, 4.25, cz + 6), WHITE, SMOOTH))
H("VillaL", part("RoofA", (19, 0.5, 13), (cx, 8.5, cz), WHITE, SMOOTH))
H("VillaL", part("GlassA", (18, 8, 0.4), (cx, 4.25, cz - 6), GLASSC, GLASS, transparency=0.45))
H("VillaL", part("WallBBack", (0.5, 8, 12), (cx + 17, 4.25, cz + 6), WHITE, SMOOTH))
H("VillaL", part("WallBOuter", (8, 8, 0.5), (cx + 13, 4.25, cz + 12), WHITE, SMOOTH))
H("VillaL", part("RoofB", (9, 0.5, 13), (cx + 13, 8.5, cz + 6), WHITE, SMOOTH))
H("VillaL", part("GoldBeam", (18, 0.3, 0.3), (cx, 8, cz - 5.8), GOLD, FOIL, cancollide=False))
door("VillaL", cx - 2, 0.25, cz - 6)
H("VillaL", part("Pool", (8, 0.8, 5), (cx - 2, 0.4, cz - 12), POOL, GLASS, transparency=0.35))
H("VillaL", part("PoolDeck", (10, 0.3, 7), (cx - 2, 0.15, cz - 12), MARBLEC, MARBLE))
table("VillaL", cx + 3, 0.5, cz + 2, 5, WOOD, DARKWOOD, 0)
for dx, dz in ((-1.8, -1), (1.8, -1), (-1.8, 1), (1.8, 1)):
    H("VillaL", part("Chair", (1, 1.8, 1), (cx + 3 + dx, 1.4, cz + 2 + dz), DARKWOOD, WOOD))
H("VillaL", part("Counter", (6, 1, 1.5), (cx - 5, 1, cz + 5), (60, 60, 66), GRANITE))
H("VillaL", part("CounterGlow", (6, 0.15, 1.5), (cx - 5, 0.55, cz + 5), WARM, NEON, cancollide=False))
sofa("VillaL", cx - 5, 0.5, cz + 1, (100, 105, 118))
rug("VillaL", cx - 5, 0.5, cz + 1, 8, 6, (185, 160, 110))
chandelier("VillaL", cx + 3, 7.6, cz + 2)
bed("VillaL", cx + 13, 0.5, cz + 6)
plant("VillaL", cx - 8, 0.5, cz - 4)

# ---------- House E: Dome (octagon glass + round bed) ----------
cx, cz = 30, 92
H("Dome", part("Floor", (0.5, 16, 16), (cx, 0.25, cz), MARBLEC, MARBLE, shape=2, rotz=90))
for k in range(8):
    if k == 4:  # front opening
        continue
    a = math.radians(k * 45)
    px, pz = cx + 8 * math.sin(a), cz + 8 * math.cos(a)
    H("Dome", part(f"WallPanel{k}", (6.6, 6, 0.4), (px, 3.25, pz), GLASSC, GLASS,
                   transparency=0.4, roty=math.degrees(a)))
door("Dome", cx, 0.25, cz - 8, w=5, hgt=6, color=GLASSC)
H("Dome", part("DomeRoof", (17, 17, 17), (cx, 5, cz), GLASSC, GLASS, transparency=0.35, shape=0))
H("Dome", part("NeonRing", (0.25, 10, 10), (cx, 5.5, cz), WARM, NEON, shape=2, rotz=90, cancollide=False))
bed("Dome", cx, 0.5, cz + 2, round_=True)
rug("Dome", cx, 0.5, cz, 10, 10, (90, 60, 110))
plant("Dome", cx - 5, 0.5, cz - 3)
plant("Dome", cx + 5, 0.5, cz - 3)
lamp_floor("Dome", cx + 5.5, 0.5, cz + 4)

# ---------- assemble ----------
order = ["Shared", "ModernCube", "AFrame", "Castle", "VillaL", "Dome"]
inner = ""
for name in order:
    inner += (f'<Item class="Folder" referent="{ref()}"><Properties>'
              f'<string name="Name">{name}</string></Properties>'
              + "".join(houses.get(name, [])) + "</Item>")

with open(os.path.join(os.path.dirname(__file__), "HouseLogic.lua"), encoding="utf-8") as f:
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
    f'<float name="FogStart">300</float><float name="FogEnd">1000</float>'
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
n = doc.count("<Item class=")
n_doors = doc.count('>Door<')
assert n_doors == 5, n_doors
print(f"OK {out}: {os.path.getsize(out)} bytes, {n} items, {n_doors} doors")
