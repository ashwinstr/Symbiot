""" Bot's database using pymongo """

import enum
import json
import logging
from typing import Any

import dns.resolver
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from sym.config import Config

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

database = Config.DB_URL

if database:
    DB_CLIENT = AsyncIOMotorClient(database)
    db_name = Config.DB_NAME
    db_client = DB_CLIENT[db_name]
else:
    DB_CLIENT = db_client = None


class DatabaseLogLevel(enum.Enum):
    PRINT = print
    # LOG_TO_CHANNEL = ...
    TO_LOGS = logging.info


class Collection(AsyncIOMotorCollection):

    def __init__(self, name: str, log: bool = False, log_level: DatabaseLogLevel = DatabaseLogLevel.PRINT, **kwargs: Any):
        self.log = log
        self.logger = log_level.value
        self.collection_name = name
        super().__init__(db_client, name, **kwargs)

    @property
    async def dumps(self) -> str:
        string = ""
        async for data in self.find():
            string += json.dumps(data) + "\n"
        return string

    async def add(self, data: dict) -> int:
        """ Add an entry to the database """
        json_ = json.dumps(data, indent=4)
        found = await self.find_one({"_id": data["_id"]})
        if not found:
            entry = await self.insert_one(data)
            if self.log:
                self.logger(f"Entry added to name '{self.collection_name}':\n\n{json_}")
        else:
            await self.delete_one(found)
            entry = await self.insert_one(data)
            if self.log:
                self.logger(f"Entry updated to name '{self.collection_name}':\n\n{json_}")
        return entry.inserted_id

    async def remove(self, entry: int|dict) -> bool:
        """ Remove an entry from the database """
        id_ = entry if isinstance(entry, int) else entry['_id']
        if isinstance(id_, int):
            found = await self.find_one({"_id": id_})
            json_ = json.dumps(found, indent=4)
            if found:
                await self.delete_one(found)
                if self.log:
                    self.logger(f"Entry removed from collection '{self.collection_name}:\n\n{json_}")
                return True
            else:
                return False
        else:
            raise self.InvalidDatabaseQuery("Data ID is of unknown type.")

    async def drop(
        self,
        session = None,
        comment = None,
        encrypted_fields = None
    ):
        """ Collection drop """
        await super().drop(session, comment, encrypted_fields)
        if self.log:
            self.logger(f"The entries in collection '{self.collection_name}'.")

            
    class InvalidDatabaseQuery(Exception):
        
        def __init__(self, message: str):
            super().__init__(message)