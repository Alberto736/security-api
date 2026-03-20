from contextlib import asynccontextmanager

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.settings import Settings


class Mongo:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        self._client = AsyncIOMotorClient(self._settings.mongo_uri)
        self._db = self._client[self._settings.mongo_db]

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
        self._client = None
        self._db = None

    @property
    def db(self) -> AsyncIOMotorDatabase:
        if self._db is None:
            raise RuntimeError("Mongo is not connected")
        return self._db


@asynccontextmanager
async def mongo_lifespan(mongo: Mongo):
    await mongo.connect()
    try:
        yield
    finally:
        await mongo.close()
