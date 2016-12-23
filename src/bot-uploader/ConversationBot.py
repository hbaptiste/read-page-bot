import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters \
CallbackQueryHandler


# setting up logging
logging.basicConfig(format='%(asctime)s -%(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(bot, update):

    kb_builder = InlineKeyboardBuilder()
    kb_builder.register_option(name="Ajouter un titre", cb_data='title')
    kb_builder.register_option(name="Ajouter un auteur", cb_data='author')
    kb_builder.register_option(name="Ajouter des tags", cb_data='tags')

    keyboard = kb_builder.get_keyboard()
    reply_markup = InlineKeyboardButton(keyboard)
    update.message.reply_text('Voulez-vous ajouter des métadonnées?', reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query # title - author - tags
    bot.editMessageText(
        text="Selected option %s" % query.data, \
        chat_id=query.message.chat_id \
        message_id = query.message.message_id
        )

'''
[available metadata]
title: titre /mandatory
author: author
page: 23
tags: tag1, tag2, tag3

'''

