"""Rend l'arbre en image pour relecture (Pillow). Usage : python -I render_arbre_v2.py classes/passive_tree.json sortie.png
L'image n'est pas commitee (fichier de relecture)."""
import json
import math
import sys
from PIL import Image, ImageDraw, ImageFont

tree = json.load(open(sys.argv[1], encoding="utf-8"))
out = sys.argv[2]
W = H = 3900
S = 64.0
CX, CY = W / 2, H / 2 + 80
BG = (16, 18, 24)
font = lambda size, bold=False: ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf", size)
F_SMALL, F_MID, F_BIG, F_TITLE, F_ARM = font(17), font(21, True), font(25, True), font(54, True), font(40, True)

colors = {a["id"]: tuple(int(a["color"][i:i + 2], 16) for i in (1, 3, 5)) for a in tree["arms"]}
NEUTRAL = (225, 225, 230)
GOLD = (242, 196, 90)
nodes = {n["id"]: n for n in tree["nodes"]}
U = float(tree.get("layout", {}).get("scale", 1))  # pos en unites de dessin -> unites du gabarit
P = lambda n: (CX + n["pos"][0] / U * S, CY + n["pos"][1] / U * S)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# distance rings (15 / 30 / 50 / 75 points, at the template distances)
for r, lab in ((6.5, "15"), (11, "30"), (17, "50"), (23.5, "75")):
    d.ellipse([CX - r * S, CY - r * S, CX + r * S, CY + r * S], outline=(40, 44, 56), width=2)
    d.text((CX + 6, CY - r * S + 6), f"{lab} pts", font=F_SMALL, fill=(80, 86, 104))

for a, b in tree["edges"]:
    na, nb = nodes[a], nodes[b]
    bridge = na["arm"] is None and na["kind"] != "center" or nb["arm"] is None and nb["kind"] != "center"
    col = (95, 95, 105) if bridge else tuple(int(c * 0.45) for c in colors.get(na["arm"] or nb["arm"], NEUTRAL))
    d.line([P(na), P(nb)], fill=col, width=4 if not bridge else 3)

SIZE = {"center": 30, "small": 10, "bridge_small": 9, "notable_15": 18, "side": 16, "notable_30": 22,
        "notable_50": 26, "hybrid": 18, "mega": 34}
LABEL_FONT = {"notable_15": F_MID, "side": F_SMALL, "notable_30": F_MID, "notable_50": F_MID, "hybrid": F_SMALL,
              "mega": F_BIG}
for n in tree["nodes"]:
    x, y = P(n)
    r = SIZE[n["kind"]]
    col = NEUTRAL if n["arm"] is None else colors[n["arm"]]
    if n["kind"] == "side":
        d.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=BG, outline=col, width=4)
    elif n["kind"] == "mega":
        pts = []
        for k in range(10):
            rr = r if k % 2 == 0 else r * 0.5
            t = -math.pi / 2 + k * math.pi / 5
            pts.append((x + rr * math.cos(t), y + rr * math.sin(t)))
        d.polygon(pts, fill=col, outline=GOLD, width=3)
    elif n["kind"] in ("small", "bridge_small"):
        d.ellipse([x - r, y - r, x + r, y + r], fill=col if n["kind"] == "small" else (70, 72, 80))
    else:
        d.ellipse([x - r, y - r, x + r, y + r], fill=BG, outline=col, width=5)
        d.ellipse([x - r * 0.45, y - r * 0.45, x + r * 0.45, y + r * 0.45], fill=col)
    if n["kind"] in LABEL_FONT:
        txt = n["name_fr"].split(" : ")[-1] if n["kind"] == "notable_30" and " : " in n["name_fr"] else n["name_fr"]
        f = LABEL_FONT[n["kind"]]
        w = d.textlength(txt, font=f)
        tc = GOLD if n["kind"] == "mega" else ((235, 235, 240) if n["kind"] != "side" else (170, 172, 182))
        ch = n.get("choice")
        above = False
        if ch:
            grp = [m for m in tree["nodes"] if m.get("choice", {}).get("group") == ch["group"]]
            idx = grp.index(n)
            above = (len(grp) == 2 and idx == 0) or (len(grp) == 3 and idx != 1)
        ty = y - r - 5 - f.size - 4 if above else y + r + 5
        d.text((x - w / 2 + 1, ty + 1), txt, font=f, fill=(0, 0, 0))
        d.text((x - w / 2, ty), txt, font=f, fill=tc)

for a in tree["arms"]:
    t = math.radians(a["angle_deg"])
    x, y = CX + 27.2 * S * math.cos(t), CY + 27.2 * S * math.sin(t)
    w = d.textlength(a["name_fr"].upper(), font=F_ARM)
    d.text((x - w / 2, y - 22), a["name_fr"].upper(), font=F_ARM, fill=colors[a["id"]])

d.text((60, 40), "Arbre des passifs V2", font=F_TITLE, fill=(235, 235, 240))
leg = [("petit noeud (rangs)", "small"), ("notable 15", "notable_15"), ("detour", "side"), ("notable 30", "notable_30"),
       ("notable 50", "notable_50"), ("mega 75", "mega"), ("pont : passage / hybride", "hybrid")]
lx, ly = 64, 130
for lab, kind in leg:
    r = min(SIZE[kind], 18)
    col = NEUTRAL if kind == "hybrid" else (230, 107, 82)
    if kind == "side":
        d.polygon([(lx + 18, ly), (lx + 18 + r, ly + r), (lx + 18, ly + 2 * r), (lx + 18 - r, ly + r)], outline=col, width=4)
    elif kind == "mega":
        d.regular_polygon((lx + 18, ly + 18, 18), 5, fill=col, outline=GOLD)
    elif kind == "small":
        d.ellipse([lx + 8, ly + 8, lx + 28, ly + 28], fill=col)
    else:
        d.ellipse([lx + 18 - r, ly + 18 - r, lx + 18 + r, ly + 18 + r], outline=col, width=4)
    d.text((lx + 50, ly + 6), lab, font=F_MID, fill=(200, 202, 210))
    ly += 46
d.text((64, ly + 10), "Anneaux = distance du centre en points (15 / 30 / 50 / 75).", font=F_SMALL, fill=(130, 134, 148))
img.save(out)
print("saved", out)
