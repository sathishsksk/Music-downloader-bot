from addons.utils import logger
from helpers.media_info import *
import os
import traceback
from messages.creator import *
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import http.server
import socketserver

dest = "telegramMusic/"
TOKEN = os.getenv("BOT_TOKEN")
APP_NAME = os.getenv("APP_NAME")

def health_check():
    # Perform any necessary health checks here
    # For example, check if the required environment variables are set
    if 'TOKEN' in os.environ:
        return 200
    else:
        return 500

class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(health_check())
        self.end_headers()

def start(update, context):
    fname = update.message.chat.first_name
    update.message.reply_text(start_msg(fname), parse_mode="MarkdownV2")

def help(update, context):
    update.message.reply_text(help_msg(), parse_mode="MarkdownV2")

def list(update, context):
    files = os.listdir("/app/telegramMusic")
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

            elif "/playlist/" or "/featured/" in query:
                msg = update.message.reply_text("Getting playlist info 🔎🔎")
                send_playlist(update, context, query, msg)
            else:
                wrong_link(update)
        else:
            process_exist(update)
    else:
        wrong_link(update)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("list", list))
    dp.add_handler(CommandHandler("contact", contact))
    dp.add_handler(MessageHandler(Filters.text, download, run_async=True))
    dp.add_error_handler(error_handler)

    logger.info("Loaded all handlers")

    # Set up webhook for the Telegram bot
    PORT = int(os.environ.get('PORT', 8080))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN,
                          webhook_url=f"https://{APP_NAME}.koyeb.app/{TOKEN}")

    # Set up health check server
    health_server = socketserver.TCPServer(("0.0.0.0", PORT + 1), HealthHandler)
    health_server.serve_forever()

if __name__ == "__main__":
    main()
