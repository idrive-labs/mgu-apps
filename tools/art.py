#!/usr/bin/env python3
"""art.py - the page's art, in the look of the apps: the M colours (#00A1D6, #353189, #E6242E, sharp),
slanted Saira, speed lines on a dark weave. Writes art/banner.png, art/h-*.png, art/steps.png and a
card per app (art/card-<id>.png) from apps.json, icons/<id>.png and previews/<id>.jpg.
    python3 tools/art.py          (publish.py runs it too)"""
import json, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(ROOT, 'tools', 'fonts', 'Saira.ttf')
OUT = os.path.join(ROOT, 'art')
M1, M2, M3 = (0x00, 0xA1, 0xD6), (0x35, 0x31, 0x89), (0xE6, 0x24, 0x2E)
BG, TINT = (9, 11, 16), (18, 17, 46)
TEXT2, TEXT3 = (196, 206, 226), (132, 148, 178)


def font(sz, wght=800, wdth=110):
    f = ImageFont.truetype(FONT, sz); f.set_variation_by_axes([wght, wdth]); return f


def slanted(text, sz, fill=(255, 255, 255), wght=900, wdth=112, slant=0.2, glow=None):
    f = font(sz, wght, wdth); l, t, r, b = f.getbbox(text)
    w, h = r - l + int(sz * slant) + 20, b - t + 20
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - l + int(sz * slant), 10 - t), text, font=f, fill=fill)
    im = im.transform(im.size, Image.AFFINE, (1, slant, 0, 0, 1, 0), Image.BICUBIC)
    if glow:
        pad = int(sz / 3)
        big = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); big.alpha_composite(im, (pad, pad))
        a = big.split()[3].filter(ImageFilter.GaussianBlur(sz / 7)).point(lambda v: int(v * 0.85))
        g = Image.new('RGBA', big.size, glow + (255,)); g.putalpha(a)
        out = Image.new('RGBA', big.size, (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(big); im = out
    return im


def weave(w, h):
    im = Image.new('RGB', (w, h), BG); d = ImageDraw.Draw(im)
    for x in range(-h, w, 6): d.line([(x, 0), (x + h, h)], fill=(13, 16, 22), width=2)
    return im.convert('RGBA')


def glow_left(im, box, strength=170, blur=150):
    W, H = im.size
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).ellipse(box, fill=strength); g = g.filter(ImageFilter.GaussianBlur(blur))
    return Image.composite(Image.new('RGBA', (W, H), TINT + (255,)), im, g)


def stripe(d, x, y, h, w=18, gap=6, slant=0.35):
    for i, c in enumerate((M1, M2, M3)):
        x0 = x + i * (w + gap)
        d.polygon([(x0 + h * slant, y), (x0 + w + h * slant, y), (x0 + w, y + h), (x0, y + h)], fill=c)


def speed(im, box, n=26, seed=3):
    r = random.Random(seed); lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = box
    for _ in range(n):
        y = r.uniform(y0, y1); L = r.uniform(80, 340); x = r.uniform(x0, max(x0 + 1, x1 - L))
        d.line([(x, y), (x + L, y)], fill=(255, 255, 255, int(r.uniform(16, 64))), width=r.choice((1, 1, 2)))
    im.alpha_composite(lay)


def bottom_stripe(d, W, H):
    for i, c in enumerate((M1, M2, M3)): d.rectangle((0, H - 12 + i * 4, W, H - 9 + i * 4), fill=c)


def rounded(im, r):
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=r, fill=255)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.paste(im, (0, 0), m); return out


def banner(apps):
    W, H = 1280, 520
    im = glow_left(weave(W, H), (-260, -200, 680, 720))
    speed(im, (0, 40, W, H - 40), 34)
    d = ImageDraw.Draw(im)
    stripe(d, 70, 74, 42, w=30, gap=9)
    im.alpha_composite(slanted('APPS FOR', 64, (255, 255, 255), 900, 112, 0.2), (56, 120))
    im.alpha_composite(slanted('iDRIVE 7 & 8', 116, (255, 255, 255), 900, 112, 0.2, glow=M1), (30, 172))
    d.text((74, 340), 'One source. Every app. Every update.', font=font(30, 500, 104), fill=TEXT2)
    d.text((76, 390), 'idrive-labs/mgu-apps', font=font(26, 700, 104), fill=M1)
    # a centre display, drawn: a wide rounded screen holding a grid of app tiles, the M stripe on top
    sx, sy, sw, sh = 892, 110, 350, 280
    shd = Image.new('L', (W, H), 0); ImageDraw.Draw(shd).rounded_rectangle((sx + 8, sy + 18, sx + sw + 8, sy + sh + 22), radius=28, fill=170)
    im = Image.composite(Image.new('RGBA', (W, H), (0, 0, 0, 255)), im, shd.filter(ImageFilter.GaussianBlur(20)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((sx, sy, sx + sw, sy + sh), radius=26, fill=(16, 17, 22), outline=(64, 68, 80), width=3)
    d.rounded_rectangle((sx + 14, sy + 14, sx + sw - 14, sy + sh - 14), radius=16, fill=(11, 12, 16))
    for i, c in enumerate((M1, M2, M3)): d.rectangle((sx + 34 + i * 26, sy + 32, sx + 56 + i * 26, sy + 37), fill=c)
    cols, rows, tw, th, gx, gy = 3, 2, 82, 82, 20, 20
    ox = sx + (sw - (cols * tw + (cols - 1) * gx)) // 2; oy = sy + 70
    tile = 0
    for r in range(rows):
        for c in range(cols):
            x, y = ox + c * (tw + gx), oy + r * (th + gy)
            lit = tile < 3
            d.rounded_rectangle((x, y, x + tw, y + th), radius=18, fill=(26, 28, 38) if lit else (17, 18, 24), outline=(48, 52, 64) if lit else (30, 32, 40), width=2)
            if lit:
                col = (M1, M2, M3)[tile]
                d.polygon([(x + 22, y + th - 22), (x + 42, y + 20), (x + 56, y + 20), (x + 36, y + th - 22)], fill=col)
            else:
                d.text((x + tw // 2 - 8, y + th // 2 - 20), '+', font=font(34, 500, 100), fill=(54, 58, 72))
            tile += 1
    bottom_stripe(d, W, H)
    im.convert('RGB').save(os.path.join(OUT, 'banner.png'), optimize=True)


def header(slug, title, sub):
    W, H = 1280, 128
    im = glow_left(weave(W, H), (-300, -200, 520, 300), 120, 90)
    speed(im, (600, 10, W, H - 10), 18, seed=len(slug))
    d = ImageDraw.Draw(im)
    stripe(d, 34, 30, 68, w=12, gap=6)
    im.alpha_composite(slanted(title, 58, (255, 255, 255), 900, 112, 0.2), (120, 14))
    d.text((132, 88), sub, font=font(22, 500, 104), fill=TEXT3)
    d.rectangle((0, H - 3, W, H), fill=(28, 32, 42))
    im.convert('RGB').save(os.path.join(OUT, 'h-' + slug + '.png'), optimize=True)


def steps():
    W, H = 1280, 230
    im = weave(W, H); d = ImageDraw.Draw(im)
    items = [('1', 'OPEN THE STORE', 'Settings  >  Add source'), ('2', 'ADD THE SOURCE', 'idrive-labs/mgu-apps  >  Releases'), ('3', 'INSTALL', 'Pick an app, tap Install')]
    cw = W / 3
    for i, (n, t, s) in enumerate(items):
        x = int(i * cw) + 40
        num = slanted(n, 104, (255, 255, 255), 900, 112, 0.2, glow=(M1, M2, M3)[i])
        im.alpha_composite(num, (x - 36, 34))
        d.text((x + 116, 74), t, font=font(28, 800, 106), fill=(255, 255, 255))
        d.text((x + 116, 116), s, font=font(20, 500, 100), fill=TEXT3 if i != 1 else M1)
        if i: d.line([(int(i * cw) + 6, 40), (int(i * cw) - 6, H - 40)], fill=(40, 46, 60), width=2)
    for j, c in enumerate((M1, M2, M3)): d.rectangle((0, j * 3, W, j * 3 + 2), fill=c)
    im.convert('RGB').save(os.path.join(OUT, 'steps.png'), optimize=True)


def wrap(text, f, width, d):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) > width and cur: lines.append(cur); cur = w
        else: cur = t
    if cur: lines.append(cur)
    return lines


def card(aid, a):
    W, H = 1280, 420
    im = glow_left(weave(W, H), (-200, -160, 640, 560), 150, 120)
    d = ImageDraw.Draw(im)
    # the preview on the right, fading in, framed like the car's display
    pv = os.path.join(ROOT, a.get('preview', ''))
    if a.get('preview') and os.path.exists(pv):
        p = Image.open(pv).convert('RGB'); pw = 600; ph = int(p.height * pw / p.width); p = p.resize((pw, ph), Image.LANCZOS)
        fr = Image.new('RGBA', (pw + 16, ph + 16), (0, 0, 0, 0)); ImageDraw.Draw(fr).rounded_rectangle((0, 0, pw + 15, ph + 15), radius=20, fill=(16, 17, 20, 255), outline=(58, 60, 68, 255), width=2)
        fr.alpha_composite(rounded(p.convert('RGBA'), 14), (8, 8))
        px, py = W - pw - 16 - 40, (H - ph - 16) // 2
        sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((px + 6, py + 14, px + pw + 10, py + ph + 24), radius=20, fill=160)
        im = Image.composite(Image.new('RGBA', (W, H), (0, 0, 0, 255)), im, sh.filter(ImageFilter.GaussianBlur(16)))
        im.alpha_composite(fr, (px, py)); d = ImageDraw.Draw(im)
    ic = os.path.join(ROOT, 'icons', aid + '.png')
    if os.path.exists(ic): im.alpha_composite(Image.open(ic).convert('RGBA').resize((120, 120), Image.LANCZOS), (48, 46))
    im.alpha_composite(slanted(a['title'].upper(), 64, (255, 255, 255), 900, 112, 0.2, glow=M1), (174, 50))
    d.text((190, 126), a.get('tagline', ''), font=font(23, 600, 104), fill=M1)
    f = font(22, 400, 100)
    for i, l in enumerate(wrap(a.get('card_description', a['description']), f, 440, d)[:4]): d.text((50, 196 + i * 34), l, font=f, fill=TEXT2)   # the card's own shorter text, else the Store's
    # chips: the head units, the version
    x = 50
    for txt, col in [('iDRIVE 7', M2) if 'ID7' in a.get('mguHmi', []) else (None, None), ('iDRIVE 8', M2) if 'ID8' in a.get('mguHmi', []) else (None, None), ('v' + str(a.get('version') or ''), M3)]:
        if not txt: continue
        cf = font(19, 800, 106); tw = d.textlength(txt, font=cf)
        d.polygon([(x + 8, 352), (x + tw + 30, 352), (x + tw + 22, 386), (x, 386)], fill=col)
        d.text((x + 15, 357), txt, font=cf, fill=(255, 255, 255)); x += int(tw) + 42
    bottom_stripe(d, W, H)
    im.convert('RGB').save(os.path.join(OUT, 'card-' + aid + '.png'), optimize=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    apps = json.load(open(os.path.join(ROOT, 'apps.json')))
    banner([k for k, a in apps.items() if a.get('kind') != 'tool'])   # a tool comes with its app
    header('apps', 'THE APPS', 'Every app of this source: tap one for its page')
    header('add', 'ADD THE SOURCE', 'Once, in the MGU Store on your car')
    steps()
    for aid, a in apps.items():
        if a.get('artifact') and a.get('kind') != 'tool': card(aid, a)
    print('art in art/')


if __name__ == '__main__':
    main()
