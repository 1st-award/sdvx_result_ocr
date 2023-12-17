import os
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple
from yolov8.predict import Box

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FONT_DIR_PATH = os.environ.get("FONT_DIR_PATH")
TITLE_HEIGHT = 20

def _new_title(title: str, size: Tuple[int, int]) -> Image:
    image = Image.new('RGB', (size[0], TITLE_HEIGHT), BLACK)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_DIR_PATH, 10)
    draw.text((10, 0), title, font=font, fill=WHITE)
    return image

def calc_size(cutted_img: dict[str: Image]) -> Tuple[int, int]:
    max_width = -1
    max_height = 0
    for _, image in cutted_img.items():
        width, height = image.size
        if max_width < width:
            max_width = width
        max_height += height + TITLE_HEIGHT # 자른사진 높이 + TITLE 높이
    return max_width, max_height

def merge(cutted_img: dict[str: Image], size: Tuple[int, int]) -> Image:
    # for img in cutted_img:
    current_height: int = 0
    murge_image = Image.new('RGB', size, BLACK)
    for title, image in cutted_img.items():
        title_image = _new_title(title, size)
        murge_image.paste(title_image, (0, current_height))
        murge_image.paste(image, (0, current_height + TITLE_HEIGHT))
        current_height += image.size[1] + TITLE_HEIGHT
    return murge_image

def cut(original_img: Image, box: Box) -> Image:
    if box.class_nm == "title":
        xx, xy, yx, yy = box.pos
        new_yy = (xy + yy) // 2
        box.pos = (xx, xy, yx, new_yy)
    cutting_img = original_img.crop(box.pos)
    # cutting_img.show()
    return cutting_img

# for file in os.listdir("./sdvx/"):
#     cut_image(f"./sdvx/{file}")
# new_title("TITLE", (850, 1888))