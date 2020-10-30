#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, \
                         Filters
from telegram import User
from dotenv import load_dotenv
from validator_collection import checkers

import logging
import shlex
import subprocess
import random
import os
import requests
import make_image

load_dotenv()
TOKEN = os.getenv("CITADOR_TOKEN")
FAKE_MARK = "Esta é uma falsa citação gerada com /fake_quote"

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Olá! Use o comando /quote em resposta a uma mensagem ou /fake_quote para criar uma citação fake')

def format_name(name):
    return name[1].upper() + ", " + name[0] if len(name) > 1 else name[0]

def get_user_pic(user: User):
    name = user.first_name + " " + user.last_name if user.last_name else user.first_name
    name = name.split(" ")
    formatted_name = format_name(name)

    photos = user.get_profile_photos().photos

    if not photos or not photos[0]:
        return formatted_name

    # first photo, last version (better quality)
    photo_size = photos[0][-1]
    photo = photo_size.get_file().download_as_bytearray()

    return (photo, (photo_size.width, photo_size.height), formatted_name)

def get_pic_from_url(url, update):
    if not checkers.is_url(url):
        update.message.reply_text('Use um URL válido')
        return None

    response = requests.get(url)
    valid_content_types = ['image/jpeg', 'image/png']

    if not response.headers['content-type'] in valid_content_types:
        update.message.reply_text('O URL deve ser de uma imagem jpeg ou png.')
        return None


    image = response.content

    return (image, (500, 500))


def apply_overlay(n, photo, quote, name, context, fake_quote=False):
    result = f'result-{n}.jpg'

    if photo:
        make_image_quote(photo, quote, name, context, result, fake_quote)
        return result
    else:
        make_image_noprofile_quote(quote, name, context, result)
        return result

    return result


def make_fake_quote(bot, update):
    print('fake_quote ' + update.effective_user.username)
    splitted_text = update['message']['text'].split()

    if len(splitted_text) < 5:
        update.message.reply_text('Use /fake_quote <url da imagem> <nome> <sobrenome> <frase>')
        return

    url = splitted_text[1]
    photo = get_pic_from_url(url, update)

    if photo is None:
        return

    fake_quote = True
    name = [splitted_text[2], splitted_text[3]]
    quote = splitted_text[4:]
    joined_quote = ' '.join(quote)
    formatted_name = format_name(name)

    n = random.randint(1, 1000)
    file_name = False

    file_name = f'image-{n}.jpg'
    open(file_name, 'wb').write(photo[0])
    result = apply_overlay(n, file_name, joined_quote, formatted_name, None, fake_quote)

    update.message.reply_photo(photo=open(result, 'rb'))

    if file_name:
        os.remove(file_name)
    os.remove(result)

def make_quote(bot, update):
    print('quote ' + update.effective_user.username)
    if len(result := update['message']['text'].split(' ', 1)) > 1 and update['message']['forward_from'] is None:
        context = result[-1]
    else:
        context = None
    if update['message']['forward_from'] is not None:
        if update['message']['chat']['type'] == 'group':
            return
        user_pic = get_user_pic(update.message.forward_from)
        quote = update['message']['text']
    else:
        if update['message']['reply_to_message'] is None:
            update.message.reply_text('Use /quote em reposta a uma mensagem.')
            return

        if update['message']['reply_to_message']['forward_from'] is not None:
            user_pic = get_user_pic(update.message.reply_to_message.forward_from)
        else:
            user_pic = get_user_pic(update.message.reply_to_message.from_user)
        quote = update['message']['reply_to_message']['text']

    n = random.randint(1, 1000)
    file_name = False

    if len(user_pic) == 3:
        file_name = f'user-{n}.jpg'
        open(file_name, 'wb').write(user_pic[0])
        name = user_pic[2]
    else:
        name = user_pic

    result = apply_overlay(n, file_name, quote, name, context)

    update.message.reply_photo(photo=open(result, 'rb'))

    if file_name:
        os.remove(file_name)
    os.remove(result)


def make_image_quote(
    photo: str,
    quote: str,
    name: str,
    context: str,
    result: str,
    fake_quote: bool=False
    ):

    with make_image.Image.open(photo) as img:
        quote = "“{}”".format(quote)
        img = img.convert("L")
        img_caption = make_image.text_image(quote, padding=25)
        img_author = make_image.text_image(name, font_size=int(make_image.FONT_SIZE * 0.5), padding=25)
        img_text = make_image.get_concat_vertical(img_caption, img_author, align="right")

        if fake_quote:
            img_fake = make_image.text_image(FAKE_MARK, font_size=int(make_image.FONT_SIZE * 0.4), padding=25)
            img_text = make_image.get_concat_vertical(img_text, img_fake, align="right")

        if context is not None:
            img_context = make_image.text_image(context, font_size=int(make_image.FONT_SIZE * 0.5), padding=25)
            img_text = make_image.get_concat_vertical(img_text, img_context, align="left")
        img_quote = make_image.get_concat_horizontal(img_text, img, resize=img.height < img_text.height)
        img_quote.save(result)


def make_image_noprofile_quote(quote: str, name: str, context: str, result:  str):
    quote = '“{}”'.format(quote)
    img_caption = make_image.text_image(quote, padding=25)
    img_author = make_image.text_image(name, font_size=int(make_image.FONT_SIZE * 0.5), padding=25)
    img_text = make_image.get_concat_vertical(img_caption, img_author, align="right")
    if context is not None:
            img_context = make_image.text_image(context, font_size=int(make_image.FONT_SIZE * 0.5), padding=25)
            img_text = make_image.get_concat_vertical(img_text, img_context, align="left")
    img_text.save(result)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("quote", make_quote))
    dp.add_handler(CommandHandler("fake_quote", make_fake_quote))
    dp.add_handler(MessageHandler(Filters.forwarded, make_quote))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
