from fontTools.ttLib import TTFont
from io import BytesIO


def convert_to_woff(woff2):
    b = BytesIO()
    with open(woff2, "rb") as f:
        ttf = TTFont(f)
    ttf.flavor = "woff"
    ttf.save(b)
    b.seek(0)
    return b.read()
