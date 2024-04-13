import os
from dotenv import load_dotenv
from bot import AioBot
import asyncio

class Main:
    def __init__(self) -> None:
        api = self.api_key
        self.aio_bot = AioBot(api)
        asyncio.run(self.aio_bot.start())

    @property
    def api_key(self):
        load_dotenv()
        get_api = os.getenv("API")
        return get_api


if __name__ == '__main__':
    main = Main()
