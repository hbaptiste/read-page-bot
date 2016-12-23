from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from helpers.InlineKeyboardBuilder import InlineKeyboardBuilder
import logging
import uuid
import sys
import os
from pprint import pprint


# data
states_data = {}

# states list
states = {'START': "START", 'METADATA':'METADATA','UPLOAD_IMAGE':'UPLOAD_IMAGE','IMAGE_UPLOADED':"IMAGE_UPLOADED", 'TITLE': "TITLE", 'PAGE': "PAGE", 'TAG': "tag", 'END': 'END'}

CURRENT_STATE = states['START']

# states transition
STATE_TRANSITIONS = {}
STATE_TRANSITIONS[states['START']] = ['UPLOAD_IMAGE']
STATE_TRANSITIONS[states['UPLOAD_IMAGE']] = ['IMAGE_UPLOADED']
STATE_TRANSITIONS[states['IMAGE_UPLOADED']] = ['TITLE'] # mandatory
STATE_TRANSITIONS[states['TITLE']] = 'METADATA'
STATE_TRANSITIONS[states['METADATA']] = ['PAGE','TAG','END']
STATE_TRANSITIONS[states['PAGE']] = ['TAG','END']
STATE_TRANSITIONS[states['TAG']] = ['END']


# start image -> metadata { title: xxx, page: xxx, tag: tag1, tag2, tag3 }

#logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))
IMAGES_PATH = os.path.join(PROJECT_PATH, "data")

updater = Updater(token='324505554:AAFy6DK57_2BdB3BtDspNMWVoeuIzYPNwoo')

#dispatcher
dispatcher = updater.dispatcher


def setCurrentState(next_state, update):
    global CURRENT_STATE
    print("previous current state %s " % (next_state))
    CURRENT_STATE = next_state
    handle_states(update)

# compute next state
def compute_transitions(state):
    try:
        return STATE_TRANSITIONS[state]
    except Exception as e:
        return states.START

def getUid():
    return str(uuid.uuid4())

# Keyboard add filter
def createKeyBoard(update):
    kb_builder = InlineKeyboardBuilder()
    if CURRENT_STATE == "METADATA":
        kb_builder.register_option(name="Ajouter la page", cb_data='PAGE')
        kb_builder.register_option(name="Ajouter des Tags", cb_data='TAGS')
        kb_builder.register_option(name="Terminer", cb_data='END')
    if CURRENT_STATE == 'TAG':
        kb_builder.register_option(name="Ajouter des Tags", cb_data='TAG')
        kb_builder.register_option(name="Terminer", cb_data='END')
    if CURRENT_STATE == 'PAGE':
        kb_builder.register_option(name="Ajouter la page", cb_data='PAGE')
        kb_builder.register_option(name="Terminer", cb_data='END')

    keyboard = kb_builder.get_keyboard()
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Do you wan?', reply_markup=reply_markup)

'''
display the right keyboards according the actual state
'''
def handle_states(update):

    next_states = compute_transitions(CURRENT_STATE)

    if CURRENT_STATE == states['START']:
        update.message.reply_text("Hello, please upload a new page!")

    if CURRENT_STATE == states['IMAGE_UPLOADED']:
        update.message.reply_text("Image reçue!")
        if len(next_states) == 1 and next_states[0] == 'TITLE':
            setCurrentState('TITLE', update)

    if CURRENT_STATE == states['TITLE']:
        update.message.reply_text("Now enter the source")

    if CURRENT_STATE == states['METADATA']:
        # show options
        keyboard = createKeyBoard(update)

# text
def handle_text(bot, update):
   if CURRENT_STATE == states['TITLE']:
        title = update.message.text.strip()
        setCurrentState(states['METADATA'], update)

# start handler
def start(bot, update):
    setCurrentState(states['START'], update)

def button(bot, update):
    query = update.callback_query

    bot.editMessageText(text="Selection option %s" % query.data,
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id
        )


def save_image(bot, update):
    user = update.message.from_user
    logging.info("User %s did send a page" % user)

    #find the file
    try:
        photo_file = bot.getFile(update.message.photo[-1].file_id)
        image_name = getUid() + '.jpg'
        photo_file.download(os.path.join(IMAGES_PATH, image_name))
        setCurrentState('IMAGE_UPLOADED', update)
    except Exception as e:
        print(e.message)
        update.message.reply_text("Erreur lors de la transmission de l'image!")

# new command for adding an image
'''
> upload image
> ask for tags for images
'''

# handler
start_handler = CommandHandler('start', start)
photo_handler = MessageHandler(Filters.photo, save_image)
text_handler = MessageHandler(Filters.text, handle_text)

# dispatcher
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_handler(start_handler)
dispatcher.add_handler(photo_handler)
dispatcher.add_handler(text_handler)

if __name__ == '__main__':
    try:
        updater.start_polling()
        updater.idle()
    except Exception as e:
        print(e.message)
        sys.exit()