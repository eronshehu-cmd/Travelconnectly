"""Render a 1200x630 social share image: python og_image.py <out.jpg> <bg photo> <eyebrow> <title line1> <title line2> <sub>"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

out, bg_path, eyebrow, t1, t2, sub = sys.argv[1:7]
W, H = 1200, 630
NAVY = (13, 27, 42)
TEAL = (63, 217, 199)
AMBER = (244, 168, 37)
LIGHT = (237, 242, 247)
MUTED = (160, 180, 200)

bold = lambda s: ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", s)
reg = lambda s: ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", s)
mono = lambda s: ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", s)

img = Image.new("RGB", (W, H), NAVY)

# Photo on the right, fading into navy on the left.
photo = Image.open(bg_path).convert("RGB")
scale = H / photo.height
photo = photo.resize((int(photo.width * scale), H))
left = max(0, (photo.width - 620) // 2)
photo = photo.crop((left, 0, left + 620, H))
img.paste(photo, (W - 620, 0))
fade = Image.new("L", (W, H), 0)
fd = ImageDraw.Draw(fade)
for x in range(W):
    if x < W - 620:
        a = 255
    else:
        a = int(255 * max(0.35, 1 - (x - (W - 620)) / 520))
    fd.line([(x, 0), (x, H)], fill=a)
img = Image.composite(Image.new("RGB", (W, H), NAVY), img, fade)

d = ImageDraw.Draw(img)
# Logo mark (shield + globe)
d.polygon([(80, 70), (116, 88), (116, 115), (98, 142), (80, 150), (62, 142), (44, 115), (44, 88)], outline=TEAL, width=4)
d.ellipse([62, 90, 98, 126], outline=AMBER, width=3)
d.line([(62, 108), (98, 108)], fill=AMBER, width=2)
d.text((134, 86), "Travel", font=bold(40), fill=LIGHT)
tw = d.textlength("Travel", font=bold(40))
d.text((134 + tw, 86), "Connectly", font=bold(40), fill=AMBER)

d.line([(64, 236), (94, 236)], fill=TEAL, width=2)
d.text((108, 224), eyebrow, font=mono(24), fill=TEAL)
d.text((60, 262), t1, font=bold(64), fill=LIGHT)
d.text((60, 340), t2, font=bold(64), fill=TEAL)
d.text((62, 440), sub, font=reg(28), fill=MUTED)
d.text((62, 548), "travelconnectly.com", font=mono(24), fill=MUTED)

img.save(out, "JPEG", quality=86, optimize=True, progressive=True)
print("wrote", out, img.size)
