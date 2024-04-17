import os
from dotenv import load_dotenv
from bot import AioBot
from db import asyncDb
import asyncio

class Main:
    def __init__(self) -> None:
        api = self.api_key
        self.aio_bot = AioBot(api)
        self.db = asyncDb(user='admin', password=self.db_password)
        asyncio.run(self.aio_bot.start())

    @property
    def api_key(self) -> str:
        """
        :return: Telegram Bot Api from .env
        """
        load_dotenv()
        get_api = os.getenv("API")
        return get_api

    @property
    def db_password(self) -> str:
        """
        :return: PostgreSQL user password from .env
        """
        load_dotenv()
        get_pass = os.getenv("DATABASE_PASSWORD")
        return get_pass


if __name__ == '__main__':
    main = Main()
