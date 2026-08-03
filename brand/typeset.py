"""Typeset the VENEER headline onto the generated banner.

Type is rendered locally rather than asked for from the image model, so the
lettering is actually sharp and correctly spelled at every size.
"""
from PIL import Image, ImageDraw, ImageFont

HN = "/System/Library/Fonts/Supplemental/HelveticaNeue.ttc"
LIGHT, ULTRALIGHT, MEDIUM, THIN = 7, 5, 10, 12
GOLD = (198, 160, 94)
WARM_WHITE = (238, 234, 226)
GREY = (150, 148, 145)

SRC = "banner_raw.png"
WORDMARK = "VENEER"
LINE1 = "Same facts. Different clothes."
LINE2 = "A 65-point swing in what LLM judges prefer."


def tracked(draw, xy, text, font, fill, track):
    """Draw text with letter-spacing (PIL has no tracking of its own)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track
    return x - track


def tracked_width(draw, text, font, track):
    return sum(draw.textlength(c, font=font) for c in text) + track * (len(text) - 1)


def compose(out, size, box, wm_size, l1_size, l2_size, track, rule=True, gap=None,
            x_frac=0.0):
    """box = (left, top) of the text block in the OUTPUT image, in px."""
    im = Image.open(SRC).convert("RGB")
    tw, th = size
    # cover-crop the source to the target aspect, anchored left so the foil stays
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    im = im.resize((round(sw * scale), round(sh * scale)), Image.LANCZOS)
    # x_frac slides the crop window right, so tighter aspects keep dark negative
    # space on the right for the type instead of putting it on the bright foil
    left = round((im.width - tw) * x_frac)
    top = (im.height - th) // 2
    im = im.crop((left, top, left + tw, top + th))

    d = ImageDraw.Draw(im)
    f_wm = ImageFont.truetype(HN, wm_size, index=ULTRALIGHT)
    f_l1 = ImageFont.truetype(HN, l1_size, index=LIGHT)
    f_l2 = ImageFont.truetype(HN, l2_size, index=THIN)

    x, y = box
    g = gap or round(wm_size * 0.55)
    tracked(d, (x, y), WORDMARK, f_wm, WARM_WHITE, track)
    y += wm_size + g
    if rule:
        w = tracked_width(d, WORDMARK, f_wm, track)
        d.line([(x, y), (x + w, y)], fill=GOLD, width=max(1, round(tw / 900)))
        y += g
    d.text((x, y), LINE1, font=f_l1, fill=GOLD)
    y += round(l1_size * 1.65)
    d.text((x, y), LINE2, font=f_l2, fill=GREY)
    im.save(out, quality=96)
    print(f"{out}  {im.size}")


# Kaggle dataset cover / HF card / wide hero — native 3:1
compose("veneer_banner_3x1.png", (2172, 724), (1020, 250), 132, 40, 34, 26)
# GitHub social preview — 1280x640 (2:1); text sits lower-right of the curl
compose("veneer_social_1280x640.png", (1280, 640), (660, 190), 92, 27, 23, 18, x_frac=0.62)
# X / LinkedIn post card — 1600x900 (16:9)
compose("veneer_card_1600x900.png", (1600, 900), (800, 250), 104, 30, 26, 20, x_frac=0.70)
