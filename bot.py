from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
import asyncio
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
import json
import random


class AioBot:
    def __init__(self, api_id, database):
        self.data = json.load(open('cities.json'))
        self.bot = Bot(api_id)
        self.buttons_builder()
        self.dispatcher = Dispatcher()
        self.db = database
        self.run_sync_func()



    def buttons_builder(self):
        """
        Builder of inline keyboard buttons
        """
        self.start_mrkp = InlineKeyboardBuilder()
        bttn_1 = InlineKeyboardButton(text='Начать игру!', callback_data='start_game')
        self.start_mrkp.add(bttn_1)

    def game_buttons_builder(self, user_id):
        """
        Builder of inline buttons in game
        """
        city, available_categories = self.db.get_game_data(user_id=user_id)
        city_data = self.data[city]
        city_categories = city_data['categories']
        categories = [category for category in city_categories if category['id'] in available_categories]
        buttons = [[InlineKeyboardButton(text=category['name'], callback_data=category['id'])]
                   for category in categories]
        game_mrkp = InlineKeyboardMarkup(inline_keyboard=buttons)


        return game_mrkp

    def start_game_process(self, user_id):
        """
        If user clicked start_game button
        Working with JSON data
        """
        city = random.choice(list(self.data.keys()))
        available_categories = [category["id"] for category in self.data[city]["categories"]]
        self.db.add_game(user_id=user_id, city=city, categories=available_categories)

    def handler_of_commands(self):
        """
        Handler of commands
        """
        @self.dispatcher.message(Command('start'))
        async def cmd_start(message: types.Message):
            if not self.db.get_user_by_id(message.chat.id):
                await message.answer(f'Привет, <a href="https://t.me/{message.from_user.username}">'
                                     f'{message.from_user.first_name}</a>! Видимо, ты у нас новенький.',
                                     reply_markup=self.start_mrkp.as_markup(), parse_mode='html',
                                     disable_web_page_preview=1)
                user_id = message.chat.id
                user_first = message.from_user.first_name
                user_second = message.from_user.last_name
                user_username = message.from_user.username
                self.db.add_user(user_id=user_id, user_nickname=user_username, user_firstname=user_first,
                                 user_secondname=user_second)

            else:
                if not self.db.get_game_status(user_id=message.chat.id):
                    await message.answer(f'Рад тебя видеть, <a href="https://t.me/{message.from_user.username}">'
                                         f'{message.from_user.first_name}</a>!',
                                         reply_markup=self.start_mrkp.as_markup(), parse_mode='html',
                                         disable_web_page_preview=1)

                print(message.chat.id)

        @self.dispatcher.message(Command('admin'))
        async def admin_cmd(message: types.Message):
            command = message.text.split('/admin ')[1]
            if command == 'change_game_status':
                self.db.game_status(user_id=message.chat.id)
                await message.answer(f"✅ Status changed to - {self.db.get_game_status(user_id=message.chat.id)}")


    def handler_callbacks(self):
        """
        Handler of keyboard (buttons) callbacks
        """
        @self.dispatcher.callback_query(lambda call: call.data == 'start_game')
        async def callback(call: CallbackQuery):
            await self.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
            self.db.game_status(user_id=call.from_user.id, status=True)
            self.start_game_process(user_id=call.from_user.id)
            markup = self.game_buttons_builder(user_id=call.from_user.id)
            msg = self.bot.send_message(chat_id=call.message.chat.id, text='🌟 Выберите категорию',
                                        reply_markup=markup)
            await msg

        @self.dispatcher.callback_query(lambda call: len(call.data) == 1)
        async def callback(call: CallbackQuery):
            buttons = [[InlineKeyboardButton(text='Да', callback_data=f'id{call.data}')],
                       [InlineKeyboardButton(text='Нет', callback_data='cancel')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await self.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text='Вы уверены в выборе категории?', reply_markup=keyboard)

    def run_sync_func(self):
        self.handler_of_commands()
        self.handler_callbacks()

    async def start(self):
        await self.dispatcher.start_polling(self.bot)
