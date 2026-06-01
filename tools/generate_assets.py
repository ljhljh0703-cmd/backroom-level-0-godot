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
    trail = [(70, 668), (150, 640), (245, 648), (335, 612), (448, 622)]
    draw.line(trail, fill=(62, 4, 4), width=28, joint="curve")
    draw.line(trail, fill=(154, 18, 14), width=17, joint="curve")
    draw.line([(92, 695), (210, 675), (320, 685), (405, 660)], fill=(126, 12, 10), width=11, joint="curve")
    for x, y, rx, ry in [
        (105, 650, 30, 12),
        (188, 632, 22, 8),
        (274, 648, 38, 13),
        (366, 616, 28, 10),
        (426, 634, 18, 7),
        (238, 690, 20, 8),
    ]:
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(112, 9, 8))


def stop_sign_shape(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, alpha_fill: tuple[int, int, int] = (113, 19, 17)) -> None:
    points = []
    for i in range(8):
        angle = math.pi / 8 + i * math.pi / 4
        points.append((cx + int(math.cos(angle) * radius), cy + int(math.sin(angle) * radius)))
    draw.polygon(points, fill=alpha_fill, outline=(214, 188, 120))
    draw.line(points + [points[0]], fill=(40, 22, 17), width=max(2, radius // 16))
    label_font = font(max(14, radius // 2))
    bbox = draw.textbbox((0, 0), "STOP", font=label_font)
    draw.text((cx - (bbox[2] - bbox[0]) / 2, cy - (bbox[3] - bbox[1]) / 2 - radius * 0.05), "STOP", fill=(238, 224, 177), font=label_font)


def scene_fork_stop() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: FORK_STOP")
    draw.rectangle((455, 45, 825, 230), fill=(0, 0, 0), outline=(76, 58, 40), width=3)
    text_center(draw, (455, 45, 825, 118), "STOP BACK", 28)
    arrow_path(draw, "left", "LEFT")
    arrow_path(draw, "right", "RIGHT")
    red_trace(draw)
    draw.text((120, 320), "LEFT", fill=HOT, font=font(34))
    draw.text((1010, 320), "RIGHT", fill=HOT, font=font(34))
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


def scene_stop_back_dark() -> Image.Image:
    img = Image.new("RGB", (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    for y in range(0, H, 48):
        draw.line((0, y, W, y), fill=(8, 8, 10), width=1)
    draw.rectangle((0, 0, 270, H), fill=(5, 5, 6), outline=(34, 34, 38), width=2)
    draw.text((34, 30), "BLOCKOUT: STOP_BACK_DARK", fill=(72, 72, 78), font=font(24))
    draw.text((44, H // 2 - 20), "BACK", fill=(92, 92, 96), font=font(30))
    return img


def scene_stop_back_red() -> Image.Image:
    img = Image.new("RGB", (W, H), (7, 0, 0))
    draw = ImageDraw.Draw(img)
    for y in range(0, H, 40):
        draw.line((0, y, W, y), fill=(22, 4, 4), width=2)
    for x in range(0, W, 70):
        draw.line((x, 0, W // 2, H // 2), fill=(18, 3, 3), width=1)
    draw.rectangle((0, 0, 270, H), fill=(8, 5, 5), outline=(70, 22, 18), width=2)
    draw.ellipse((435, 155, 845, 565), fill=(96, 14, 12), outline=(176, 32, 22), width=6)
    draw.rectangle((500, 210, 780, 520), fill=(20, 0, 0), outline=(210, 54, 36), width=5)
    text_center(draw, (500, 210, 780, 520), "RED GAP", 36)
    draw.text((34, 30), "BLOCKOUT: STOP_BACK_RED", fill=(146, 68, 56), font=font(24))
    draw.text((44, H // 2 - 20), "BACK", fill=(136, 72, 62), font=font(30))
    return img


def scene_left_blood_path() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: LEFT_BLOOD_PATH")
    doorway(draw, (710, 230, 1080, 615), "SWITCH")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    blood = ImageDraw.Draw(overlay)
    main_trail = [(360, 700), (430, 650), (500, 602), (574, 548), (646, 490), (704, 390)]
    blood.line(main_trail, fill=(64, 0, 0, 180), width=46, joint="curve")
    blood.line(main_trail, fill=(152, 11, 8, 225), width=27, joint="curve")
    blood.line([(400, 690), (455, 666), (505, 671), (572, 632)], fill=(182, 28, 20, 190), width=18, joint="curve")
    blood.line([(548, 590), (616, 585), (690, 552), (754, 510)], fill=(118, 6, 6, 170), width=16, joint="curve")
    for x, y, rx, ry, color in [
        (405, 678, 52, 20, (86, 0, 0, 200)),
        (492, 617, 42, 16, (136, 8, 7, 215)),
        (578, 552, 48, 18, (166, 16, 10, 225)),
        (654, 484, 36, 13, (112, 4, 4, 200)),
        (712, 410, 26, 11, (158, 20, 14, 215)),
        (475, 700, 20, 8, (198, 30, 20, 180)),
        (602, 625, 18, 8, (120, 0, 0, 180)),
        (748, 560, 15, 6, (150, 8, 8, 170)),
    ]:
        blood.ellipse((x - rx, y - ry, x + rx, y + ry), fill=color)
    blood.polygon([(438, 650), (512, 622), (592, 638), (542, 676), (468, 688)], fill=(78, 0, 0, 145))
    overlay = overlay.filter(ImageFilter.GaussianBlur(1.1))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.text((330, 590), "DRAG TRACE", fill=(190, 70, 62), font=font(28))
    return img


def scene_left_switch_room() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: LEFT_SWITCH_ROOM")
    draw.rectangle((520, 250, 760, 475), fill=(34, 34, 38), outline=LINE, width=4)
    draw.rectangle((576, 305, 704, 420), fill=(16, 16, 18), outline=HOT, width=5)
    draw.ellipse((618, 338, 662, 382), fill=(114, 28, 20), outline=(220, 80, 52), width=4)
    text_center(draw, (520, 430, 760, 500), "LIGHT BUTTON", 24)
    draw.line((320, 610, 470, 560), fill=RED, width=8)
    return img


def scene_right_panel_path() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: RIGHT_PANEL_PATH")
    doorway(draw, (870, 240, 1195, 610), "DEAD END")
    draw.rectangle((510, 190, 710, 560), fill=(62, 62, 66), outline=LINE, width=4)
    draw.ellipse((575, 230, 645, 300), fill=(12, 12, 14))
    draw.rectangle((595, 298, 625, 430), fill=(12, 12, 14))
    draw.line((595, 340, 548, 420), fill=(12, 12, 14), width=18)
    draw.line((625, 340, 672, 420), fill=(12, 12, 14), width=18)
    draw.line((603, 430, 570, 525), fill=(12, 12, 14), width=18)
    draw.line((617, 430, 650, 525), fill=(12, 12, 14), width=18)
    text_center(draw, (500, 560, 720, 615), "PANEL", 24)
    return img


def scene_right_dead_end() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: RIGHT_DEAD_END")
    draw.rectangle((360, 200, 920, 610), fill=(58, 58, 62), outline=LINE, width=5)
    draw.line((380, 240, 900, 590), fill=(36, 36, 40), width=5)
    draw.line((900, 240, 380, 590), fill=(36, 36, 40), width=5)
    text_center(draw, (430, 340, 850, 460), "DEAD END", 48)
    return img


def scene_true_exit_room() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: TRUE_EXIT_ROOM")
    draw.rectangle((455, 135, 825, 650), fill=(88, 88, 82), outline=(220, 205, 138), width=8)
    draw.rectangle((505, 190, 775, 635), fill=(190, 186, 150), outline=(240, 226, 158), width=5)
    draw.rectangle((520, 92, 760, 140), fill=(20, 72, 42), outline=HOT, width=4)
    text_center(draw, (520, 92, 760, 140), "EXIT", 34)
    return img


def scene_false_exit_room() -> Image.Image:
    img, draw = blockout_room("BLOCKOUT: FALSE_EXIT_STOP_ROOM")
    draw.rectangle((0, 0, W, H), fill=(13, 12, 10))
    for y in range(95, 620, 118):
        for x in range(85, 1220, 152):
            jitter_x = (x * 17 + y * 3) % 31 - 15
            jitter_y = (x * 7 + y * 11) % 23 - 11
            radius = 39 + ((x + y) % 18)
            stop_sign_shape(draw, x + jitter_x, y + jitter_y, radius, (92, 14, 13))
            draw.rectangle((x + jitter_x - 4, y + jitter_y + radius - 2, x + jitter_x + 4, y + jitter_y + radius + 92), fill=(58, 48, 32))
    floor_hatch = [(470, 625), (810, 625), (920, 715), (360, 715)]
    draw.polygon(floor_hatch, fill=(3, 3, 4), outline=(150, 32, 24))
    draw.line((430, 670, 850, 670), fill=(98, 20, 16), width=5)
    draw.text((34, 30), "BLOCKOUT: FALSE_EXIT_STOP_ROOM", fill=(130, 88, 72), font=font(24))
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
        "bg_fork_stop.png": scene_fork_stop(),
        "fg_stop_sign.png": stop_sign_foreground(),
        "bg_stop_back_dark.png": scene_stop_back_dark(),
        "bg_stop_back_red.png": scene_stop_back_red(),
        "bg_left_blood_path.png": scene_left_blood_path(),
        "bg_left_switch_room.png": scene_left_switch_room(),
        "bg_right_panel_path.png": scene_right_panel_path(),
        "bg_right_dead_end.png": scene_right_dead_end(),
        "bg_true_exit_room.png": scene_true_exit_room(),
        "bg_false_exit_room.png": scene_false_exit_room(),
        "vignette.png": vignette(),
        "noise_overlay.png": noise_overlay(),
        "icon.png": icon(),
    }
    for name, img in scenes.items():
        img.save(IMAGES / name)
    make_audio()


if __name__ == "__main__":
    main()
