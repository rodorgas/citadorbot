import io
import textwrap
import time
import emoji
import re

from enum import Enum
from typing import List
from PIL import Image, ImageDraw, ImageFont, ImageColor
from utils import decode_compressed_file


def open_image(emoji_bytes: io.BytesIO):
    img = Image.open(emoji_bytes)
    img.load()
    emoji_bytes.close()
    return img.convert("RGBA")


emojis = {
    emoji_name: open_image(emoji_file)
    for emoji_name, emoji_file in decode_compressed_file()
}

FONT_REGULAR = "./fonts/Roboto-Regular.ttf"
FONT_ITALIC = "./fonts/Roboto-Italic.ttf"
FONT_EMOJI = "./fonts/NotoColorEmoji.ttf"

FONT_EMOJI_SIZE = 109
FONT_REGULAR_SIZE = 72
BACKGROUND_COLOR = (0, 0, 0)
COLOR = "white"
WRAP_WIDTH = 30
PADDING = 10
MARGIN = 15


_UNICODE_EMOJI_REGEX = "|".join(
    map(re.escape, sorted(emoji.EMOJI_DATA.keys(), key=len, reverse=True))
)
EMOJI_REGEX = re.compile(f"({_UNICODE_EMOJI_REGEX})")


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.upper())
            kw["log_time"][name] = int((te - ts) * 1000)
        else:
            print("%r  %2.2f ms" % (method.__name__, (te - ts) * 1000))
        return result

    return timed


def _resize(
    im1: Image.Image, im2: Image.Image, resample=Image.BICUBIC, resize_big_image=True
):
    if im1.height == im2.height:
        _im1 = im1
        _im2 = im2
    elif ((im1.height > im2.height) and resize_big_image) or (
        (im1.height < im2.height) and not resize_big_image
    ):
        _im1 = im1.resize(
            (int(im1.width * im2.height / im1.height), im2.height), resample=resample
        )
        _im2 = im2
    else:
        _im1 = im1
        _im2 = im2.resize(
            (int(im2.width * im1.height / im2.height), im1.height), resample=resample
        )
    return _im1, _im2


def get_concat_horizontal(
    im1: Image.Image,
    im2: Image.Image,
    margin: int = MARGIN,
    padding: int = PADDING,
    align: str = "center",
    background_color: tuple = BACKGROUND_COLOR,
    resize: bool = False,
) -> Image.Image:
    """Concatenate im1 with im2 in this order

    Args:
        im1 (Image): left image
        im2 (Image): right image
        margin (int, optional): space around images. Defaults to MARGIN.
        padding (int, optional): space between content image and borders. Defaults to PADDING.
        align (str, optional): align images horizontally (top, center, bottom). Defaults to "center".
        background_color (tuple = (r, g, b), optional): background color. Defaults to BACKGROUND_COLOR.
    Returns:
        Image: The result image object of the concatenation
    """
    _im1, _im2 = _resize(im1, im2) if resize else (im1, im2)

    margin_padding = margin + padding
    max_height = max(_im1.height, _im2.height)
    height = max_height + 2 * margin_padding
    width = _im1.width + _im2.width + 2 * padding + 4 * margin

    img_concat = Image.new("RGB", (width, height), background_color)

    if align == "top":
        img_concat.paste(_im1, (margin_padding, margin_padding))
        img_concat.paste(_im2, (_im1.width + 3 * margin, margin_padding))
    if align == "center":
        img_concat.paste(
            _im1, (margin_padding, (max_height - _im1.height) // 2 + margin_padding)
        )
        img_concat.paste(
            _im2,
            (_im1.width + 3 * margin, (max_height - _im2.height) // 2 + margin_padding),
        )
    if align == "bottom":
        img_concat.paste(_im1, (margin_padding, height - _im1.height - margin_padding))
        img_concat.paste(
            _im2, (_im1.width + 3 * margin, height - _im2.height - margin_padding)
        )

    return img_concat


def get_concat_vertical(
    im1: Image.Image,
    im2: Image.Image,
    margin: int = MARGIN,
    padding: int = PADDING,
    align: str = "center",
    background_color: tuple = BACKGROUND_COLOR,
    resize: bool = False,
) -> Image.Image:
    """Concatenate im1 with im2 in this order

    Args:
        im1 (Image): top image
        im2 (Image): bottom image
        margin (int, optional): space around images. Defaults to MARGIN.
        padding (int, optional): space between content image and borders. Defaults to PADDING.
        align (str, optional): align images vertically (left, center, right). Defaults to "center".
    Returns:
        Image: The result image object of the concatenation
    """
    _im1, _im2 = _resize(im1, im2) if resize else (im1, im2)

    max_width = max(_im1.width, _im2.width)
    width = max_width + 2 * padding + 2 * margin
    hight = _im1.height + _im2.height + 2 * padding + 4 * margin
    margin_padding = margin + padding

    img_concat = Image.new("RGB", (width, hight), background_color)

    if align == "left":
        img_concat.paste(_im1, (margin_padding, margin_padding))
        img_concat.paste(_im2, (margin_padding, _im1.height + 3 * margin))
    if align == "center":
        img_concat.paste(_im1, ((max_width - _im1.width) // 2, margin_padding))
        img_concat.paste(
            _im2,
            ((max_width - _im2.width) // 2 + margin_padding, _im1.height + 3 * margin),
        )
    if align == "right":
        img_concat.paste(_im1, (width - _im1.width - margin_padding, margin_padding))
        img_concat.paste(
            _im2, (width - _im2.width - margin_padding, _im1.height + 3 * margin)
        )

    return img_concat


class TextInfo:
    class types(Enum):
        EMOJI = "EMOJI"
        TEXT = "TEXT"
        NEWLINE = "\n"

    class modes(Enum):
        RGB = "RGB"
        RGBA = "RGBA"

    def __init__(
        self,
        text: str,
        width: int = 0,
        text_type: str = None,
        mask=None,
        mode: str = None,
        use_font: bool = False,
    ):
        self.text = text
        self.width = width
        self.type = text_type
        self.mask = mask
        self.mode = mode
        self.use_font = use_font


def get_text_dimensions(text_string: str, font: ImageFont.FreeTypeFont, mode: str):
    mask, offset = font.getmask2(text_string, mode)
    return mask.size[0] + offset[0], mask.size[1] + offset[1], mask


def remove_variant_selector(raw_emoji):
    variant_selector_regex = r"\uFE0F"
    zero_width_joiner = chr(0x200D)
    if zero_width_joiner not in raw_emoji:
        return re.sub(variant_selector_regex, "", raw_emoji)
    return raw_emoji


def to_code_point(emoji: str):
    emoji = remove_variant_selector(emoji)
    return "-".join([format(ord(c), "04x") for c in emoji])


def parse_and_calculate_text_dimensions(
    text: str,
    font: ImageFont.ImageFont,
    font_emoji: ImageFont.ImageFont,
    emoji_size: int,
):
    max_width = max_height = break_lines = 0
    parsed_text = []
    for line in text:
        line_width = 0
        for current_text in [t for t in EMOJI_REGEX.split(line) if t]:

            use_default_font = False
            if current_text == TextInfo.types.NEWLINE:
                current_text_type = TextInfo.types.NEWLINE
                break_lines += 1
                max_width = max(max_width, line_width)
                line_width = 0

            elif emoji.is_emoji(current_text):
                mode = TextInfo.modes.RGBA
                current_text_type = TextInfo.types.EMOJI
                code_point = to_code_point(current_text)
                mask = emojis.get(code_point)

                if mask:
                    width, height = mask.size
                    ratio = min(emoji_size / width, emoji_size / height)
                    width, height = int(width * ratio), int(height * ratio)
                    mask = mask.resize((width, height), resample=Image.BICUBIC)
                else:
                    use_default_font = True
                    width, height, mask = get_text_dimensions(
                        current_text,
                        font_emoji,
                        mode=TextInfo.modes.RGBA.value,
                    )
            else:
                mode = TextInfo.modes.RGB
                current_text_type = TextInfo.types.TEXT
                width, height, mask = get_text_dimensions(
                    current_text,
                    font,
                    mode=TextInfo.modes.RGB.value,
                )

            parsed_text.append(
                TextInfo(
                    current_text,
                    width=width,
                    text_type=current_text_type,
                    mask=mask,
                    mode=mode,
                    use_font=use_default_font,
                )
            )

            line_width += width
            max_height = max(max_height, height)

        parsed_text.append(TextInfo("\n", text_type=TextInfo.types.NEWLINE))
        max_width = max(max_width, line_width)

    return parsed_text, int(max_width), int(max_height), break_lines


def _draw_emojis(xy, draw, mask):
    color, mask = mask, mask.getband(3)
    color.fillband(3, (draw.ink >> 24) & 0xFF)
    coord = xy[0] + mask.size[0], xy[1] + mask.size[1]
    draw.im.paste(color, xy + coord, mask)


def _draw_text(
    img: Image.Image,
    text: List[TextInfo],
    padding: int = 0,
    line_height: int = 0,
    font_color: str = "white",
):

    draw = ImageDraw.Draw(img)
    ink = draw.draw.draw_ink(ImageColor.getcolor(font_color, "RGBA"))

    y = x = padding
    for text_info in text:
        if text_info.type == TextInfo.types.NEWLINE:
            y += line_height
            x = padding
            continue

        width, height = text_info.mask.size

        _y = y + (line_height - height) // 2
        if text_info.mode == TextInfo.modes.RGBA:
            if text_info.use_font:
                _draw_emojis((x, _y), draw, text_info.mask)
            else:
                img.paste(
                    text_info.mask, (x, _y, x + width, _y + height), mask=text_info.mask
                )
        else:
            draw.draw.draw_bitmap((x, _y), text_info.mask, ink)

        x += width


@timeit
def text_image(
    text: str,
    font: str = FONT_REGULAR,
    font_emoji: str = FONT_EMOJI,
    font_size: int = FONT_REGULAR_SIZE,
    font_emoji_size: str = FONT_EMOJI_SIZE,
    font_color: tuple = COLOR,
    background_color: tuple = BACKGROUND_COLOR,
    width: int = WRAP_WIDTH,
    padding: int = PADDING,
    line_height: int = 0,
) -> Image.Image:
    """Creates an image object which is proportional to the text size.
    The text is wrapped if exceed the passed width.

    Args:
        text (str): text to be rendered
        font (str, optional): path for the text font. Defaults to FONT.
        font_emoji (str, optional): path for the text font emoji. Defaults to FONT_EMOJI.
        font_size (int, optional): size of the text. Defaults to FONT_EMOJI_SIZE.
        font_emoji_size (int, optional): size of the text. Defaults to FONT_EMOJI_SIZE.
        font_color (str, optional): color of the text in string in css-color. Defaults to COLOR.
        background_color (tuple, optional): color of the text box. Defaults to BACKGROUND_COLOR.
        width (int, optional): with at text should be wrapped. Defaults to WRAP_WIDTH.
        padding (int, optional): padding of the text box. Defaults to PADDING.
        line_height (int, optional): the extra height which the text will be drawn at. Defaults to zero.

    Returns:
        PILL.Image.Image: the image object containing the text
    """

    _text = [
        item
        for sublist in textwrap.wrap(
            text.strip(), width=width, replace_whitespace=False
        )
        for item in sublist.split("\n")
    ]

    _font = ImageFont.truetype(font, font_size, layout_engine=ImageFont.LAYOUT_RAQM)
    _font_emoji = ImageFont.truetype(
        font_emoji,
        font_emoji_size,
        layout_engine=ImageFont.LAYOUT_RAQM,
    )

    (
        parsed_text,
        max_width,
        max_height,
        break_lines,
    ) = parse_and_calculate_text_dimensions(_text, _font, _font_emoji, font_size)

    img = Image.new(
        "RGB",
        (
            int(max_width + 2 * padding),
            int((max_height + line_height) * (len(_text) + break_lines) + 2 * padding),
        ),
        background_color,
    )

    _draw_text(
        img,
        parsed_text,
        line_height=max_height + line_height,
        padding=padding,
        font_color=font_color,
    )

    return img


if __name__ == "__main__":
    img = text_image(
        "asadsdasd \n\n\n🧔🏿‍♀️ 👨‍👩‍👧‍👦👨‍👩‍👧‍👦👨‍👧‍👧🌂🥽👓👓🧶🪢🪡🧵🦺👔👘👜🩰👢",
        padding=20,
        line_height=500,
        font_size=200,
        font_color="#1b89a1",
    )
    img.show()
