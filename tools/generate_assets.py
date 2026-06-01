from __future__ import annotations

import math
import random
import wave
from array import array
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "assets" / "images"
AUDIO = ROOT / "assets" / "audio"
W, H = 1280, 720


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def add_noise(img: Image.Image, strength: int = 24, contrast: float = 0.92) -> Image.Image:
    noise = Image.effect_noise(img.size, strength).convert("L")
    colored = Image.merge("RGB", (noise, noise, noise))
    img = Image.blend(img.convert("RGB"), colored, 0.10)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(0.82)
    small = img.resize((W // 2, H // 2), Image.Resampling.BILINEAR)
    img = small.resize((W, H), Image.Resampling.NEAREST)
    return img.filter(ImageFilter.GaussianBlur(0.25))


def draw_wallpaper(draw: ImageDraw.ImageDraw, polygon: list[tuple[int, int]], offset: int = 0) -> None:
    color_a = (174, 151, 68)
    color_b = (127, 112, 58)
    for x in range(-80 + offset, W + 120, 70):
        draw.line([(x, 0), (x + 110, H)], fill=color_b, width=2)
    for y in range(20, H, 42):
        draw.line([(0, y), (W, y + 18)], fill=(151, 132, 64), width=1)
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    md.polygon(polygon, fill=255)
    overlay = Image.new("RGB", (W, H), color_a)
    od = ImageDraw.Draw(overlay)
    for x in range(-60 + offset, W + 120, 70):
        od.line([(x, 0), (x + 110, H)], fill=color_b, width=2)
    for y in range(20, H, 42):
        od.line([(0, y), (W, y + 18)], fill=(151, 132, 64), width=1)
    return overlay, mask


def composite_polygon(base: Image.Image, polygon: list[tuple[int, int]], color: tuple[int, int, int], pattern_offset: int = 0) -> None:
    draw = ImageDraw.Draw(base)
    draw.polygon(polygon, fill=color)
    overlay, mask = draw_wallpaper(draw, polygon, pattern_offset)
    base.paste(Image.blend(base, overlay, 0.28), (0, 0), mask)


def fluorescent(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=4, fill=(226, 210, 113), outline=(116, 103, 61), width=2)
    draw.rectangle((x + 7, y + 4, x + w - 7, y + h - 4), fill=(254, 238, 153))
    for r in range(8, 40, 8):
        draw.ellipse((x - r, y - r, x + w + r, y + h + r), outline=(236, 216, 115), width=1)


def carpet(draw: ImageDraw.ImageDraw, polygon: list[tuple[int, int]], seed: int) -> None:
    random.seed(seed)
    draw.polygon(polygon, fill=(100, 88, 51))
    for _ in range(1300):
        x = random.randrange(0, W)
        y = random.randrange(410, H)
        shade = random.randrange(56, 120)
        draw.point((x, y), fill=(shade + 20, shade + 8, max(20, shade - 24)))
    for y in range(430, H, 42):
        draw.line([(0, y), (W, y + 24)], fill=(70, 61, 37), width=1)


def base_room(seed: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    random.seed(seed)
    img = Image.new("RGB", (W, H), (159, 139, 66))
    draw = ImageDraw.Draw(img)
    ceiling = [(0, 0), (W, 0), (980, 250), (300, 250)]
    floor = [(0, H), (W, H), (940, 430), (340, 430)]
    left_wall = [(0, 0), (305, 250), (340, 430), (0, H)]
    right_wall = [(W, 0), (980, 250), (940, 430), (W, H)]
    back_wall = [(305, 250), (980, 250), (940, 430), (340, 430)]
    draw.polygon(ceiling, fill=(133, 121, 71))
    composite_polygon(img, left_wall, (155, 137, 70), 11)
    composite_polygon(img, right_wall, (147, 130, 66), 37)
    composite_polygon(img, back_wall, (170, 150, 73), 4)
    carpet(draw, floor, seed + 99)
    for x in range(250, 980, 180):
        draw.line([(x, 0), (x + random.randint(-80, 80), 252)], fill=(93, 86, 56), width=2)
    for y in (70, 152):
        draw.line([(0, y), (W, y + random.randint(-20, 20))], fill=(100, 92, 58), width=2)
    fluorescent(draw, 520, 72, 210, 28)
    return img, draw


def draw_doorway(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], dark: bool = True) -> None:
    x1, y1, x2, y2 = box
    draw.rectangle((x1 - 8, y1 - 8, x2 + 8, y2 + 8), fill=(92, 79, 45))
    fill = (20, 19, 16) if dark else (83, 78, 62)
    draw.rectangle((x1, y1, x2, y2), fill=fill)
    draw.line((x1, y1, x2, y1), fill=(221, 193, 91), width=2)


def scene_start() -> Image.Image:
    img, draw = base_room(10)
    draw_doorway(draw, (895, 210, 1125, 620), True)
    draw.rectangle((160, 258, 310, 350), fill=(145, 124, 60), outline=(94, 80, 43), width=5)
    draw.line((192, 314, 268, 281), fill=(80, 65, 39), width=2)
    return add_noise(img, 28)


def scene_hallway() -> Image.Image:
    img = Image.new("RGB", (W, H), (151, 133, 65))
    draw = ImageDraw.Draw(img)
    center = [(455, 180), (825, 180), (745, 535), (535, 535)]
    left = [(0, 0), (455, 180), (535, 535), (0, H)]
    right = [(W, 0), (825, 180), (745, 535), (W, H)]
    ceiling = [(0, 0), (W, 0), (825, 180), (455, 180)]
    floor = [(0, H), (W, H), (745, 535), (535, 535)]
    draw.polygon(ceiling, fill=(125, 113, 69))
    composite_polygon(img, left, (152, 135, 69), 7)
    composite_polygon(img, right, (146, 128, 64), 39)
    composite_polygon(img, center, (168, 149, 75), 14)
    carpet(draw, floor, 28)
    draw.rectangle((568, 252, 712, 502), fill=(18, 17, 14))
    for y in range(215, 505, 65):
        draw.line((410, y, 860, y), fill=(98, 88, 52), width=1)
    fluorescent(draw, 572, 66, 160, 24)
    fluorescent(draw, 600, 142, 100, 15)
    return add_noise(img, 30, 0.88)


def scene_junction() -> Image.Image:
    img, draw = base_room(44)
    draw_doorway(draw, (90, 205, 310, 645), True)
    draw_doorway(draw, (900, 235, 1140, 632), True)
    draw.rectangle((520, 268, 742, 386), fill=(150, 130, 64), outline=(94, 80, 41), width=4)
    for i in range(9):
        y = 282 + i * 10
        draw.line((540, y, 724, y + random.randint(-3, 3)), fill=(76, 66, 44), width=1)
    fluorescent(draw, 210, 90, 180, 22)
    fluorescent(draw, 820, 86, 160, 20)
    return add_noise(img, 31, 0.87)


def scene_sign() -> Image.Image:
    img, draw = base_room(61)
    draw_doorway(draw, (40, 200, 260, 642), True)
    draw.rectangle((538, 158, 835, 276), fill=(78, 38, 30), outline=(35, 24, 20), width=6)
    draw.text((580, 178), "EXIT", fill=(232, 205, 120), font=font(62))
    draw.polygon([(805, 218), (930, 218), (930, 186), (1030, 236), (930, 286), (930, 252), (805, 252)], fill=(105, 31, 25))
    draw.rectangle((472, 350, 642, 428), fill=(161, 139, 69), outline=(94, 80, 41), width=4)
    draw.text((488, 365), "NO MAP", fill=(53, 47, 33), font=font(26))
    return add_noise(img, 34, 0.86)


def scene_door() -> Image.Image:
    img, draw = base_room(80)
    draw.rectangle((493, 158, 790, 655), fill=(83, 76, 58), outline=(38, 34, 29), width=10)
    draw.rectangle((526, 196, 758, 635), fill=(58, 55, 48), outline=(102, 90, 61), width=3)
    draw.ellipse((715, 415, 736, 436), fill=(161, 139, 70), outline=(40, 33, 22))
    draw.rectangle((524, 106, 760, 148), fill=(24, 43, 29), outline=(16, 25, 18), width=5)
    draw.text((590, 109), "EXIT", fill=(104, 206, 122), font=font(34))
    draw.line((641, 158, 638, 655), fill=(29, 26, 21), width=3)
    return add_noise(img, 36, 0.84)


def scene_other() -> Image.Image:
    img = Image.new("RGB", (W, H), (64, 64, 58))
    draw = ImageDraw.Draw(img)
    ceiling = [(0, 0), (W, 0), (980, 210), (300, 210)]
    floor = [(0, H), (W, H), (930, 455), (350, 455)]
    back = [(300, 210), (980, 210), (930, 455), (350, 455)]
    left = [(0, 0), (300, 210), (350, 455), (0, H)]
    right = [(W, 0), (980, 210), (930, 455), (W, H)]
    draw.polygon(ceiling, fill=(58, 56, 50))
    composite_polygon(img, left, (103, 93, 61), 19)
    composite_polygon(img, right, (83, 79, 61), 49)
    composite_polygon(img, back, (111, 98, 63), 9)
    carpet(draw, floor, 118)
    draw.rectangle((610, 230, 700, 450), fill=(8, 8, 8))
    fluorescent(draw, 520, 70, 210, 23)
    draw.text((474, 520), "LEVEL 0", fill=(51, 45, 35), font=font(54))
    return add_noise(img, 42, 0.78)


def vignette() -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pix = img.load()
    cx, cy = W / 2, H / 2
    maxd = math.sqrt(cx * cx + cy * cy)
    for y in range(H):
        for x in range(W):
            d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / maxd
            a = int(max(0, (d - 0.34) / 0.56) ** 1.8 * 230)
            pix[x, y] = (0, 0, 0, a)
    return img


def noise_overlay() -> Image.Image:
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    pix = img.load()
    random.seed(420)
    for y in range(256):
        for x in range(256):
            if y % 5 == 0:
                pix[x, y] = (0, 0, 0, 54)
            else:
                v = random.randrange(0, 255)
                pix[x, y] = (v, v, v, random.randrange(8, 38))
    return img


def icon() -> Image.Image:
    img = Image.new("RGBA", (256, 256), (158, 136, 57, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((42, 42, 214, 214), outline=(42, 36, 22), width=10)
    draw.rectangle((88, 84, 168, 202), fill=(24, 23, 20))
    draw.text((62, 26), "0", fill=(236, 212, 112), font=font(82))
    return img


def save_wav(path: Path, samples: list[float], rate: int = 44100) -> None:
    data = array("h", [max(-32767, min(32767, int(s * 32767))) for s in samples])
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(data.tobytes())


def make_audio() -> None:
    rate = 44100
    dur = 3.2
    samples = []
    for n in range(int(rate * dur)):
        t = n / rate
        value = 0.075 * math.sin(2 * math.pi * 58 * t) + 0.028 * math.sin(2 * math.pi * 116 * t)
        value += random.uniform(-0.010, 0.010)
        samples.append(value)
    save_wav(AUDIO / "hum_loop.wav", samples, rate)

    samples = []
    for n in range(int(rate * 0.09)):
        t = n / rate
        env = max(0.0, 1.0 - t / 0.09)
        samples.append(env * (0.18 * math.sin(2 * math.pi * 840 * t) + random.uniform(-0.08, 0.08)))
    save_wav(AUDIO / "click.wav", samples, rate)

    samples = []
    for n in range(int(rate * 0.28)):
        t = n / rate
        env = math.exp(-t * 11)
        samples.append(env * (0.52 * math.sin(2 * math.pi * 74 * t) + random.uniform(-0.04, 0.04)))
    save_wav(AUDIO / "thump.wav", samples, rate)

    samples = []
    for n in range(int(rate * 1.1)):
        t = n / rate
        env = min(1.0, t * 18) * math.exp(-t * 2.4)
        tone = 0.42 * math.sin(2 * math.pi * (320 + 580 * t) * t)
        tone += 0.25 * math.sin(2 * math.pi * 71 * t)
        tone += random.uniform(-0.28, 0.28)
        samples.append(max(-0.9, min(0.9, env * tone)))
    save_wav(AUDIO / "sting.wav", samples, rate)


def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)
    scenes = {
        "bg_start.png": scene_start(),
        "bg_hallway.png": scene_hallway(),
        "bg_junction.png": scene_junction(),
        "bg_sign.png": scene_sign(),
        "bg_door.png": scene_door(),
        "bg_other.png": scene_other(),
        "vignette.png": vignette(),
        "noise_overlay.png": noise_overlay(),
        "icon.png": icon(),
    }
    for name, img in scenes.items():
        img.save(IMAGES / name)
    make_audio()


if __name__ == "__main__":
    main()

