#!/usr/bin/env python3
"""민정 레시피북 런처 아이콘 생성기.

토마토색 푸딩셰프 캐릭터를 그려서 mipmap-*/ic_launcher.png,
ic_launcher_round.png, ic_launcher_foreground.png (adaptive) 를 만든다.
실행: python3 tools/make_icons.py  (프로젝트 루트에서)
"""
import os
from PIL import Image, ImageDraw

S = 1024  # 마스터 캔버스

CREAM = (255, 251, 242)
BODY = (255, 90, 54)        # 토마토 레드-오렌지
BODY_HI = (255, 133, 92)    # 하이라이트
BODY_SH = (226, 62, 32)     # 그림자
INK = (58, 36, 24)          # 눈/입
BLUSH = (255, 138, 120)
GREEN = (109, 196, 111)
GREEN_DK = (78, 165, 82)
WHITE = (255, 255, 255)
HAT_SH = (240, 226, 214)
YELLOW = (255, 209, 71)
ORANGE = (255, 138, 43)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vgrad(size, c_top, c_bottom):
    img = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(img)
    for y in range(size):
        d.line([(0, y), (size, y)], fill=lerp(c_top, c_bottom, y / (size - 1)))
    return img.convert("RGBA")


def rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m


def circle_mask(size):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size - 1, size - 1], fill=255)
    return m


def draw_character(canvas):
    """투명 캔버스 위에 푸딩셰프 캐릭터를 그린다 (1024 기준 좌표)."""
    d = ImageDraw.Draw(canvas, "RGBA")

    # --- 그림자 (바닥) ---
    d.ellipse([292, 790, 732, 872], fill=(190, 90, 40, 46))

    # --- 몸통 (살짝 배가 나온 푸딩 모양) ---
    body_box = [262, 392, 762, 862]
    body_mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(body_mask).ellipse(body_box, fill=255)

    body = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body, "RGBA")
    bd.ellipse(body_box, fill=BODY)
    # 오른쪽 아래 음영 (몸통 안쪽으로만)
    bd.ellipse([548, 560, 800, 900], fill=BODY_SH)
    # 위쪽 하이라이트
    bd.ellipse([318, 424, 528, 566], fill=BODY_HI)
    bd.ellipse([334, 440, 502, 540], fill=(255, 158, 120))
    body.putalpha(Image.composite(body.getchannel("A"), Image.new("L", (S, S), 0), body_mask))
    canvas.alpha_composite(body)
    d = ImageDraw.Draw(canvas, "RGBA")

    # --- 초록 꼭지 (모자 양옆으로 살짝 보이게) ---
    d.ellipse([236, 404, 340, 470], fill=GREEN)
    d.ellipse([690, 404, 790, 470], fill=GREEN)
    d.ellipse([236, 404, 340, 470], outline=GREEN_DK, width=8)
    d.ellipse([690, 404, 790, 470], outline=GREEN_DK, width=8)

    # --- 얼굴 ---
    # 볼
    d.ellipse([330, 660, 452, 736], fill=(255, 138, 120, 120))
    d.ellipse([572, 660, 694, 736], fill=(255, 138, 120, 120))

    # 눈
    for cx in (446, 614):
        d.ellipse([cx - 52, 600, cx + 52, 716], fill=INK)
        d.ellipse([cx - 30, 616, cx + 6, 656], fill=WHITE)
        d.ellipse([cx + 10, 662, cx + 30, 684], fill=(255, 255, 255, 190))

    # 입 (웃는 입)
    d.arc([468, 656, 592, 762], start=18, end=162, fill=INK, width=20)

    # --- 셰프 모자 ---
    # 모자 그림자
    d.ellipse([332, 300, 700, 452], fill=HAT_SH)
    # 모자 띠
    d.rounded_rectangle([352, 372, 680, 452], radius=34, fill=WHITE)
    # 모자 봉긋한 부분
    d.ellipse([366, 236, 548, 400], fill=WHITE)
    d.ellipse([482, 226, 664, 392], fill=WHITE)
    d.ellipse([416, 190, 604, 370], fill=WHITE)
    # 띠 접힘선
    d.rounded_rectangle([352, 424, 680, 452], radius=14, fill=HAT_SH)
    # 모자 하이라이트
    d.ellipse([430, 240, 520, 320], fill=(255, 255, 255))

    return canvas


def build_legacy(size):
    bg = vgrad(S, (255, 224, 130), ORANGE)
    # 위쪽에 노란 빛
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(glow, "RGBA").ellipse([-200, -320, 760, 420], fill=(255, 238, 170, 150))
    bg.alpha_composite(glow)

    char = draw_character(Image.new("RGBA", (S, S), (0, 0, 0, 0)))
    # 캐릭터를 살짝 축소해서 여백을 준다 (런처가 모서리를 잘라도 얼굴이 살아남게)
    scale = 0.88
    cw = int(S * scale)
    char = char.resize((cw, cw), Image.LANCZOS)
    ox = (S - cw) // 2
    oy = int((S - cw) / 2) + 22
    bg.alpha_composite(char, (ox, oy))

    bg.putalpha(rounded_mask(S, int(S * 0.22)))
    return bg.resize((size, size), Image.LANCZOS)


def build_round(size):
    img = build_legacy(S)
    img.putalpha(circle_mask(S))
    return img.resize((size, size), Image.LANCZOS)


def build_foreground(size):
    char = draw_character(Image.new("RGBA", (S, S), (0, 0, 0, 0)))
    return char.resize((size, size), Image.LANCZOS)


LEGACY = {
    "mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192,
}
FOREGROUND = {
    "mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432,
}


def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    res = os.path.join(root, "app", "src", "main", "res")

    for density, px in LEGACY.items():
        d = os.path.join(res, "mipmap-" + density)
        os.makedirs(d, exist_ok=True)
        build_legacy(px).save(os.path.join(d, "ic_launcher.png"))
        build_round(px).save(os.path.join(d, "ic_launcher_round.png"))

    for density, px in FOREGROUND.items():
        d = os.path.join(res, "mipmap-" + density)
        os.makedirs(d, exist_ok=True)
        build_foreground(px).save(os.path.join(d, "ic_launcher_foreground.png"))

    # 미리보기용 (앱에는 포함되지 않음)
    prev = os.path.join(root, "tools", "preview")
    os.makedirs(prev, exist_ok=True)
    build_legacy(512).save(os.path.join(prev, "icon-legacy-512.png"))
    build_round(512).save(os.path.join(prev, "icon-round-512.png"))

    print("icons written")


if __name__ == "__main__":
    main()
