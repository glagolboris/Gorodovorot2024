from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
import asyncio
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
import json
import random
import aiogram


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

        keyboard = [[InlineKeyboardButton(text='Начать игру!', callback_data='start_game')],
                    [InlineKeyboardButton(text='Помощь', callback_data='help')],
                    [InlineKeyboardButton(text='Профиль', callback_data='profile')],
                    [InlineKeyboardButton(text='Статистика', callback_data='statistic')]]
        self.start_mrkp = InlineKeyboardMarkup(inline_keyboard=keyboard)

    def game_buttons_builder(self, user_id):
        """
        Builder of inline buttons in game
        """

        city, available_categories = self.db.get_game_data(user_id=user_id)
        city_data = self.data[city]
        city_categories = city_data['categories']
        categories = [category for category in city_categories if category['id'] in available_categories]
        if len(categories) > 0:
            buttons = [[InlineKeyboardButton(text=category['name'], callback_data=category['id'])]
                       for category in categories]
            buttons.append([InlineKeyboardButton(text='⬅️ Выйти в меню', callback_data='stop_game')])
            game_mrkp = InlineKeyboardMarkup(inline_keyboard=buttons)

            return game_mrkp

        else:
            return None

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
                                     reply_markup=self.start_mrkp, parse_mode='html',
                                     disable_web_page_preview=1)
                user_id = message.chat.id
                user_first = message.from_user.first_name
                user_second = message.from_user.last_name
                user_username = message.from_user.username
                self.db.add_user(user_id=user_id, user_nickname=user_username, user_firstname=user_first,
                                 user_secondname=user_second)

            else:

                if not self.db.get_game_status(user_id=message.chat.id):
                    self.db.clear_after_game(user_id=message.chat.id)
                    await message.answer(f'Рад тебя видеть, <a href="https://t.me/{message.from_user.username}">'
                                         f'{message.from_user.first_name}</a>!',
                                         reply_markup=self.start_mrkp, parse_mode='html',
                                         disable_web_page_preview=1)

        @self.dispatcher.message(Command('admin'))
        async def admin_cmd(message: types.Message):
            command = message.text.split('/admin ')[1]
            if command == 'change_game_status':
                self.db.game_status(user_id=message.chat.id)
                await message.answer(f"✅ Status changed to - {self.db.get_game_status(user_id=message.chat.id)}")
            elif command == 'drop':
                self.db.drop_tables()
                self.db.create_tables()
                await message.answer(f'✅ Tables was dropped')

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

        @self.dispatcher.callback_query(lambda call: call.data == 'cancel')
        async def callback(call: CallbackQuery):
            markup = self.game_buttons_builder(user_id=call.from_user.id)
            msg = self.bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                             text='🌟 Выберите категорию', reply_markup=markup)
            await msg

        @self.dispatcher.callback_query(lambda call: call.data.startswith('id'))
        async def callback(call: CallbackQuery):
            category_id = call.data[2:]
            city, available_categories = self.db.get_game_data(user_id=call.from_user.id)
            available_categories.remove(category_id)
            self.db.set_available_categories(user_id=call.from_user.id, categories=available_categories)

            categories = self.data[city]['categories']
            for category_ in categories:
                if category_['id'] == category_id:
                    category = category_

            text = f'🌟 <b>"{category["name"]}"</b>\n{open(category["info_path"]).read()}'

            await self.bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

            await self.bot.send_photo(chat_id=call.from_user.id,
                                      photo=BufferedInputFile.from_file(category['image_path']),
                                      caption=text, parse_mode='html')
            self.db.set_waiting_for_city(user_id=call.from_user.id, status=True)

        @self.dispatcher.callback_query(lambda call: call.data == 'back')
        async def callback(call: CallbackQuery):
            self.buttons_builder()
            await self.bot.edit_message_text(text=f'Рад тебя видеть, <a href="https://t.me/{call.from_user.username}">'
                                                  f'{call.from_user.first_name}</a>!',
                                             reply_markup=self.start_mrkp, parse_mode='html',
                                             disable_web_page_preview=1, message_id=call.message.message_id,
                                             chat_id=call.from_user.id)

        @self.dispatcher.callback_query(lambda call: call.data == 'help')
        async def help_cmd(call: types.Message):
            buttons = [[InlineKeyboardButton(text='Назад', callback_data='back')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await self.bot.edit_message_text(chat_id=call.from_user.id,
                                             text="👤 Цель игры - угадать крупные города России "
                                                  "по интересным фактам."
                                                  "Вам предстоит выбирать одну из доступных"
                                                  "  категорий о городе. Бот присылает информацию, "
                                                  "а ваша задача - дать верный ответ. Если ваш ответ совпадает "
                                                  "с правильным вариантом, вы побеждаете! В противном случае, вам "
                                                  "придется выбрать следующую категорию. Если вы не угадаете правильный вариант"
                                                  "из всех категорий, вы проигрываете.",
                                             reply_markup=keyboard, message_id=call.message.message_id)

        @self.dispatcher.callback_query(lambda call: call.data == 'profile')
        async def profile_cmd(call: types.Message):
            buttons = [[InlineKeyboardButton(text='Назад', callback_data='back')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await self.bot.edit_message_text(chat_id=call.from_user.id,
                                             text=f"У вас - {self.db.get_score(user_id=call.from_user.id)} очков!",
                                             reply_markup=keyboard, message_id=call.message.message_id)

        @self.dispatcher.callback_query(lambda call: call.data == 'statistic')
        async def statistic(call: types.Message):
            buttons = [[InlineKeyboardButton(text='Назад', callback_data='back')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            text = '🔰 ТОП ИГРОКОВ:\n' + self.db.get_records()
            await self.bot.edit_message_text(chat_id=call.from_user.id, text=text, parse_mode='html',
                                             reply_markup=keyboard, message_id=call.message.message_id,
                                             disable_web_page_preview=1)

        @self.dispatcher.callback_query(lambda call: call.data == 'stop_game')
        async def callback(call: CallbackQuery):
            self.db.game_status(user_id=call.from_user.id, status=False)
            self.db.set_waiting_for_city(user_id=call.from_user.id, status=False)
            self.db.clear_after_game(user_id=call.from_user.id)
            self.buttons_builder()
            await self.bot.edit_message_text(text=f'Рад тебя видеть, <a href="https://t.me/{call.from_user.username}">'
                                                  f'{call.from_user.first_name}</a>!',
                                             reply_markup=self.start_mrkp, parse_mode='html',
                                             disable_web_page_preview=1, message_id=call.message.message_id,
                                             chat_id=call.from_user.id)

    def text_handler(self):
        """
        Handler of text messages
        """

        @self.dispatcher.message()
        async def any_messages(message: Message):
            if self.db.waiting_for_city_get(user_id=message.chat.id):
                answer = message.text.strip().lower()
                city, available_categories = self.db.get_game_data(user_id=message.chat.id)
                if answer in self.data[city]['variants']:
                    buttons = [[InlineKeyboardButton(text='Сыграть еще раз!', callback_data=f'start_game')],
                               [InlineKeyboardButton(text='Назад', callback_data=f'back')]]
                    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                    await self.bot.send_message(chat_id=message.chat.id, text='Верно!')
                    msg = self.bot.send_message(chat_id=message.chat.id, text='Вы победили!', reply_markup=keyboard)
                    await msg
                    self.db.game_status(user_id=message.chat.id, status=False)
                    self.db.set_waiting_for_city(user_id=message.chat.id, status=False)
                    city, available_categories = self.db.get_game_data(user_id=message.chat.id)
                    self.db.add_score(user_id=message.chat.id, scores=len(available_categories))
                    self.db.clear_after_game(user_id=message.chat.id)




                else:
                    self.db.set_waiting_for_city(user_id=message.chat.id, status=False)
                    await self.bot.send_message(chat_id=message.chat.id, text='Неверно!')
                    markup = self.game_buttons_builder(user_id=message.chat.id)
                    if markup:
                        msg = self.bot.send_message(chat_id=message.chat.id,
                                                    text='🌟 Выберите категорию', reply_markup=markup)
                    else:
                        buttons = [[InlineKeyboardButton(text='Попробовать еще раз', callback_data=f'start_game')],
                                   [InlineKeyboardButton(text='Назад', callback_data=f'back')]]
                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                        msg = self.bot.send_message(chat_id=message.chat.id,
                                                    text='🔰 Вы проиграли!', reply_markup=keyboard)
                        self.db.game_status(user_id=message.chat.id, status=False)
                        self.db.set_waiting_for_city(user_id=message.chat.id, status=False)
                        self.db.clear_after_game(user_id=message.chat.id)

                    await msg

    def run_sync_func(self):
        self.handler_of_commands()
        self.handler_callbacks()
        self.text_handler()

    async def start(self):
        await self.dispatcher.start_polling(self.bot)
