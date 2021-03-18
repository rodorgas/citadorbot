from PIL import Image, ImageDraw, ImageFont
import textwrap
import emoji
import math
import unicodedata

FONT_REGULAR = "./fonts/Roboto-Regular.ttf"
FONT_ITALIC = "./fonts/Roboto-Italic.ttf"
FONT_EMOJI = "./fonts/NotoColorEmoji.ttf"

FONT_SIZE = 109
BACKGROUND_COLOR = (0, 0, 0)
COLOR = (255, 255, 255)
WRAP_WIDTH = 30
PADDING = 10
MARGIN = 15


def _resize(im1: Image, im2: Image, resample=Image.BICUBIC, resize_big_image=True):
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


def text_image2(
    text: str,
    font: str = FONT_REGULAR,
    font_size: int = FONT_SIZE,
    font_color: tuple = COLOR,
    background_color: tuple = BACKGROUND_COLOR,
    width: int = WRAP_WIDTH,
    padding: int = PADDING,
) -> Image:
    """Creates an image object which is proportional to the text size.
    The text is wrapped if exceed the passed width.

    Args:
        text (str): text to be rendered
        font (str, optional): path for the text font. Defaults to FONT.
        font_size (int, optional): size of the text. Defaults to FONT_SIZE.
        font_color (tuple, optional): color of the text. Defaults to COLOR.
        width (int, optional): with at text should be wrapped. Defaults to WRAP_WIDTH.
        padding (int, optional): padding of the text box. Defaults to PADDING.
        background_color (tuple, optional): color of the text box. Defaults to BACKGROUND_COLOR.

    Returns:
        Image: the image object containing the text
    """
    text_wrapped = "\n".join(textwrap.wrap(text, width, replace_whitespace=False))

    font = ImageFont.truetype(font, font_size, layout_engine=ImageFont.LAYOUT_RAQM)
    text_size = font.getsize_multiline(text_wrapped, spacing=30)

    total_text_width = text_size[0] + 2 * padding
    total_text_height = text_size[1] + 2 * padding

    img = Image.new("RGB", (total_text_width, total_text_height), background_color)
    draw = ImageDraw.Draw(img)
    draw.multiline_text(
        (padding, padding),
        text_wrapped,
        fill=font_color,
        font=font,
        spacing=30,
        embedded_color=True,
    )

    return img


def get_concat_horizontal(
    im1: Image,
    im2: Image,
    margin: int = MARGIN,
    padding: int = PADDING,
    align: str = "center",
    background_color: tuple = BACKGROUND_COLOR,
    resize: bool = False,
) -> Image:
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
    im1: Image,
    im2: Image,
    margin: int = MARGIN,
    padding: int = PADDING,
    align: str = "center",
    background_color: tuple = BACKGROUND_COLOR,
    resize: bool = False,
) -> Image:
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


def _calculate_text_image_size(text, font, font_emoji):
    def getsize(c):
        if c in emoji.UNICODE_EMOJI_ENGLISH:
            return font_emoji.getlength(c), font_emoji.getsize(c)[1]
        return font.getlength(c), font.getsize(c)[1]

    max_width = 0
    max_height = 0
    break_lines = 0

    for line in text:
        line_width = 0
        for c in line:
            if unicodedata.category(c) in ["Cc", "Mn", "Zs"]:
                if c == "\n":
                    break_lines += 1
                    max_width = max(max_width, line_width)
                    line_width = 0
                continue
            w, h = getsize(c)
            line_width += w
            max_height = max(max_height, h)

        max_width = max(max_width, line_width)

    return math.ceil(max_width), math.ceil(max_height), break_lines


def _draw_text(
    img: Image,
    text: str,
    font: ImageFont,
    font_color: str,
    font_emoji: ImageFont,
    line_height,
    padding,
):

    draw = ImageDraw.Draw(img)

    y = 0
    for line in text:
        x = padding
        for c in line:
            if unicodedata.category(c) in ["Cc", "Mn"]:
                if c == "\n":
                    y += line_height
                    x = padding
                continue

            _font = font_emoji if c in emoji.UNICODE_EMOJI_ENGLISH else font

            draw.text(
                (int(x), y),
                c,
                font=_font,
                fill=font_color,
                embedded_color=True,
            )
            x += _font.getlength(c)

        y += line_height


def text_image(
    text: str,
    font: str = FONT_REGULAR,
    font_emoji: str = FONT_EMOJI,
    font_size: int = FONT_SIZE,
    font_emoji_size: str = FONT_SIZE,
    font_color: tuple = COLOR,
    background_color: tuple = BACKGROUND_COLOR,
    width: int = WRAP_WIDTH,
    padding: int = PADDING,
) -> Image:
    """Creates an image object which is proportional to the text size.
    The text is wrapped if exceed the passed width.

    Args:
        text (str): text to be rendered
        font (str, optional): path for the text font. Defaults to FONT.
        font_emoji (str, optional): path for the text font emoji. Defaults to FONT_EMOJI.
        font_size (int, optional): size of the text. Defaults to FONT_SIZE.
        font_emoji_size (int, optional): size of the text. Defaults to FONT_SIZE.
        font_color (tuple, optional): color of the text. Defaults to COLOR.
        width (int, optional): with at text should be wrapped. Defaults to WRAP_WIDTH.
        padding (int, optional): padding of the text box. Defaults to PADDING.
        background_color (tuple, optional): color of the text box. Defaults to BACKGROUND_COLOR.

    Returns:
        Image: the image object containing the text
    """

    _text = text.strip()
    _text = textwrap.wrap(_text, width=width, replace_whitespace=False)

    _font = ImageFont.truetype(font, font_size, layout_engine=ImageFont.LAYOUT_RAQM)
    _font_emoji = ImageFont.truetype(
        font_emoji, font_emoji_size, layout_engine=ImageFont.LAYOUT_RAQM
    )

    max_width, max_height, break_lines = _calculate_text_image_size(
        _text, _font, _font_emoji
    )

    img = Image.new(
        "RGB",
        (
            math.ceil((max_width + 2 * padding) + max_width * 0.05),
            max_height * (len(_text) + break_lines) + 2 * padding,
        ),
        background_color,
    )

    _draw_text(img, _text, _font, font_color, _font_emoji, max_height, padding)

    return img
