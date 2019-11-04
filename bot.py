#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, \
                         Filters
from telegram import User
import logging
import shlex
import subprocess
import random
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Olá! Use o comando /quote em resposta a uma mensagem')

def get_user_pic(user: User):
    photos = user.get_profile_photos().photos

    if not photos or not photos[0]:
        return None

    # first photo, last version (better quality)
    photo_size = photos[0][-1]
    photo = photo_size.get_file().download_as_bytearray()

    return (photo, (photo_size.width, photo_size.height))


def apply_overlay(n, photo, quote):
    result = 'result-{n}.jpg'.format(n=n)
    command = f'./make_image.sh "{quote}" "{photo}" "{result}"'
    subprocess.call(shlex.split(command))

    return result


def make_quote(bot, update):
    print('quote ' + update.effective_user.username)

    if update['message']['reply_to_message'] is None:
        update.message.reply_text('Use /quote em reposta a uma mensagem.')
        return

    pic, size = get_user_pic(update.message.reply_to_message.from_user)
    n = random.randint(1, 1000)
    file_name = 'user-{n}.jpg'.format(n=n)
    open(file_name, 'wb').write(pic)

    quote = update['message']['reply_to_message']['text']

    result = apply_overlay(n, file_name, quote)

    update.message.reply_photo(photo=open(result, 'rb'))

    os.remove(file_name)
    os.remove(result)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("987204899:AAGWMFVEjyQwwo6n_sGjjUkrRN_Aid1qUSY")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("quote", make_quote))

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
