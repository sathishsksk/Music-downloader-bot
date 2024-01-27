from flask import Flask, request
import requests
import subprocess
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from helpers.media_info import *
from messages.creator import *
from telegram.ext.dispatcher import run_async

dest = "telegramMusic/"
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

app = Flask(__name__)

def health_check():
    return 'Bot is running and healthy!'

@app.route('/health', methods=['GET'])
def health():
    return health_check()

def start(update, context):
    fname = update.message.chat.first_name
    update.message.reply_text(start_msg(fname), parse_mode="MarkdownV2")

def help(update, context):
    update.message.reply_text(help_msg(), parse_mode="MarkdownV2")

def list(update, context):
    files = os.listdir(dest)
    string = ""
    for l in files:
        if l.endswith(".mp3"):
            s = "<b>"+l+"</b>"+"\n"
            string = string+s
    if string:
        update.message.reply_html(string)
    else:
        update.message.reply_html("No songs are currently present")

def contact(update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("Contact", url="telegram.me/TgBotsChat")], ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Contact The Maker:', reply_markup=reply_markup)

def error_handler(update, context):
    logger.error(f"Error {traceback.format_exc()}")

def download(update, context: CallbackContext):
    query = update.message.text
    if 'https://www.saavn' in query or 'https://www.jiosaavn' in query:
        if not context.user_data.get('downloading', False):
            if "/song/" in query:
                msg = update.message.reply_text("Getting song info 🔎🔎")
                send_song(update, context, query, msg)

            elif "/album" in query:
                msg = update.message.reply_text("Getting album info 🔎🔎")
                send_album(update, context, query, msg)

            elif "/playlist/" in query:
                msg = update.message.reply_text("Getting playlist info 🔎🔎")
                send_playlist(update, context, query, msg)
            elif "/featured/" in query:
                msg = update.message.reply_text("Getting featured info 🔎🔎")
                send_featured(update, context, query, msg)
            else:
                wrong_link(update)
        else:
            process_exist(update)
    else:
        wrong_link(update)

def download_media(song_id, quality='128kbps', output_format='mp3'):
    # Function to download media using FFmpeg with specified quality
    pass

def set_quality(update, context):
    # Command to set quality for downloading songs
    quality = context.args[0].lower()
    if quality in ['128kbps', '320kbps']:
        # Store the chosen quality in user_data
        context.user_data['quality'] = quality
        update.message.reply_text(f'Quality set to {quality}.')
    else:
        update.message.reply_text('Invalid quality option. Please choose either 128kbps or 320kbps.')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("list", list))
    dp.add_handler(CommandHandler("contact", contact))
    dp.add_handler(CommandHandler("setquality", set_quality, pass_args=True))
    dp.add_handler(MessageHandler(Filters.text, download, run_async=True))
    dp.add_error_handler(error_handler)

    logger.info("Loaded all handlers")

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
