#!/usr/bin/env python3
"""Geometry audit: SAT furniture-vs-walls, furniture-vs-furniture, stair
reach, door clearance, floor placement."""
import xml.etree.ElementTree as ET

t = ET.parse("houses.rbxlx")
CHAR_H = 5.0
TOL = 0.15      # wall clipping tolerance (studs)
FTOL = 0.3      # furniture-vs-furniture tolerance (studs)

# root furniture that must stand on a floor
GROUND = {"SofaBase", "BedBase", "Nightstand", "Wardrobe", "Bookshelf",
          "TVStand", "TubOuter", "ToiletBase", "SinkPedestal", "Fridge",
          "Cabinet", "Fireplace", "Pot", "LampBase"}
FURN = GROUND | {"CoffeeTable", "DiningTable", "ChairSeat", "CarBody",
                 "Dais", "Dais2", "ThroneSeat", "PoolBasin", "PondBasin",
                 "LowTable", "BonsaiPot"}

def props(it):
    p = it.find("./Properties")
    nm = p.find("string[@name='Name']")
    sz = p.find("Vector3")
    cf = p.find("CoordinateFrame")
    pos = tuple(float(cf.find(a).text) for a in "XYZ")
    size = tuple(float(sz.find(a).text) for a in "XYZ")
    R = [[float(cf.find(f"R{i}{j}").text) for j in range(3)] for i in range(3)]
    return (nm.text if nm is not None else "?", size, pos, R)

def axes(R):
    return [(R[0][j], R[1][j], R[2][j]) for j in range(3)]

def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])

def sat(sizeA, posA, RA, sizeB, posB, RB, tol):
    """Full 15-axis SAT for two OBBs."""
    axA, axB = axes(RA), axes(RB)
    d = [posB[i] - posA[i] for i in range(3)]
    for ax in axA + axB + [cross(a, b) for a in axA for b in axB]:
        L = sum(v * v for v in ax)
        if L < 1e-9:
            continue
        ax = tuple(v / L ** 0.5 for v in ax)
        dist = abs(sum(d[j] * ax[j] for j in range(3)))
        ext = 0.0
        for R, s in ((RA, sizeA), (RB, sizeB)):
            for j in range(3):
                ext += abs(sum(axes(R)[j][k] * ax[k] for k in range(3))) * s[j] / 2
        if dist > ext - tol:
            return False
    return True

def y_top(p):
    """Rotation-aware top surface Y."""
    _, s, pos, R = p
    hy = sum(abs(R[i][1]) * s[i] / 2 for i in range(3))
    return pos[1] + hy

issues = []
for folder in t.iter("Item"):
    if folder.get("class") != "Folder":
        continue
    hname = folder.find("./Properties/string[@name='Name']").text
    if hname == "Shared":
        continue
    parts = [props(it) for it in folder.findall("./Item")]
    tops = sorted({round(y_top(p), 1) for p in parts
                   if p[0].startswith(("Floor", "Platform", "TowerFloor"))},
                  reverse=True)
    walls = [p for p in parts if p[0].startswith(("Wall", "Slope", "Header"))]
    steps = sorted((p for p in parts if p[0].startswith("Step")),
                   key=lambda p: p[2][1])
    roots = [p for p in parts if p[0] in FURN]

    for n, s, pos, R in roots:
        for wn, ws, wp, WR in walls:
            if sat(s, pos, R, ws, wp, WR, TOL):
                issues.append(f"{hname}: {n} intersects {wn}")
        for sn, ss, sp, SR in steps:
            if sat(s, pos, R, ss, sp, SR, TOL):
                issues.append(f"{hname}: {n} intersects {sn} (stair)")
        if n in GROUND:
            base = pos[1] - sum(abs(R[i][1]) * s[i] / 2 for i in range(3))
            if not any(abs(base - ft) < 1.0 for ft in tops):
                issues.append(f"{hname}: {n} base y={base:.1f} off floors "
                              f"{tops}")

    # deliberate stacks: bonsai on LowTable, pool lamp sits on basin rim
    STACK_OK = {frozenset(("LowTable", "BonsaiPot")),
                frozenset(("PoolBasin", "LampBase")),
                frozenset(("Dais", "Dais2")), frozenset(("Dais", "ThroneSeat")),
                frozenset(("Dais2", "ThroneSeat"))}
    for i in range(len(roots)):
        for j in range(i + 1, len(roots)):
            a, b = roots[i], roots[j]
            if sat(a[1], a[2], a[3], b[1], b[2], b[3], FTOL):
                if frozenset((a[0], b[0])) in STACK_OK:
                    continue
                issues.append(f"{hname}: {a[0]} overlaps {b[0]}")

    if steps:
        top_step = steps[-1][2][1] + sum(
            abs(steps[-1][3][i][1]) * steps[-1][1][i] / 2 for i in range(3))
        if abs(top_step - tops[0]) > 1.2:
            issues.append(f"{hname}: stair top {top_step:.1f} vs top floor "
                          f"{tops[0]}")
        rise = (steps[-1][2][1] - steps[0][2][1]) / max(len(steps) - 1, 1)
        if rise > 2.2:
            issues.append(f"{hname}: stair rise {rise:.2f} too steep")

    for n, s, pos, R in parts:
        if n == "Door":
            if s[1] < CHAR_H + 1:
                issues.append(f"{hname}: door height {s[1]:.1f} too low")
            if not any(abs(pos[1] - s[1] / 2 - ft) < 1.0 for ft in tops):
                issues.append(f"{hname}: door base off floor")

print(f"{len(issues)} issues")
seen = set()
for i in issues:
    if i not in seen:
        print(" -", i)
        seen.add(i)
