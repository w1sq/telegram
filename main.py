from math import e
import constants as keys
from telegram.ext import *
import responses as resp

print('Bot started')

def start_command(update,context):
    update.message.reply_text('Напиши что-нибудь для начала')


def help_command(update,context):
    update.message.reply_text('Гугл в помощь')


def send_image(update,context):
    update.message.send_photo('https://seebot.dev/images/archive/missions/1_Jun_2021.png')


def handle_massage(update,context):
    user_msg = str(update.message.text).lower()
    response = resp.sample_responses(user_msg)

    update.message.reply_text(response)


def error(update,context):
    print(f"Обновление {update} вызвало ошибку {context.error}")



def get_user_id(update,context):
    with open('user.txt','w') as userstxt:
        users = userstxt.readlines()
        user_id = update.message.chat.id
        if user_id not in users:
            userstxt.write(user_id)


def main():
    updater = Updater(keys.API_KEY, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start",start_command))
    dp.add_handler(CommandHandler("help",help_command))
    dp.add_handler(CommandHandler("image",send_image))
    
    dp.add_handler(MessageHandler(Filters.text,handle_massage))

    dp.add_error_handler(error)

    updater.start_polling()

main()