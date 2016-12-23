from telegram import InlineKeyboardButton

# Build and return a keyword for a bot
class InlineKeyboardBuilder :

    def __init__(self):
        self.callback_map = {}
        self.kb = []

    def register_option(self, name="", cb_data=None):
        self.callback_map[name] = cb_data

    def build_keyboard(self):
        for key, value in self.callback_map.items():
            inline_btn = [InlineKeyboardButton(key, callback_data=value)]
            self.kb.append(inline_btn)

    def filter_option(self, options=[]):
        pass

    def get_keyboard(self):
        self.build_keyboard()
        return self.kb