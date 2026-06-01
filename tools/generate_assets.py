from __future__ import annotations

import math
import random
import wave
from array import array
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


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


def fluorescent(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=4, fill=(226, 210, 113), outline=(116, 103, 61), width=2)
    draw.rectangle((x + 7, y + 4, x + w - 7, y + h - 4), fill=(254, 238, 153))
    for r in range(8, 40, 8):
        draw.ellipse((x - r, y - r, x + w + r, y + h + r), outline=(236, 216, 115), width=1)


def base_room(seed: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    random.seed(seed)
    img = Image.new("RGB", (W, H), (135, 122, 78))
    draw = ImageDraw.Draw(img)
    ceiling = [(0, 0), (W, 0), (W, 188), (930, 232), (350, 232), (0, 205)]
    floor = [(0, 382), (365, 360), (900, 360), (W, 388), (W, H), (0, H)]
    left_wall = [(0, 205), (350, 232), (365, 360), (0, 420)]
    back_wall = [(350, 232), (930, 232), (900, 360), (365, 360)]
    right_wall = [(930, 232), (W, 188), (W, 420), (900, 360)]
    paste_polygon_gradient(img, ceiling, (77, 73, 52), (136, 126, 83), 0, 232)
    paste_polygon_gradient(img, left_wall, (149, 136, 86), (112, 102, 70), 200, 420)
    paste_polygon_gradient(img, back_wall, (164, 150, 94), (128, 117, 76), 228, 360)
    paste_polygon_gradient(img, right_wall, (141, 130, 84), (106, 96, 67), 188, 420)
    paste_polygon_gradient(img, floor, (128, 116, 76), (109, 97, 64), 360, H)
    for offset, poly in enumerate((ceiling, left_wall, back_wall, right_wall, floor)):
        add_surface_texture(img, poly, seed + offset, 0.05, 54)
    draw_ceiling_grid(draw, (655, 224), 238)
    draw_floor_perspective(draw, (655, 344), 372)
    draw_column(draw, 330, 170, 550, 76, "left")
    draw_column(draw, 940, 184, 520, 64, "right")
    draw_light_panel(draw, (510, 72, 710, 96), 48)
    draw_light_panel(draw, (266, 132, 420, 150), 28)
    draw_light_panel(draw, (814, 134, 944, 151), 28)
    return img, draw


def draw_doorway(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], dark: bool = True) -> None:
    x1, y1, x2, y2 = box
    draw.rectangle((x1 - 8, y1 - 8, x2 + 8, y2 + 8), fill=(92, 79, 45))
    fill = (20, 19, 16) if dark else (83, 78, 62)
    draw.rectangle((x1, y1, x2, y2), fill=fill)
    draw.line((x1, y1, x2, y1), fill=(221, 193, 91), width=2)


def color_lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def paste_polygon_gradient(
    img: Image.Image,
    polygon: list[tuple[int, int]],
    top: tuple[int, int, int],
    bottom: tuple[int, int, int],
    y1: int = 0,
    y2: int = H,
) -> None:
    gradient = Image.new("RGB", (W, H), top)
    gd = ImageDraw.Draw(gradient)
    for y in range(H):
        t = (y - y1) / max(1, y2 - y1)
        t = max(0.0, min(1.0, t))
        gd.line((0, y, W, y), fill=color_lerp(top, bottom, t))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(polygon, fill=255)
    img.paste(gradient, (0, 0), mask)


def add_surface_texture(img: Image.Image, polygon: list[tuple[int, int]], seed: int, opacity: float = 0.055, strength: int = 56) -> None:
    random.seed(seed)
    noise = Image.effect_noise((W, H), strength).convert("L")
    colored = Image.merge("RGB", (noise, noise, noise))
    tint = Image.new("RGB", (W, H), (151, 139, 93))
    texture = Image.blend(tint, colored, 0.22)
    texture = ImageEnhance.Contrast(texture).enhance(0.76)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(polygon, fill=int(255 * opacity))
    img.paste(texture, (0, 0), mask)


def draw_ceiling_grid(draw: ImageDraw.ImageDraw, vanishing: tuple[int, int], horizon_y: int = 230) -> None:
    vx, vy = vanishing
    for x in range(-180, W + 220, 86):
        draw.line((x, 0, vx + (x - W // 2) * 0.24, horizon_y), fill=(96, 91, 64), width=2)
    for y in range(30, horizon_y, 42):
        margin = int((horizon_y - y) * 1.55)
        draw.line((-margin, y, W + margin, y + 7), fill=(91, 86, 61), width=2)


def draw_light_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], glow: int = 48) -> None:
    x1, y1, x2, y2 = box
    for r in range(glow, 0, -12):
        draw.rounded_rectangle((x1 - r, y1 - r // 3, x2 + r, y2 + r // 3), radius=3, outline=(151, 143, 94), width=1)
    draw.rounded_rectangle(box, radius=3, fill=(238, 230, 181), outline=(135, 126, 84), width=2)
    for x in range(x1 + 7, x2 - 4, 10):
        draw.line((x, y1 + 3, x, y2 - 3), fill=(255, 251, 215), width=2)


def draw_column(draw: ImageDraw.ImageDraw, x: int, top_y: int, bottom_y: int, width: int, light_side: str = "left") -> None:
    x1, x2 = x - width // 2, x + width // 2
    if light_side == "left":
        shades = [(x1, (139, 128, 81)), (x1 + width // 3, (173, 159, 97)), (x2, (101, 93, 62))]
    else:
        shades = [(x1, (100, 93, 62)), (x1 + width // 2, (154, 142, 88)), (x2, (181, 166, 99))]
    for xx in range(x1, x2):
        t = (xx - x1) / max(1, width)
        if t < 0.5:
            local = t / 0.5
            color = color_lerp(shades[0][1], shades[1][1], local)
        else:
            local = (t - 0.5) / 0.5
            color = color_lerp(shades[1][1], shades[2][1], local)
        draw.line((xx, top_y, xx, bottom_y), fill=color)
    draw.rectangle((x1, top_y, x2, bottom_y), outline=(82, 74, 48), width=2)
    draw.rectangle((x1 - 10, bottom_y - 10, x2 + 10, bottom_y + 8), fill=(100, 89, 57))


def draw_floor_perspective(draw: ImageDraw.ImageDraw, vanish: tuple[int, int], y_start: int = 360) -> None:
    vx, vy = vanish
    for y in range(y_start + 14, H, 38):
        draw.line((0, y, W, y - 8), fill=(94, 84, 57), width=1)
    for x in range(-80, W + 120, 140):
        draw.line((x, H, vx + int((x - W // 2) * 0.12), vy), fill=(103, 93, 62), width=1)

def scene_start() -> Image.Image:
    img = Image.new("RGB", (W, H), (132, 120, 78))
    draw = ImageDraw.Draw(img)
    ceiling = [(0, 0), (W, 0), (W, 190), (920, 214), (420, 212), (0, 198)]
    floor = [(0, 385), (390, 362), (835, 355), (W, 375), (W, H), (0, H)]
    left_wall = [(0, 198), (420, 212), (390, 362), (0, 410)]
    back_wall = [(420, 212), (920, 214), (835, 355), (390, 362)]
    right_wall = [(920, 214), (W, 190), (W, 405), (835, 355)]
    paste_polygon_gradient(img, ceiling, (73, 69, 49), (132, 122, 81), 0, 230)
    paste_polygon_gradient(img, left_wall, (153, 141, 89), (112, 101, 69), 190, 420)
    paste_polygon_gradient(img, back_wall, (159, 148, 94), (128, 116, 75), 205, 365)
    paste_polygon_gradient(img, right_wall, (139, 128, 83), (101, 91, 64), 190, 420)
    paste_polygon_gradient(img, floor, (123, 113, 74), (108, 96, 63), 355, H)
    for seed, poly in ((20, ceiling), (21, left_wall), (22, back_wall), (23, right_wall), (24, floor)):
        add_surface_texture(img, poly, seed)
    draw_ceiling_grid(draw, (668, 226), 232)
    draw_floor_perspective(draw, (650, 338), 365)

    left_opening = [(20, 258), (255, 236), (305, 373), (0, 500)]
    draw.polygon([(0, 238), (275, 218), (330, 390), (0, 535)], fill=(98, 88, 59))
    draw.polygon(left_opening, fill=(38, 36, 31))
    draw.polygon([(48, 282), (255, 250), (266, 348), (45, 432)], fill=(45, 43, 36))

    right_path_floor = [(832, 355), (1038, 308), (W, 322), (W, 590), (930, 492)]
    right_opening = [(900, 238), (W, 210), (W, 452), (955, 405), (835, 355)]
    draw.polygon([(874, 226), (W, 194), (W, 470), (940, 428), (815, 364)], fill=(114, 103, 70))
    draw.polygon(right_opening, fill=(74, 68, 53))
    paste_polygon_gradient(img, right_path_floor, (138, 127, 83), (118, 106, 70), 310, 590)
    draw.line((884, 232, 1035, 212), fill=(72, 65, 47), width=3)

    draw_column(draw, 328, 172, 540, 76, "left")
    draw_column(draw, 628, 192, 430, 48, "left")
    draw_column(draw, 770, 184, 505, 58, "right")
    draw_column(draw, 1036, 172, 560, 72, "right")
    draw_light_panel(draw, (746, 18, 902, 38), 56)
    draw_light_panel(draw, (430, 118, 610, 137), 42)
    draw_light_panel(draw, (322, 160, 464, 176), 30)
    draw_light_panel(draw, (648, 182, 735, 195), 22)
    random.seed(130)
    for _ in range(8):
        x = random.randint(64, 300)
        y = random.randint(525, 690)
        draw.line(
            [(x, y), (x + random.randint(90, 230), y + random.randint(-20, 26))],
            fill=(100 + random.randint(0, 40), 16, 12),
            width=random.randint(3, 7),
        )
    for _ in range(6):
        x = random.randint(150, 465)
        y = random.randint(472, 662)
        draw.ellipse((x - 8, y - 5, x + 8, y + 5), fill=(93, 12, 10))
    return add_noise(img.filter(ImageFilter.GaussianBlur(0.35)), 22, 0.90)


def stop_sign_foreground() -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, 210
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
    img = Image.new("RGB", (W, H), (126, 115, 74))
    draw = ImageDraw.Draw(img)
    ceiling = [(0, 0), (W, 0), (W, 192), (878, 226), (338, 228), (0, 200)]
    floor = [(0, 380), (512, 440), (748, 438), (W, 362), (W, H), (0, H)]
    left_wall = [(0, 200), (338, 228), (512, 440), (0, 548)]
    right_wall = [(878, 226), (W, 192), (W, 505), (748, 438)]
    back_wall = [(338, 228), (878, 226), (748, 438), (512, 440)]
    paste_polygon_gradient(img, ceiling, (70, 67, 48), (126, 116, 77), 0, 232)
    paste_polygon_gradient(img, left_wall, (143, 130, 83), (99, 90, 63), 200, 548)
    paste_polygon_gradient(img, right_wall, (134, 123, 80), (94, 86, 62), 190, 505)
    paste_polygon_gradient(img, back_wall, (111, 101, 70), (55, 52, 43), 225, 438)
    paste_polygon_gradient(img, floor, (122, 111, 73), (104, 92, 61), 360, H)
    for seed, poly in ((31, ceiling), (32, left_wall), (33, right_wall), (34, back_wall), (35, floor)):
        add_surface_texture(img, poly, seed)
    draw_ceiling_grid(draw, (642, 222), 234)
    draw_floor_perspective(draw, (642, 407), 390)
    draw.polygon([(356, 228), (868, 228), (748, 438), (512, 440)], fill=(43, 41, 36))
    draw.polygon([(416, 260), (802, 258), (706, 392), (556, 394)], fill=(30, 29, 27))
    draw_column(draw, 260, 158, 610, 92, "left")
    draw_column(draw, 936, 176, 560, 74, "right")
    draw_column(draw, 1070, 178, 500, 50, "right")
    draw_light_panel(draw, (506, 74, 690, 96), 46)
    draw_light_panel(draw, (318, 138, 460, 155), 28)
    draw_light_panel(draw, (758, 140, 876, 156), 26)
    random.seed(210)
    trail = [(452, 684), (505, 608), (586, 548), (672, 488), (724, 420), (760, 318)]
    for width, color in ((19, (72, 8, 7)), (10, (131, 18, 13)), (4, (181, 36, 24))):
        draw.line(trail, fill=color, width=width, joint="curve")
    for _ in range(18):
        x = random.randint(450, 760)
        y = random.randint(300, 650)
        draw.ellipse((x - 10, y - 5, x + 12, y + 6), fill=(95 + random.randint(0, 50), 12, 9))
    return add_noise(img.filter(ImageFilter.GaussianBlur(0.35)), 24, 0.88)


def scene_right_path() -> Image.Image:
    img = Image.new("RGB", (W, H), (137, 125, 80))
    draw = ImageDraw.Draw(img)
    ceiling = [(0, 0), (W, 0), (W, 188), (932, 230), (382, 230), (0, 205)]
    floor = [(0, 382), (382, 360), (850, 360), (W, 382), (W, H), (0, H)]
    left_wall = [(0, 205), (382, 230), (382, 360), (0, 418)]
    back_wall = [(382, 230), (932, 230), (850, 360), (382, 360)]
    right_wall = [(932, 230), (W, 188), (W, 438), (850, 360)]
    paste_polygon_gradient(img, ceiling, (79, 75, 53), (139, 129, 86), 0, 232)
    paste_polygon_gradient(img, left_wall, (150, 137, 88), (113, 103, 70), 200, 418)
    paste_polygon_gradient(img, back_wall, (164, 151, 98), (132, 121, 80), 225, 360)
    paste_polygon_gradient(img, right_wall, (143, 132, 88), (107, 97, 68), 190, 438)
    paste_polygon_gradient(img, floor, (131, 120, 79), (111, 99, 66), 360, H)
    for seed, poly in ((41, ceiling), (42, left_wall), (43, back_wall), (44, right_wall), (45, floor)):
        add_surface_texture(img, poly, seed)
    draw_ceiling_grid(draw, (682, 222), 238)
    draw_floor_perspective(draw, (690, 342), 370)
    draw.polygon([(530, 230), (920, 230), (852, 372), (520, 372)], fill=(148, 137, 91))
    draw.rectangle((585, 252, 708, 372), fill=(56, 52, 42))
    draw.rectangle((608, 268, 685, 372), fill=(38, 36, 31))
    draw.line((530, 230, 920, 230), fill=(93, 84, 58), width=3)
    draw_column(draw, 382, 166, 552, 82, "left")
    draw_column(draw, 646, 188, 432, 48, "left")
    draw_column(draw, 902, 190, 492, 58, "right")
    draw_column(draw, 1068, 178, 552, 64, "right")
    draw_light_panel(draw, (708, 52, 888, 74), 48)
    draw_light_panel(draw, (460, 126, 622, 144), 34)
    draw_light_panel(draw, (832, 146, 950, 161), 28)
    random.seed(310)
    for _ in range(55):
        x = random.randint(420, 1040)
        y = random.randint(405, 680)
        shade = random.randint(102, 136)
        draw.point((x, y), fill=(shade, shade - 10, shade - 37))
    return add_noise(img.filter(ImageFilter.GaussianBlur(0.35)), 21, 0.93)


def scene_hallway() -> Image.Image:
    img = Image.new("RGB", (W, H), (128, 116, 74))
    draw = ImageDraw.Draw(img)
    ceiling = [(0, 0), (W, 0), (850, 186), (430, 186)]
    left = [(0, 0), (430, 186), (520, 528), (0, H)]
    right = [(W, 0), (850, 186), (760, 528), (W, H)]
    center = [(430, 186), (850, 186), (760, 528), (520, 528)]
    floor = [(0, H), (W, H), (760, 528), (520, 528)]
    paste_polygon_gradient(img, ceiling, (72, 68, 49), (125, 115, 77), 0, 186)
    paste_polygon_gradient(img, left, (150, 136, 86), (102, 93, 65), 0, H)
    paste_polygon_gradient(img, right, (136, 125, 82), (96, 88, 62), 0, H)
    paste_polygon_gradient(img, center, (160, 146, 91), (116, 105, 70), 186, 528)
    paste_polygon_gradient(img, floor, (116, 105, 70), (95, 85, 57), 528, H)
    for seed, poly in ((51, ceiling), (52, left), (53, right), (54, center), (55, floor)):
        add_surface_texture(img, poly, seed)
    draw_ceiling_grid(draw, (640, 186), 190)
    draw_floor_perspective(draw, (640, 510), 530)
    draw.rectangle((565, 250, 715, 505), fill=(29, 28, 25))
    draw.rectangle((579, 268, 701, 505), fill=(18, 18, 16))
    draw.line((565, 250, 715, 250), fill=(91, 83, 58), width=3)
    draw_light_panel(draw, (572, 66, 732, 88), 46)
    draw_light_panel(draw, (602, 144, 700, 158), 24)
    return add_noise(img.filter(ImageFilter.GaussianBlur(0.35)), 25, 0.89)


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
    img = Image.new("RGB", (W, H), (72, 69, 57))
    draw = ImageDraw.Draw(img)
    ceiling = [(0, 0), (W, 0), (W, 190), (890, 225), (390, 225), (0, 205)]
    floor = [(0, 386), (380, 370), (900, 370), (W, 390), (W, H), (0, H)]
    left = [(0, 205), (390, 225), (380, 370), (0, 420)]
    back = [(390, 225), (890, 225), (900, 370), (380, 370)]
    right = [(890, 225), (W, 190), (W, 420), (900, 370)]
    paste_polygon_gradient(img, ceiling, (45, 44, 39), (84, 79, 60), 0, 225)
    paste_polygon_gradient(img, left, (95, 86, 61), (61, 58, 49), 205, 420)
    paste_polygon_gradient(img, back, (110, 99, 66), (67, 62, 51), 225, 370)
    paste_polygon_gradient(img, right, (85, 78, 58), (57, 54, 47), 190, 420)
    paste_polygon_gradient(img, floor, (82, 74, 54), (50, 47, 40), 370, H)
    for seed, poly in ((81, ceiling), (82, left), (83, back), (84, right), (85, floor)):
        add_surface_texture(img, poly, seed, 0.06, 58)
    draw_ceiling_grid(draw, (650, 222), 230)
    draw_floor_perspective(draw, (650, 354), 382)
    draw.rectangle((600, 236, 708, 454), fill=(13, 13, 12))
    draw.rectangle((612, 253, 696, 454), fill=(5, 5, 5))
    draw_light_panel(draw, (520, 72, 730, 96), 52)
    return add_noise(img.filter(ImageFilter.GaussianBlur(0.35)), 30, 0.80)


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
