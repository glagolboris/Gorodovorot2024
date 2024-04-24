from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
import asyncio
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


class AioBot:
    def __init__(self, api_id, database):
        self.bot = Bot(api_id)
        self.buttons_builder()
        self.dispatcher = Dispatcher()
        self.db = database
        self.run_sync_func()

    def buttons_builder(self):
        self.start_mrkp = InlineKeyboardBuilder()
        bttn_1 = InlineKeyboardButton(text='Начать игру!', callback_data='start_game')
        self.start_mrkp.add(bttn_1)

    def handler_of_start(self):
        @self.dispatcher.message(Command('start'))
        async def cmd_start(message: types.Message):
            if not self.db.get_user_by_id(int(message.from_user.id)):
                await message.answer("Привет! Видимо, ты у нас новенький.", reply_markup=self.start_mrkp.as_markup())
            else:
                await message.answer('Привет!')

    def run_sync_func(self):
        self.handler_of_start()

    async def start(self):
        await self.dispatcher.start_polling(self.bot)
