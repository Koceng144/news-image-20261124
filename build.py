#!/usr/bin/env python3
"""Render entry.png for the 24 November 2026 news-image entry.

Offline composition script (PIL only). Deterministic: no clock, no
randomness, no network. Run from the repo root:
    python3 build.py
Produces entry.png (1024x1024, <= 1 MiB) next to this file.

Design (v2 composition upgrade): cream broadsheet front page with a
centred nameplate + red date band masthead, a markets bar-chart strip
(honest % moves from facts-2026-11-24.md), ONE dominant full-width
lead (Sanofi $41bn: big image left, big headline + deck right), two
smaller subordinate secondary panels (Hormuz, Nepal quake), the day
in ten as a numbered vertical timeline rail with region tags, a dotted
world map with numbered pins, tail list, DATE CHECK box — original
layout and artwork for 24 Nov.

Date rule (from facts-2026-11-24.md): the ten leads (1-10) are all
stories whose EVENT happened on Tue 24 Nov 2026 (flagged ✅).
Items 11-38 were REPORTED on 24 Nov; some describe events of
22-23 Nov and are worded as reports, never as "happened today".
Excluded near-miss stories appear ONLY in the DATE CHECK box.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
CREAM = (247, 238, 218)
PAPER = (250, 243, 228)
INK = (26, 24, 20)
RED = (163, 29, 29)
DARKRED = (122, 18, 18)
NAVY = (31, 78, 121)
GOLD = (176, 124, 24)
GREY = (110, 102, 88)
LIGHT = (233, 222, 198)
RULE = (60, 52, 40)
GREEN = (30, 90, 50)
TEAL = (40, 110, 110)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, fnt, width, fill=INK, leading=None):
    if leading is None:
        leading = fnt.size + 3
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def secondary_panel(draw, canvas, img, x, y, w, num, place, headline,
                    deck, conf, source):
    """Subordinate lead: image strip left, text right. Deliberately
    smaller than the dominant lead (image 168x90 vs lead 600x176)."""
    h = 92
    draw.rectangle([x, y, x + w, y + h], outline=RULE, width=1)
    iw, ih = 168, h - 2
    scale = max(iw / img.size[0], ih / img.size[1])
    pic = img.resize((round(img.size[0] * scale),
                      round(img.size[1] * scale)), Image.LANCZOS)
    left = (pic.size[0] - iw) // 2
    top = (pic.size[1] - ih) // 2
    pic = pic.crop((left, top, left + iw, top + ih))
    canvas.paste(pic, (x + 1, y + 1))
    draw.rectangle([x + 1, y + 1, x + 19, y + 17], fill=RED)
    draw.text((x + 6, y + 3), str(num), font=font(SANS_B, 10),
              fill=(255, 255, 255))
    tx, tw = x + iw + 8, w - iw - 12
    draw.text((tx, y + 4), place, font=font(SANS_B, 8), fill=NAVY)
    yy = text_block(draw, tx, y + 16, headline, font(SERIF, 15), tw,
                    leading=17)
    text_block(draw, tx, yy + 1, deck, font(SERIF_R, 10), tw, leading=12)
    draw.text((tx, y + h - 12), "(%s) \u00b7 %s" % (source, conf),
              font=font(SANS, 8), fill=GREY)


def fit_timeline_deck(draw, head, deck, src, max_w):
    """Trim a timeline deck (never the headline) so one row fits
    before the region tag. Deterministic: drops whole words."""
    f_head, f_deck, f_src = font(SERIF, 12), font(SERIF_R, 10), \
        font(SANS, 8)
    d, trimmed = deck, False
    while d and " " in d and draw.textlength(head, font=f_head) + \
            draw.textlength(" \u2014 " + d, font=f_deck) + \
            draw.textlength("  (" + src + ")", font=f_src) > max_w:
        d = d.rsplit(" ", 1)[0]
        trimmed = True
    return d + " \u2026" if trimmed else d


def point_in_poly(px, py, poly):
    inside, n = False, len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and \
                (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


# ---------------- original hero artwork (PIL-drawn, no photos) ----------------

# Hero art is drawn on a 640x240 canvas: the panel crop is 310x118
# (aspect 2.63), so a 640x240 source (2.67) loses almost nothing at
# the edges — v1 used 640x360 and the centre crop cut the "$41bn",
# the sun and the smoke tops off.
def art_sanofi():
    """Money hero: teal lab / market scene, rising chart, pills, coins."""
    img = Image.new("RGB", (640, 240), (16, 74, 84))
    d = ImageDraw.Draw(img)
    for i in range(9):  # faint horizontal grid
        y = 12 + i * 26
        d.line([0, y, 640, y], fill=(24, 96, 106), width=1)
    for i in range(13):
        x = 10 + i * 50
        d.line([x, 0, x, 240], fill=(24, 96, 106), width=1)
    # gold coins, bottom right
    for (cx, cy, r) in [(545, 205, 34), (588, 216, 24), (505, 222, 19)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(212, 160, 48),
                  outline=(140, 100, 20), width=3)
        d.text((cx - 7, cy - 11), "$", font=font(SANS_B, 20),
               fill=(120, 84, 16))
    # pill capsules, bottom left
    for (cx, cy, ang) in [(105, 205, -25), (185, 220, 15), (145, 175, 55)]:
        cap = Image.new("RGBA", (110, 46), (0, 0, 0, 0))
        cd = ImageDraw.Draw(cap)
        cd.rounded_rectangle([0, 0, 109, 45], radius=22, fill=(245, 240, 225))
        cd.rounded_rectangle([55, 0, 109, 45], radius=22, fill=(198, 52, 44))
        cap = cap.rotate(ang, expand=True, resample=Image.BICUBIC)
        img.paste(cap, (cx - cap.size[0] // 2, cy - cap.size[1] // 2), cap)
    # rising green chart with arrow
    pts = [(40, 185), (130, 158), (200, 168), (290, 128), (360, 138),
           (450, 88), (540, 52), (600, 28)]
    d.line(pts, fill=(96, 220, 130), width=6, joint="curve")
    d.polygon([(600, 28), (568, 22), (574, 52)], fill=(96, 220, 130))
    for (px, py) in pts:
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(240, 245, 235))
    d.text((36, 12), "$41bn", font=font(SERIF, 52), fill=(250, 244, 228))
    return img


def art_hormuz():
    """Sea hero: dusk sky, three burning tankers, smoke over the Gulf."""
    img = Image.new("RGB", (640, 240), (58, 38, 74))
    d = ImageDraw.Draw(img)
    for y in range(128):  # dusk gradient sky
        r = 214 - y // 2
        g = 122 - y // 3
        b = 62 + y // 4
        d.line([0, y, 640, y], fill=(max(r, 60), max(g, 40), b))
    d.ellipse([480, 38, 552, 110], fill=(250, 214, 130))  # low sun
    d.rectangle([0, 128, 640, 240], fill=(18, 42, 68))  # sea
    for y in (148, 176, 206, 230):
        for x in range(0, 640, 46):
            d.line([x, y, x + 26, y], fill=(44, 84, 120), width=3)
    # three tankers, near to far
    for (hx, hy, sc) in [(320, 145, 1.05), (80, 165, 0.85), (430, 180, 0.65)]:
        hw, hh = int(190 * sc), int(30 * sc)
        d.rectangle([hx, hy, hx + hw, hy + hh], fill=(12, 14, 18))
        d.rectangle([hx + hw - 52 * sc, hy - 20 * sc, hx + hw - 18 * sc,
                     hy], fill=(12, 14, 18))
        d.rectangle([hx + 8, hy - 8, hx + 30, hy], fill=(200, 60, 40))
        # flames above the deck
        fx = hx + hw // 2
        d.polygon([(fx - 32 * sc, hy), (fx - 11 * sc, hy - 52 * sc),
                   (fx + 4 * sc, hy - 26 * sc), (fx + 20 * sc, hy - 58 * sc),
                   (fx + 36 * sc, hy)],
                  fill=(240, 120, 30))
        d.polygon([(fx - 15 * sc, hy), (fx - 4 * sc, hy - 34 * sc),
                   (fx + 13 * sc, hy - 16 * sc), (fx + 19 * sc, hy)],
                  fill=(250, 210, 80))
        # small smoke puffs rising from the flames
        for k, sr in enumerate((16, 12, 9)):
            d.ellipse([fx - sr + k * 7, hy - 62 * sc - k * 18,
                       fx + sr + k * 7, hy - 62 * sc - k * 18 + sr * 2],
                      fill=(88, 86, 90))
    return img


def art_quake():
    """Quake hero: Himalayan peaks, red seismograph line, webcam frame."""
    img = Image.new("RGB", (640, 240), (168, 196, 214))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 640, 100], fill=(150, 186, 210))
    d.ellipse([545, 18, 598, 71], fill=(250, 242, 210))  # pale sun
    # snow peaks, back then front
    d.polygon([(0, 240), (90, 78), (210, 240)], fill=(120, 138, 158))
    d.polygon([(62, 118), (90, 78), (120, 120), (104, 114), (90, 128),
               (78, 112)], fill=(250, 250, 248))
    d.polygon([(180, 240), (330, 46), (480, 240)], fill=(96, 112, 134))
    d.polygon([(296, 94), (330, 46), (368, 96), (348, 90), (330, 106),
               (312, 88)], fill=(250, 250, 248))
    d.polygon([(380, 240), (520, 94), (640, 240)], fill=(128, 146, 164))
    d.polygon([(494, 128), (520, 94), (548, 130), (534, 124), (520, 136),
               (506, 122)], fill=(250, 250, 248))
    # valley floor + houses
    d.rectangle([0, 202, 640, 240], fill=(104, 128, 84))
    for hx in (70, 150, 470, 550):
        d.rectangle([hx, 178, hx + 48, 202], fill=(226, 214, 186))
        d.polygon([(hx - 6, 180), (hx + 24, 160), (hx + 54, 180)],
                  fill=(168, 52, 40))
    # red seismograph zigzag across the middle
    pts = [(0, 140), (60, 140), (90, 126), (120, 156), (150, 118),
           (180, 160), (205, 140), (300, 140), (330, 124), (360, 158),
           (390, 116), (420, 158), (450, 140), (640, 140)]
    d.line(pts, fill=(198, 30, 26), width=5, joint="curve")
    # webcam frame: corner brackets + REC dot
    for (bx, by, sx, sy) in [(12, 12, 1, 1), (628, 12, -1, 1),
                             (12, 228, 1, -1), (628, 228, -1, -1)]:
        d.line([bx, by, bx + 30 * sx, by], fill=(255, 255, 255), width=4)
        d.line([bx, by, bx, by + 30 * sy], fill=(255, 255, 255), width=4)
    d.ellipse([32, 28, 46, 42], fill=(198, 30, 26))
    d.text((52, 26), "REC", font=font(SANS_B, 13), fill=(255, 255, 255))
    return img


def main():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W - 1, H - 1], outline=RULE, width=2)

    # ---- masthead (v2): centred nameplate + red date band ----
    # v1 had a small top strap, left-aligned date and a tilted stamp;
    # v2 centres the nameplate, doubles the rule, and puts the date in
    # a full-width red band so the page reads as 24 Nov at thumbnail.
    draw.text((28, 8), "No. 24 \u00b7 TUESDAY EDITION",
              font=font(SANS_B, 9), fill=NAVY)
    folio_r = "ONE DAY \u00b7 ONE PAGE \u00b7 38 STORIES"
    draw.text((996 - draw.textlength(folio_r, font=font(SANS_B, 9)), 8),
              folio_r, font=font(SANS_B, 9), fill=NAVY)
    draw.line([28, 22, 996, 22], fill=INK, width=1)
    name = "THE WORLD IN ONE DAY"
    draw.text(((1024 - draw.textlength(name, font=font(SERIF, 46))) / 2,
               26), name, font=font(SERIF, 46), fill=INK)
    draw.line([28, 78, 996, 78], fill=INK, width=3)
    draw.line([28, 82, 996, 82], fill=INK, width=1)
    draw.rectangle([28, 88, 996, 116], fill=DARKRED)
    draw.text((36, 94), "TUESDAY 24 NOVEMBER 2026",
              font=font(SERIF, 20), fill=(255, 255, 255))
    band_r = "EVERY STORY REPORTED THAT DAY \u00b7 7 REGIONS"
    draw.text((996 - draw.textlength(band_r, font=font(SANS_B, 10)), 97),
              band_r, font=font(SANS_B, 10), fill=(255, 255, 255))

    # ---- markets chart strip: honest % bars (facts #28 + L1) ----
    # % moves only; prices are text chips (different units, no bars).
    # Nvidia +31% is the scale max; all bars share one linear scale.
    draw.rectangle([28, 124, 996, 192], outline=RULE, width=1,
                   fill=(238, 228, 204))
    draw.text((36, 128),
              "MARKETS IN ONE GLANCE \u2014 % MOVES REPORTED 24 NOV",
              font=font(SANS_B, 10), fill=INK)
    chip = "BRENT $86.7 \u00b7 GOLD $3,620 \u00b7 BITCOIN $60,400 \u00b7 GAS +12%"
    draw.text((996 - draw.textlength(chip, font=font(SANS, 8)), 130),
              chip, font=font(SANS, 8), fill=GREY)
    bars_l = [("NVIDIA", "+31%", 31.0), ("NASDAQ", "+6.51%", 6.51),
              ("KOSPI", "+6.3%", 6.3)]
    bars_r = [("S&P 500", "+4.73%", 4.73), ("NIKKEI", "+3.91%", 3.91),
              ("DOW", "+3.01%", 3.01)]
    for col_x, items in ((36, bars_l), (516, bars_r)):
        for j, (lab, val, pct) in enumerate(items):
            by = 146 + j * 15
            draw.text((col_x, by), lab, font=font(SANS_B, 8), fill=INK)
            bx = col_x + 64
            bw = max(5, round(pct / 31.0 * 330))
            draw.rectangle([bx, by + 1, bx + bw, by + 9], fill=GREEN)
            draw.text((bx + bw + 5, by - 1), val, font=font(SERIF, 11),
                      fill=INK)

    # ---- lead story: ONE dominant full-width block (No. 1 Sanofi) ----
    draw.text((28, 198), "LEAD STORY \u2014 No. 1",
              font=font(SANS_B, 10), fill=RED)
    lx, ly, lw, lh = 28, 214, 600, 176
    draw.rectangle([lx, ly, lx + lw, ly + lh], outline=RULE, width=1)
    limg = art_sanofi()
    # fit-height, centred (not cropped): the whole scene — $41bn,
    # chart, pills, coins — stays in frame; side bands use the art's
    # own teal so they read as a matte, not a crop.
    draw.rectangle([lx + 1, ly + 1, lx + lw - 1, ly + lh - 1],
                   fill=(16, 74, 84))
    scale = (lh - 2) / limg.size[1]
    pic = limg.resize((round(limg.size[0] * scale), lh - 2),
                      Image.LANCZOS)
    img.paste(pic, (lx + 1 + (lw - 2 - pic.size[0]) // 2, ly + 1))
    draw.rectangle([lx + 1, ly + 1, lx + 19, ly + 17], fill=RED)
    draw.text((lx + 6, ly + 3), "1", font=font(SANS_B, 10),
              fill=(255, 255, 255))
    tx = 644
    draw.text((tx, 216), "PARIS \u00b7 MARKETS",
              font=font(SANS_B, 10), fill=NAVY)
    yy = text_block(draw, tx, 232, "Sanofi buys Insmed for $41 billion",
                    font(SERIF, 30), 352, leading=32)
    draw.line([tx, yy + 4, 996, yy + 4], fill=GOLD, width=2)
    yy2 = text_block(draw, tx, yy + 12,
                     "French drugmaker agrees $175 a share in cash for US "
                     "biotech Insmed \u2014 the biggest biotech deal in "
                     "nearly three years; Sanofi shares rose ~4.5%.",
                     font(SERIF_R, 13), 352, leading=16)
    draw.text((tx, yy2 + 6), "$175 a share  \u00b7  Sanofi +4.5%",
              font=font(SERIF, 14), fill=RED)
    draw.text((tx, yy2 + 26), "(Reuters) \u00b7 CONFIRMED",
              font=font(SANS, 8), fill=GREY)
    draw.line([28, 398, 996, 398], fill=INK, width=1)

    # ---- secondary leads: smaller, clearly subordinate ----
    draw.text((28, 404), "THE OTHER LEADS",
              font=font(SANS_B, 10), fill=INK)
    secondary_panel(draw, img, art_hormuz(), 28, 418, 478, 2,
                    "STRAIT OF HORMUZ \u00b7 GULF",
                    "Three tankers hit mines in Hormuz",
                    "Tehran says three tankers caught fire after hitting "
                    "naval mines; US talks ruled out until seven "
                    "conditions are met.",
                    "CLAIM", "Horizon")
    secondary_panel(draw, img, art_quake(), 518, 418, 478, 3,
                    "TAPLEJUNG \u00b7 NEPAL",
                    "5.6-magnitude quake shakes Nepal border",
                    "Struck at ~07:02 IST, felt across Sikkim, north "
                    "Bengal, Bhutan and Bangladesh; no casualties "
                    "reported.",
                    "CONFIRMED", "The Hindu")
    draw.line([28, 518, 996, 518], fill=INK, width=1)

    # ---- the day in ten: numbered vertical timeline rail ----
    # v2 replaces the v1 2x4 card grid: one row per story (Nos. 4-10)
    # on a vertical spine with numbered nodes, headline + one-line
    # deck + source on a single line, region tag chip at right.
    draw.text((28, 524), "THE DAY IN TEN \u2014 SEVEN MORE LEADS, IN ORDER",
              font=font(SANS_B, 10), fill=INK)
    draw.text((996 - draw.textlength("Nos. 4\u201310",
                                     font=font(SANS_B, 10)), 524),
              "Nos. 4\u201310", font=font(SANS_B, 10), fill=RED)
    rows = [
        (4, DARKRED, "GAZA", "Israeli strikes kill at least six in Gaza",
         "Airstrikes killed at least six Palestinians, incl. two police "
         "officers.", "Reuters"),
        (5, (90, 60, 110), "VATICAN",
         "Pope diary: \u2018I saw the devil three times\u2019",
         "Vatican published excerpts of the late pontiff\u2019s private "
         "diary (1992\u20132024).", "Guardian"),
        (6, NAVY, "UAE", "Bus\u2013truck crash in UAE kills 13",
         "A bus carrying 41 people hit a truck on Al Watan Road, Ras Al "
         "Khaimah; 14 injured.", "Khaleej Times"),
        (7, TEAL, "PACIFIC", "Solomon Islands scraps China security pact",
         "Honiara will not renew its 2022 pact; a new treaty with "
         "Australia follows.", "ABC News"),
        (8, NAVY, "BANGLADESH", "Hasina plans 16 Dec return to Bangladesh",
         "The ousted PM plans to return from exile in India; Dhaka says "
         "she faces arrest.", "Reuters"),
        (9, DARKRED, "UKRAINE",
         "Russian strike kills 2, wounds 22 in Zaporizhzhia",
         "Overnight attack partly destroyed a five-storey residential "
         "building.", "Reuters"),
        (10, GREEN, "GERMANY",
         "Germany first into Ukraine\u2019s Delta system",
         "Defence ministers signed a letter of intent in Berlin; Germany "
         "will co-develop it.", "Kyiv Independent"),
    ]
    draw.line([44, 552, 44, 678], fill=RULE, width=2)
    for i, (num, colour, tag, head, deck, src) in enumerate(rows):
        ry = 542 + i * 21
        cy = ry + 10
        draw.ellipse([44 - 9, cy - 9, 44 + 9, cy + 9], fill=colour,
                     outline=(255, 255, 255), width=1)
        tw = draw.textlength(str(num), font=font(SANS_B, 9))
        draw.text((44 - tw / 2, cy - 6), str(num), font=font(SANS_B, 9),
                  fill=(255, 255, 255))
        d = fit_timeline_deck(draw, head, deck, src, 820)
        draw.text((62, ry + 4), head, font=font(SERIF, 12), fill=INK)
        hx = 62 + draw.textlength(head, font=font(SERIF, 12))
        draw.text((hx, ry + 5), " \u2014 " + d, font=font(SERIF_R, 10),
                  fill=INK)
        sx = hx + draw.textlength(" \u2014 " + d, font=font(SERIF_R, 10))
        draw.text((sx + 4, ry + 5), "(" + src + ")",
                  font=font(SANS, 8), fill=GREY)
        draw.rectangle([896, ry + 2, 996, ry + 18], fill=colour)
        tagw = draw.textlength(tag, font=font(SANS_B, 8))
        draw.text((946 - tagw / 2, ry + 5), tag, font=font(SANS_B, 8),
                  fill=(255, 255, 255))
        if i < 6:
            draw.line([62, ry + 20, 890, ry + 20], fill=LIGHT, width=1)
    draw.line([28, 696, 996, 696], fill=INK, width=1)

    # ---- map + tail list (shorter map: v2 freed the height for the
    # lead + timeline; pins re-spread for the 140px map, r=6) ----
    draw.text((28, 702), "WHERE IT HAPPENED",
              font=font(SANS_B, 10), fill=INK)
    draw.text((560, 702), "ALSO ON TUESDAY \u2014 28 MORE STORIES",
              font=font(SANS_B, 10), fill=INK)
    mx, my, mw, mh = 28, 718, 512, 140
    draw.rectangle([mx, my, mx + mw, my + mh], outline=RULE, width=1,
                   fill=(238, 228, 204))
    polys = [
        [(8, 20), (28, 12), (38, 18), (36, 30), (28, 38), (16, 36),
         (10, 28)],  # North America
        [(28, 48), (36, 46), (40, 58), (34, 72), (29, 60)],  # S. America
        [(46, 14), (56, 12), (60, 20), (54, 26), (47, 24)],  # Europe
        [(46, 32), (60, 30), (64, 44), (56, 60), (49, 48)],  # Africa
        [(60, 12), (92, 10), (96, 24), (88, 36), (76, 32),
         (64, 24)],  # Asia
        [(86, 58), (96, 56), (97, 64), (88, 66)],  # Oceania
    ]
    # v2: denser dots (step 2, not 3) so the continents read, and pins
    # re-gridded by hand — v1 Europe / Gulf clusters were one red blob.
    for gy in range(8, 72, 2):
        for gx in range(3, 98, 2):
            if any(point_in_poly(gx, gy, p) for p in polys):
                draw.ellipse([mx + gx / 100 * mw - 1.2,
                              my + gy / 100 * mh - 1.2,
                              mx + gx / 100 * mw + 1.2,
                              my + gy / 100 * mh + 1.2],
                             fill=(150, 128, 90))
    # pins: (story, x%, y%) — schematic spread, re-gridded for the
    # shorter map so no two pins touch. No. 38 (black hole) has no place.
    pins = [(1, 48, 27), (2, 60, 41), (3, 73, 36), (4, 56, 36),
            (5, 54, 30), (6, 64, 44), (7, 94, 60), (8, 76, 40),
            (9, 58, 23), (10, 48, 16), (11, 17, 33), (12, 49, 35),
            (13, 45, 21), (14, 60, 12), (15, 69, 39), (16, 63, 26),
            (17, 57, 44), (18, 42, 27), (19, 38, 32), (20, 80, 45),
            (21, 64, 17), (22, 53, 45), (23, 50, 53), (24, 56, 57),
            (25, 24, 52), (26, 54, 14), (27, 12, 38), (28, 23, 26),
            (29, 19, 21), (30, 40, 19), (31, 52, 20), (32, 42, 13),
            (33, 30, 58), (34, 82, 32), (35, 66, 33), (36, 10, 27),
            (37, 26, 42)]
    for num, px, py in pins:
        cx, cy = mx + px / 100 * mw, my + py / 100 * mh
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED,
                     outline=(255, 255, 255), width=1)
        tw = draw.textlength(str(num), font=font(SANS_B, 7))
        draw.text((cx - tw / 2, cy - 4), str(num), font=font(SANS_B, 7),
                  fill=(255, 255, 255))
    draw.text((mx + 4, my + mh - 14),
              "Each number is the story with that number on this page. "
              "No. 38 has no single place.",
              font=font(SANS, 8), fill=GREY)

    tail = [
        (11, "Nvidia chief returns; shares soar 31%"),
        (12, "Ukraine sinks Russian warship off Libya"),
        (13, "NATO vows space defence after satellite reports"),
        (14, "Medvedev warns of preventive nuclear attack"),
        (15, "Nepal PM in India; Delhi pledges aid"),
        (16, "Iraq moves to take over Kurdish oilfields"),
        (17, "Qatar PM meets Vance, Rubio on Iran talks"),
        (18, "EU proposes 22nd sanctions package"),
        (19, "Spain amnesties Puigdemont"),
        (20, "14 nations back ICJ Rohingya ruling"),
        (21, "700,000+ Russian soldiers killed, tally finds"),
        (22, "Saudi strikes in Yemen kill about 25"),
        (23, "Drone strike hits UN building in Khartoum"),
        (24, "DRC fighting traps Ebola responders"),
        (25, "Car bomb hits governor's office in Colombia"),
        (26, "Russian drone enters Polish airspace"),
        (27, "Mexico to try 'Chapo Isidro' despite US plea"),
        (28, "Wall Street's best day in over a year"),
        (29, "CrowdStrike to buy Zscaler in $43.9bn deal"),
        (30, "European gas soars 12% ahead of cold wave"),
        (31, "Germany business sentiment keeps improving"),
        (32, "Belgium strike cancels flights, budget set"),
        (33, "Brazil cuts 2027 growth forecast; real weakens"),
        (34, "China launches 6G pilot tests in 8 regions"),
        (35, "Pakistan's Zeeshan Ali to fly to China's station"),
        (36, "Two US states sue Musk firms over Grok images"),
        (37, "UN chief urges global AI safety framework"),
        (38, "Most distant glowing black hole found"),
    ]
    fnt = font(SANS, 8)
    for i, (num, txt) in enumerate(tail):
        col, row = divmod(i, 14)
        x = 560 + col * 220
        y = 720 + row * 10
        draw.text((x, y), "%d" % num, font=font(SANS_B, 8), fill=RED)
        draw.text((x + 16, y), txt, font=fnt, fill=INK)

    # ---- date check ----
    dy = 870
    draw.rectangle([28, dy, 996, dy + 94], outline=RED, width=2)
    draw.text((36, dy + 6), "DATE CHECK \u2014 HELD OVER, NOT TUESDAY",
              font=font(SANS_B, 11), fill=RED)
    exclusions = (
        "Left out as earlier days\u2019 news: COP31 collapse itself (Sun 22 Nov) \u00b7 "
        "US loses measles elimination status (17 Nov) \u00b7 Indonesia factory FIRE "
        "(Sat 21 Nov \u2014 only the continuing search is 24 Nov) \u00b7 Spain 15\u20130 Fiji "
        "match (Mon 23 Nov) \u00b7 Democrats\u2019 House win (early Nov) \u00b7 ICJ Rohingya "
        "ruling (last week \u2014 only the 14-nation backing is 23 Nov) \u00b7 Grok lawsuits "
        "filed (Mon 23 Nov) \u00b7 CrowdStrike\u2013Zscaler deal announced (23 Nov) \u00b7 "
        "Zaporizhzhia daytime strike killing 3 (Mon 23 Nov \u2014 Tuesday\u2019s story is "
        "the separate overnight strike)."
    )
    text_block(draw, 36, dy + 24, exclusions, font(SERIF_R, 10), 952,
               leading=13)
    draw.text((36, dy + 78),
              "Leads 1\u201310 all happened on Tuesday 24 November 2026. Items "
              "11\u201338 were reported on 24 Nov; some describe events of "
              "22\u201323 Nov.",
              font=font(SANS_B, 9), fill=INK)

    # ---- footer ----
    draw.line([28, 972, 996, 972], fill=INK, width=1)
    foot = ("Original illustrations \u00b7 Sources named beside each story "
            "\u00b7 CONFIRMED = 2+ outlets \u00b7 OFFICIAL = on the record "
            "\u00b7 REPORTED = wire reports \u00b7 CLAIM = one side\u2019s "
            "account \u00b7 * = reported 24 Nov, event earlier")
    draw.text((28, 978), foot, font=font(SANS, 8), fill=GREY)

    img.save(os.path.join(HERE, "entry.png"), optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
