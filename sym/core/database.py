""" Bot's database using pymongo """

import json
from typing import Any, Mapping

import dns.resolver
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from sym.config import Config
from sym.core import logger

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

database = Config.DB_URL

if database:
    DB_CLIENT = AsyncIOMotorClient(database)
    db_name = Config.DB_NAME
    db_client = DB_CLIENT[db_name]
else:
    DB_CLIENT = db_client = None


class Collection(AsyncIOMotorCollection):

    def __init__(self, name: str, log: bool = False, **kwargs: Any):
        self.log = log
        self.collection_name = name
        super().__init__(db_client, name, **kwargs)

    async def dumps(self) -> str:
        string = ""
        async for data in self.find():
            string += json.dumps(data, indent=4) + "\n"
        return string

    async def add(self, data: dict) -> int:
        """ Add an entry to the database """
        json_ = json.dumps(data, indent=4)
        if "_id" in data.keys():
            found = await self.find_one(data['_id'])
        else:
            raise self.InvalidDatabaseQuery("`Mandatory key '_id' not found in data.`")
        if not found:
            entry = await self.insert_one(data)
            if self.log:
                logger.Logger.console_log(f"Entry added to name '{self.collection_name}':\n\n{json_}")
        else:
            await self.delete_one(found)
            entry = await self.insert_one(data)
            if self.log:
                logger.Logger.console_log(f"Entry updated to name '{self.collection_name}':\n\n{json_}")
        return entry.inserted_id

    async def get(self, query: dict) -> Mapping[str, Any] | None:
        found = await self.find_one(query)
        if found:
            return found
        return None

    async def remove(self, entry: str|dict) -> bool:
        """ Remove an entry from the database """
        id_ = entry['_id'] if isinstance(entry, dict) and "_id" in entry.keys() else entry
        found = await self.find_one({"_id": id_})
        json_ = json.dumps(found, indent=4)
        if found:
            await self.delete_one(found)
            if self.log:
                logger.Logger.console_log(f"Entry removed from collection '{self.collection_name}:\n\n{json_}")
            return True
        else:
            return False

    async def drop(
        self,
        session = None,
        comment = None,
        encrypted_fields = None
    ):
        """ Collection drop """
        await super().drop(session, comment, encrypted_fields)
        if self.log:
            logger.Logger.console_log(f"The entries in collection '{self.collection_name}'.")

            
    class InvalidDatabaseQuery(Exception):
        
        def __init__(self, message: str):
            super().__init__(message)