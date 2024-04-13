from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
import asyncio


class AioBot:
    dispatcher = Dispatcher()

    def __init__(self, api_id):
        self.bot = Bot(api_id)

    @dispatcher.message(Command('start'))
    async def cmd_start(message: types.Message):
        await message.answer("Привет!")

    async def start(self):
        await self.dispatcher.start_polling(self.bot)
