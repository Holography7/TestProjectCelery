from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from settings import DATABASE, MONGO_URI

mongo_client = AsyncIOMotorClient(MONGO_URI)
mongo_engine = AIOEngine(client=mongo_client, database=DATABASE)
