#!/usr/bin/env python3
"""Render entry-v4.png for the 24 November 2026 news-image entry.

Offline composition script (PIL only). Deterministic: no clock, no
randomness, no network. Run from the repo root:
    python3 build.py
Produces entry.png (1024x1024, <= 1 MiB) next to this file.

Design (v4 HYBRID): v3 magazine cover — one huge vivid Hormuz hero
with overlaid headline, dusk-orange sky, embers — PLUS v2's strengths:
a proper Sanofi lead image panel, Nepal + Hormuz secondary image
panels with captions, and the honest markets % bar strip. Stories
3-10 as a 3-column numbered index, small map (leads 1-10 pinned),
tail list, DATE CHECK box. Produces entry-v4.png (1024x1024,
<= 1 MiB). v2/v3 files untouched.

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


# ---------------- v3 composition: magazine cover ----------------
# v3 is a THIRD, distinct composition (v1: 3 equal heroes + card grid;
# v2: dominant Sanofi lead + timeline rail + market bars). v3 is a
# photo-led magazine cover: one HUGE Hormuz hero (most dramatic scene)
# with the headline overlaid on it, Sanofi lead as a strip below,
# stories 3-10 as a 3-column numbered index, small map + tail, DATE
# CHECK. Same 38 stories, same numbering, same date rule as v1/v2.
# Visuals are deliberately MORE "rame": hero art is saturation /
# contrast boosted and seeded with glowing embers over the flames.

def vivid(img, color=1.45, contrast=1.25, bright=1.06):
    from PIL import ImageEnhance
    img = ImageEnhance.Color(img).enhance(color)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Brightness(img).enhance(bright)
    return img


def cover_crop(img, w, h, dy_bias=0):
    scale = max(w / img.size[0], h / img.size[1])
    pic = img.resize((round(img.size[0] * scale),
                      round(img.size[1] * scale)), Image.LANCZOS)
    left = (pic.size[0] - w) // 2
    top = max(0, min((pic.size[1] - h) // 2 + dy_bias,
                     pic.size[1] - h))
    return pic.crop((left, top, left + w, top + h))


def trim_lines(draw, deck, fnt, width, max_lines=2):
    lines = wrap(draw, deck, fnt, width)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines[-1] and draw.textlength(lines[-1] + " \u2026",
                                        font=fnt) > width:
        lines[-1] = lines[-1].rsplit(" ", 1)[0]
    lines[-1] = lines[-1] + " \u2026"
    return lines


def index_deck(draw, deck, src, max_w):
    """Trim a one-line deck so it plus its grey source fits max_w."""
    f_deck, f_src = font(SERIF_R, 9), font(SANS, 8)
    src_txt = " (" + src + ")"
    d, trimmed = deck, False
    while d and " " in d and draw.textlength(d, font=f_deck) + \
            draw.textlength(src_txt, font=f_src) > max_w:
        d = d.rsplit(" ", 1)[0]
        trimmed = True
    return (d + " …" if trimmed else d), src_txt


def main():
    import random
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, W - 1, H - 1], outline=RULE, width=2)

    # ---- masthead: centred nameplate + red date band (v3 wording) ----
    draw.text((28, 8), "No. 24 \u00b7 TUESDAY EDITION",
              font=font(SANS_B, 9), fill=NAVY)
    folio_r = "ONE DAY \u00b7 ONE PAGE \u00b7 38 STORIES"
    draw.text((996 - draw.textlength(folio_r, font=font(SANS_B, 9)), 8),
              folio_r, font=font(SANS_B, 9), fill=NAVY)
    draw.line([28, 22, 996, 22], fill=INK, width=1)
    name = "THE WORLD IN ONE DAY"
    draw.text(((1024 - draw.textlength(name, font=font(SERIF, 44))) / 2,
               26), name, font=font(SERIF, 44), fill=INK)
    draw.line([28, 74, 996, 74], fill=INK, width=3)
    draw.line([28, 78, 996, 78], fill=INK, width=1)
    draw.rectangle([28, 84, 996, 110], fill=DARKRED)
    draw.text((36, 90), "TUESDAY 24 NOVEMBER 2026",
              font=font(SERIF, 18), fill=(255, 255, 255))
    band_r = "COVER: HORMUZ IN FLAMES \u00b7 7 REGIONS"
    draw.text((996 - draw.textlength(band_r, font=font(SANS_B, 10)), 93),
              band_r, font=font(SANS_B, 10), fill=(255, 255, 255))

    # ---- cover hero: Hormuz, huge, vivid, embers (No. 2) ----
    hx, hy, hw, hh = 28, 118, 968, 242
    hero = vivid(art_hormuz(), color=1.5, contrast=1.28, bright=1.06)
    hero = cover_crop(hero, hw, hh, dy_bias=-14)
    # glowing embers drifting over the flames/smoke (seeded = deterministic)
    ed = ImageDraw.Draw(hero)
    rng = random.Random(20261124)
    for _ in range(70):
        ex = rng.randint(20, hw - 20)
        ey = rng.randint(int(hh * 0.30), int(hh * 0.92))
        er = rng.choice([1, 1, 2, 2, 3])
        col = rng.choice([(255, 190, 70), (255, 220, 120),
                          (255, 120, 30), (255, 240, 180)])
        ed.ellipse([ex - er, ey - er, ex + er, ey + er], fill=col)
    img.paste(hero, (hx, hy))
    draw.rectangle([hx, hy, hx + hw, hy + hh], outline=RULE, width=1)
    draw.rectangle([hx + 2, hy + 2, hx + hw - 2, hy + hh - 2],
                   outline=GOLD, width=1)
    # dark scrim over the bottom third so the overlaid headline reads
    base = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for i in range(120):
        a = int(190 * (i / 119) ** 1.6)
        od.line([hx, hy + hh - 120 + i, hx + hw, hy + hh - 120 + i],
                fill=(10, 8, 8, a))
    base.alpha_composite(ov)
    img = base.convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.rectangle([hx, hy, hx + hw, hy + hh], outline=RULE, width=1)
    # cover badge + kicker
    draw.rectangle([hx + 12, hy + 12, hx + 92, hy + 36], fill=RED)
    draw.text((hx + 20, hy + 17), "No. 2", font=font(SERIF, 15),
              fill=(255, 255, 255))
    draw.text((hx + 100, hy + 18), "STRAIT OF HORMUZ \u00b7 THE GULF",
              font=font(SANS_B, 11), fill=(255, 255, 255))
    draw.text((hx + 14, hy + hh - 96),
              "Three tankers ablaze in the Strait of Hormuz",
              font=font(SERIF, 32), fill=(255, 255, 255))
    text_block(draw, hx + 14, hy + hh - 56,
               "Tehran says three tankers caught fire after hitting naval "
               "mines; the US rules out talks until seven conditions are met.",
               font(SERIF_R, 13), hw - 28, fill=(238, 232, 218),
               leading=16)
    draw.text((hx + 14, hy + hh - 20), "(Horizon) \u00b7 CLAIM",
              font=font(SANS, 9), fill=(210, 200, 180))

    # ---- markets chart strip (v2): honest % bars ----
    # % moves only; prices are text chips (different units, no bars).
    # Nvidia +31% is the scale max; all bars share one linear scale.
    draw.rectangle([28, 368, 996, 428], outline=RULE, width=1,
                   fill=(238, 228, 204))
    draw.text((36, 372),
              "MARKETS IN ONE GLANCE — % MOVES REPORTED 24 NOV",
              font=font(SANS_B, 10), fill=INK)
    chip = "BRENT $86.7 · GOLD $3,620 · BITCOIN $60,400 · GAS +12%"
    draw.text((996 - draw.textlength(chip, font=font(SANS, 8)), 374),
              chip, font=font(SANS, 8), fill=GREY)
    bars_l = [("NVIDIA", "+31%", 31.0), ("NASDAQ", "+6.51%", 6.51),
              ("KOSPI", "+6.3%", 6.3)]
    bars_r = [("S&P 500", "+4.73%", 4.73), ("NIKKEI", "+3.91%", 3.91),
              ("DOW", "+3.01%", 3.01)]
    for col_x, items in ((36, bars_l), (516, bars_r)):
        for j, (lab, val, pct) in enumerate(items):
            by = 384 + j * 13
            draw.text((col_x, by), lab, font=font(SANS_B, 8), fill=INK)
            bx = col_x + 64
            bw = max(5, round(pct / 31.0 * 330))
            draw.rectangle([bx, by + 1, bx + bw, by + 9], fill=GREEN)
            draw.text((bx + bw + 5, by - 1), val, font=font(SERIF, 11),
                      fill=INK)

    # ---- lead story: No. 1 Sanofi, proper image panel (v2 strength) ----
    # v3 shrank Sanofi to a 220x70 thumb; v4 restores it as a real
    # image panel — fit-height on a teal matte (v2) so $41bn, the
    # chart, the pills and the coins all stay in frame.
    ly = 436
    draw.rectangle([28, ly, 996, ly + 92], outline=RULE, width=1,
                   fill=(238, 228, 204))
    draw.rectangle([28, ly, 34, ly + 92], fill=GOLD)
    limg = vivid(art_sanofi(), color=1.35, contrast=1.15, bright=1.03)
    draw.rectangle([35, ly + 1, 335, ly + 91], fill=(16, 74, 84))
    scale = 90 / limg.size[1]
    pic = limg.resize((round(limg.size[0] * scale), 90), Image.LANCZOS)
    img.paste(pic, (35 + (300 - pic.size[0]) // 2, ly + 1))
    draw.rectangle([35, ly + 81, 335, ly + 91], fill=(10, 8, 8))
    draw.text((40, ly + 82),
              "Chart, pills and coins — the $41bn deal in one picture.",
              font=font(SERIF_I, 8), fill=(238, 232, 218))
    draw.rectangle([35, ly + 1, 54, ly + 18], fill=RED)
    draw.text((40, ly + 3), "1", font=font(SANS_B, 10),
              fill=(255, 255, 255))
    tx = 348
    draw.text((tx, ly + 4), "LEAD STORY — No. 1",
              font=font(SANS_B, 9), fill=RED)
    draw.text((tx, ly + 16), "Sanofi buys Insmed for $41 billion",
              font=font(SERIF, 21), fill=INK)
    draw.line([tx, ly + 46, 996, ly + 46], fill=GOLD, width=2)
    text_block(draw, tx, ly + 50,
               "French drugmaker agrees $175 a share in cash for US "
               "biotech Insmed — the biggest biotech deal in nearly "
               "three years; Sanofi shares rose ~4.5%.",
               font(SERIF_R, 11), 648, leading=13)
    draw.text((tx, ly + 76), "$175 a share  ·  Sanofi +4.5%",
              font=font(SERIF, 13), fill=RED)
    sx = tx + draw.textlength("$175 a share  ·  Sanofi +4.5%",
                              font=font(SERIF, 13))
    draw.text((sx + 12, ly + 78), "(Reuters) · CONFIRMED",
              font=font(SANS, 8), fill=GREY)

    # ---- secondary image panels: Nepal + Hormuz, strong again ----
    # v3 dropped Nepal's picture entirely and left Sanofi a thumb;
    # v4 brings both back as real image panels with captions (v2's
    # strength), under the v3 cover. Hormuz returns with a different
    # angle — the talks angle — so it does not repeat the cover.
    secondaries = [
        (3, art_quake(), "TAPLEJUNG · NEPAL",
         "5.6-magnitude quake shakes Nepal border",
         "Struck at ~07:02 IST, felt across Sikkim, north Bengal, "
         "Bhutan and Bangladesh; no casualties reported.",
         "CONFIRMED", "The Hindu",
         "Himalayan peaks and the red seismograph line."),
        (2, art_hormuz(), "STRAIT OF HORMUZ · THE GULF",
         "US rules out talks until seven conditions met",
         "Washington says no talks with Tehran until its seven "
         "conditions are met; Tehran blames naval mines for the fires.",
         "CLAIM", "Horizon", "Flames over the Gulf at dusk."),
    ]
    for k, (num, art, place, head, deck, conf, src, cap) in \
            enumerate(secondaries):
        x = 28 + k * 490
        y = 536
        draw.rectangle([x, y, x + 478, y + 80], outline=RULE, width=1)
        pic = vivid(art, color=1.5, contrast=1.28, bright=1.06) \
            if num == 2 else vivid(art, color=1.3, contrast=1.15,
                                   bright=1.03)
        pic = cover_crop(pic, 180, 78, dy_bias=-8 if num == 2 else 0)
        img.paste(pic, (x + 1, y + 1))
        draw.rectangle([x + 1, y + 69, x + 181, y + 79], fill=(10, 8, 8))
        draw.text((x + 5, y + 70), cap, font=font(SERIF_I, 7),
                  fill=(238, 232, 218))
        draw.rectangle([x + 1, y + 1, x + 20, y + 18], fill=RED)
        draw.text((x + 6, y + 3), str(num), font=font(SANS_B, 10),
                  fill=(255, 255, 255))
        tx, tw = x + 190, 478 - 190 - 8
        draw.text((tx, y + 3), place, font=font(SANS_B, 8), fill=NAVY)
        yy = y + 14
        for line in trim_lines(draw, head, font(SERIF, 14), tw,
                               max_lines=2):
            draw.text((tx, yy), line, font=font(SERIF, 14), fill=INK)
            yy += 15
        for line in trim_lines(draw, deck, font(SERIF_R, 10), tw,
                               max_lines=2):
            draw.text((tx, yy), line, font=font(SERIF_R, 10),
                      fill=(64, 58, 46))
            yy += 11
        draw.text((tx, y + 69), "(%s) · %s" % (src, conf),
                  font=font(SANS, 8), fill=GREY)

    # ---- the day in ten: 3-column numbered index (Nos. 3-10) ----
    draw.text((28, 624), "THE DAY IN TEN",
              font=font(SANS_B, 11), fill=INK)
    draw.text((996 - draw.textlength("Nos. 3\u201310",
                                     font=font(SANS_B, 10)), 625),
              "Nos. 3\u201310", font=font(SANS_B, 10), fill=RED)
    cells = [
        (3, "NEPAL", "5.6-magnitude quake shakes Nepal border",
         "Struck at ~07:02 IST, felt across Sikkim, north Bengal, "
         "Bhutan and Bangladesh; no casualties reported.", "The Hindu"),
        (4, "GAZA", "Israeli strikes kill at least six in Gaza",
         "Airstrikes killed at least six Palestinians, incl. two police "
         "officers.", "Reuters"),
        (5, "VATICAN", "Pope diary: \u2018I saw the devil three times\u2019",
         "Vatican published excerpts of the late pontiff\u2019s private "
         "diary (1992\u20132024).", "Guardian"),
        (6, "UAE", "Bus\u2013truck crash in UAE kills 13",
         "A bus carrying 41 people hit a truck on Al Watan Road, Ras Al "
         "Khaimah; 14 injured.", "Khaleej Times"),
        (7, "PACIFIC", "Solomon Islands scraps China security pact",
         "Honiara will not renew its 2022 pact; a new treaty with "
         "Australia follows.", "ABC News"),
        (8, "BANGLADESH", "Hasina plans 16 Dec return to Bangladesh",
         "The ousted PM plans to return from exile in India; Dhaka says "
         "she faces arrest.", "Reuters"),
        (9, "UKRAINE",
         "Russian strike kills 2, wounds 22 in Zaporizhzhia",
         "Overnight attack partly destroyed a five-storey residential "
         "building.", "Reuters"),
        (10, "GERMANY", "Germany first into Ukraine\u2019s Delta system",
         "Defence ministers signed a letter of intent in Berlin; Germany "
         "will co-develop it.", "Kyiv Independent"),
    ]
    col_x = [28, 356, 684]
    col_w = 312
    for i, (num, tag, head, deck, src) in enumerate(cells):
        col, row = divmod(i, 3)
        cx, cy = col_x[col], 644 + row * 52
        # big numeral
        draw.text((cx, cy + 2), str(num), font=font(SERIF, 24),
                  fill=RED)
        tx2, tw2 = cx + 34, col_w - 34
        draw.text((tx2, cy + 3), tag, font=font(SANS_B, 8), fill=NAVY)
        yy = cy + 14
        for line in trim_lines(draw, head, font(SERIF, 12), tw2,
                               max_lines=2):
            draw.text((tx2, yy), line, font=font(SERIF, 12), fill=INK)
            yy += 14
        d, src_txt = index_deck(draw, deck, src, tw2)
        draw.text((tx2, cy + 41), d, font=font(SERIF_R, 9),
                  fill=(64, 58, 46))
        draw.text((tx2 + draw.textlength(d, font=font(SERIF_R, 9)),
                   cy + 41), src_txt, font=font(SANS, 8), fill=GREY)
        if col < 2:
            draw.line([cx + col_w + 8, cy + 4, cx + col_w + 8,
                       cy + 48], fill=LIGHT, width=1)
    # 9th cell: pointer to the tail list
    cx, cy = col_x[2], 644 + 2 * 52
    draw.text((cx, cy + 2), "28", font=font(SERIF, 24), fill=RED)
    draw.text((cx + 48, cy + 4), "MORE INSIDE",
              font=font(SANS_B, 10), fill=INK)
    text_block(draw, cx + 48, cy + 18,
               "More stories reported Tuesday — Nos. 11–38 in the "
               "list below.",
               font(SERIF_R, 10), col_w - 48, fill=(64, 58, 46),
               leading=12)
    draw.text((cx + 48, cy + 44), "Nos. 11–38 ↓",
              font=font(SANS_B, 9), fill=RED)
    draw.line([28, 808, 996, 808], fill=INK, width=1)

    # ---- map (small) + tail list (3 cols) ----
    draw.text((28, 816), "WHERE IT HAPPENED — LEADS 1–10",
              font=font(SANS_B, 10), fill=INK)
    draw.text((372, 816), "ALSO ON TUESDAY — 28 MORE STORIES",
              font=font(SANS_B, 10), fill=INK)
    mx, my, mw, mh = 28, 828, 330, 76
    draw.rectangle([mx, my, mx + mw, my + mh], outline=RULE, width=1,
                   fill=(238, 228, 204))
    polys = [
        [(8, 20), (28, 12), (38, 18), (36, 30), (28, 38), (16, 36),
         (10, 28)],
        [(28, 48), (36, 46), (40, 58), (34, 72), (29, 60)],
        [(46, 14), (56, 12), (60, 20), (54, 26), (47, 24)],
        [(46, 32), (60, 30), (64, 44), (56, 60), (49, 48)],
        [(60, 12), (92, 10), (96, 24), (88, 36), (76, 32), (64, 24)],
        [(86, 58), (96, 56), (97, 64), (88, 66)],
    ]
    # v3: small map (330x84) — pin ONLY the ten leads; all 37 pins
    # turned the v2-sized map into one red blob at this size.
    for gy in range(8, 72, 4):
        for gx in range(3, 98, 3):
            if any(point_in_poly(gx, gy, p) for p in polys):
                draw.ellipse([mx + gx / 100 * mw - 1.2,
                              my + gy / 100 * mh - 1.2,
                              mx + gx / 100 * mw + 1.2,
                              my + gy / 100 * mh + 1.2],
                             fill=(150, 128, 90))
    # pins: leads 1-10 only — all 37 pins turned the small map into
    # one red blob; No. 38 (black hole) has no place.
    pins = [(1, 48, 27), (2, 60, 41), (3, 73, 36), (4, 56, 36),
            (5, 54, 30), (6, 64, 44), (7, 94, 60), (8, 77, 40),
            (9, 58, 23), (10, 46, 14)]
    for num, px, py in pins:
        cx2, cy2 = mx + px / 100 * mw, my + py / 100 * mh
        draw.ellipse([cx2 - 5, cy2 - 5, cx2 + 5, cy2 + 5], fill=RED,
                     outline=(255, 255, 255), width=1)
        tw = draw.textlength(str(num), font=font(SANS_B, 6))
        draw.text((cx2 - tw / 2, cy2 - 4), str(num),
                  font=font(SANS_B, 6), fill=(255, 255, 255))
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
    for i, (num, txt) in enumerate(tail):
        col, row = divmod(i, 10)
        x = 372 + col * 212
        y = 828 + row * 8
        draw.text((x, y), "%d" % num, font=font(SANS_B, 7), fill=RED)
        draw.text((x + 15, y), txt, font=font(SANS, 7), fill=INK)

    # ---- date check ----
    dy = 912
    draw.rectangle([28, dy, 996, dy + 64], outline=RED, width=2)
    draw.text((36, dy + 5), "DATE CHECK \u2014 HELD OVER, NOT TUESDAY",
              font=font(SANS_B, 10), fill=RED)
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
    text_block(draw, 36, dy + 20, exclusions, font(SERIF_R, 9), 952,
               leading=11)
    draw.text((36, dy + 54),
              "Leads 1\u201310 all happened on Tuesday 24 November 2026.",
              font=font(SANS_B, 8), fill=INK)

    # ---- footer ----
    draw.line([28, 984, 996, 984], fill=INK, width=1)
    foot = ("Original illustrations \u00b7 Sources named beside each story "
            "\u00b7 CONFIRMED = 2+ outlets \u00b7 OFFICIAL = on the record "
            "\u00b7 REPORTED = wire reports \u00b7 CLAIM = one side\u2019s "
            "account \u00b7 * = reported 24 Nov, event earlier")
    draw.text((28, 989), foot, font=font(SANS, 8), fill=GREY)

    img.save(os.path.join(HERE, "entry-v4.png"), optimize=True)
    print("wrote entry-v4.png", img.size)


if __name__ == "__main__":
    main()
