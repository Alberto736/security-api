from contextlib import asynccontextmanager
import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.settings import Settings


class Mongo:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        try:
            self._client = AsyncIOMotorClient(
                self._settings.mongo_uri,
                serverSelectionTimeoutMS=5000,  # 5 seconds timeout
                connectTimeoutMS=5000,
                socketTimeoutMS=5000
            )
            # Test the connection
            await self._client.admin.command('ping')
            self._db = self._client[self._settings.mongo_db]
        except Exception as e:
            logging.warning(f"MongoDB connection failed: {e}")
            # Don't raise exception, allow API to work without MongoDB
            self._client = None
            self._db = None

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
        self._client = None
        self._db = None

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise RuntimeError("MongoDB not connected. Database operations are not available.")
        return self._db

    @property
    def is_connected(self) -> bool:
        return self._db is not None


@asynccontextmanager
async def mongo_lifespan(mongo: Mongo):
    await mongo.connect()
    try:
        yield
    finally:
        await mongo.close()
