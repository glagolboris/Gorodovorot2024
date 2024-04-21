import asyncio
from sqlalchemy_aio import ASYNCIO_STRATEGY
from sqlalchemy import (
    Column, Integer, MetaData, Table, Text, create_engine, select)
from sqlalchemy.schema import CreateTable, DropTable


class asyncDb:
    def __init__(self, user, password):
        self.database_user = user
        self.user_password = password

    async def main(self):
        self.engine = create_engine(f'postgresql://{self.database_user}:{self.user_password}/gorodovorot')

