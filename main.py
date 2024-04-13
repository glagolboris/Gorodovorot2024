import os
from dotenv import load_dotenv


class Main:
    def __init__(self) -> None:
        print(self.api_key)

    @property
    def api_key(self):
        load_dotenv()
        get_api = os.getenv("API")
        return get_api


if __name__ == '__main__':
    main = Main()
