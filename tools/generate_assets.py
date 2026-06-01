from __future__ import annotations

import math
import random
import wave
from array import array
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "assets" / "images"
AUDIO = ROOT / "assets" / "audio"
W, H = 1280, 720

# Current visual mode is intentionally a blockout. Final image style should be
# applied in one pass after the room flow and object placement are approved.
BG = (10, 10, 11)
FLOOR = (32, 32, 34)
WALL = (46, 46, 48)
LINE = (92, 92, 96)
DARK = (2, 2, 3)
HOT = (188, 176, 112)
RED = (126, 20, 18)


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


def text_center(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, size: int = 32) -> None:
    fnt = font(size)
    bbox = draw.textbbox((0, 0), text, font=fnt)
    x = box[0] + (box[2] - box[0] - (bbox[2] - bbox[0])) / 2
    y = box[1] + (box[3] - box[1] - (bbox[3] - bbox[1])) / 2
    draw.text((x, y), text, fill=HOT, font=fnt)


def blockout_room(label: str = "") -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    ceiling = [(0, 0), (W, 0), (W, 205), (840, 260), (440, 260), (0, 205)]
    left_wall = [(0, 205), (440, 260), (455, 455), (0, 520)]
    back_wall = [(440, 260), (840, 260), (825, 455), (455, 455)]
    right_wall = [(840, 260), (W, 205), (W, 520), (825, 455)]
    floor = [(0, 520), (455, 455), (825, 455), (W, 520), (W, H), (0, H)]
    draw.polygon(ceiling, fill=(24, 24, 26))
    draw.polygon(left_wall, fill=WALL)
    draw.polygon(back_wall, fill=(56, 56, 58))
    draw.polygon(right_wall, fill=(38, 38, 40))
    draw.polygon(floor, fill=FLOOR)
    for x in range(0, W + 1, 160):
        draw.line((x, H, 640, 455), fill=(55, 55, 58), width=2)
    for y in range(500, H, 44):
        draw.line((0, y, W, y), fill=(55, 55, 58), width=2)
    for x in range(80, W, 160):
        draw.line((x, 0, 640, 260), fill=(48, 48, 51), width=2)
    for y in range(45, 230, 45):
        draw.line((0, y, W, y), fill=(48, 48, 51), width=2)
    draw.rectangle((520, 110, 760, 140), fill=(150, 145, 105), outline=HOT, width=3)
    if label:
        draw.text((34, 30), label, fill=(130, 130, 136), font=font(24))
    return img, draw


def doorway(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str = "") -> None:
    x1, y1, x2, y2 = box
    draw.rectangle((x1 - 12, y1 - 12, x2 + 12, y2 + 12), fill=(78, 78, 82), outline=LINE, width=3)
    draw.rectangle(box, fill=DARK)


def arrow_path(draw: ImageDraw.ImageDraw, side: str, label: str) -> None:
    if side == "left":
        poly = [(60, 355), (330, 285), (445, 455), (0, 620)]
    else:
        poly = [(950, 285), (1220, 355), (1280, 620), (835, 455)]
    draw.polygon(poly, fill=(4, 4, 5), outline=LINE)


def red_trace(draw: ImageDraw.ImageDraw) -> None:
    trail = [(90, 662), (175, 640), (260, 646), (345, 618), (430, 624)]
    draw.line(trail, fill=RED, width=9)
    draw.line([(110, 690), (240, 676), (330, 684)], fill=RED, width=6)


def scene_start() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: FORK")
    arrow_path(draw, "left", "LEFT")
    arrow_path(draw, "right", "RIGHT")
    red_trace(draw)
    return img


def stop_sign_foreground() -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, 218
    radius = 86
    points = []
    for i in range(8):
        angle = math.pi / 8 + i * math.pi / 4
        points.append((cx + int(math.cos(angle) * radius), cy + int(math.sin(angle) * radius)))
    draw.polygon(points, fill=(113, 19, 17, 245), outline=(216, 188, 121, 255))
    draw.line(points + [points[0]], fill=(40, 22, 17, 255), width=5)
    draw.text((cx - 75, cy - 29), "STOP", fill=(238, 224, 177, 255), font=font(50))
    draw.rectangle((cx - 8, cy + radius - 5, cx + 8, 512), fill=(73, 64, 43, 255))
    draw.rectangle((cx - 40, 500, cx + 40, 528), fill=(65, 55, 37, 255))
    return img


def scene_left_path() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: LEFT PATH")
    doorway(draw, (510, 255, 770, 470), "DARK PATH")
    draw.line([(430, 690), (500, 620), (575, 560), (650, 500), (705, 395)], fill=RED, width=13)
    for x, y in [(470, 650), (535, 600), (610, 550), (690, 480), (720, 420)]:
        draw.ellipse((x - 12, y - 7, x + 12, y + 7), fill=RED)
    return img


def scene_right_path() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: RIGHT PATH")
    doorway(draw, (545, 260, 735, 470), "CLEAN PATH")
    return img


def scene_hallway() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: HALL")
    doorway(draw, (565, 250, 715, 505), "END")
    return img


def scene_junction() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: JUNCTION")
    doorway(draw, (90, 250, 310, 610), "LEFT ROOM")
    doorway(draw, (970, 250, 1190, 610), "RIGHT HALL")
    draw.rectangle((520, 315, 760, 430), fill=(62, 62, 66), outline=LINE, width=3)
    text_center(draw, (520, 315, 760, 430), "VENT", 30)
    return img


def scene_sign() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: EXIT SIGN ROOM")
    doorway(draw, (70, 250, 290, 610), "BACK")
    draw.rectangle((500, 175, 815, 285), fill=(67, 28, 28), outline=HOT, width=4)
    text_center(draw, (500, 175, 815, 285), "EXIT", 54)
    draw.polygon([(805, 214), (930, 214), (930, 184), (1030, 230), (930, 276), (930, 246), (805, 246)], fill=(105, 31, 25))
    draw.rectangle((470, 370, 645, 455), fill=(62, 62, 66), outline=LINE, width=3)
    text_center(draw, (470, 370, 645, 455), "NO MAP", 24)
    return img


def scene_door() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: FINAL DOOR")
    draw.rectangle((490, 165, 790, 655), fill=(50, 50, 54), outline=LINE, width=9)
    draw.rectangle((525, 205, 755, 635), fill=(20, 20, 22), outline=(86, 86, 90), width=3)
    draw.ellipse((715, 420, 738, 443), fill=HOT)
    draw.rectangle((520, 104, 760, 150), fill=(20, 48, 32), outline=HOT, width=3)
    text_center(draw, (520, 104, 760, 150), "EXIT", 32)
    return img


def scene_other() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: END ROOM")
    doorway(draw, (590, 235, 710, 475), "")
    return img


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
    img = Image.new("RGBA", (256, 256), (42, 42, 46, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((42, 42, 214, 214), outline=(170, 160, 104), width=10)
    draw.rectangle((88, 84, 168, 202), fill=(8, 8, 9))
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
        "fg_stop_sign.png": stop_sign_foreground(),
        "bg_left_path.png": scene_left_path(),
        "bg_right_path.png": scene_right_path(),
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
