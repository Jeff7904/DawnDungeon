"""DawnDungeon is a text-based RPG game.
"""

__version__ = "0.0.0"

from dawndungeon.configs.config_manager import ConfigManager
from dawndungeon.db.mongodb.mongo_manager import MongoManager
from dawndungeon.db.pineconedb.pinecone_manager import PineconeManager
# from aioredis import Redis

config: ConfigManager = ConfigManager()
mongodb: MongoManager = MongoManager(
    config.get("MONGODB_URI"), config.get("MONGODB_DATABASE_NAME")
)
pineconedb: PineconeManager = PineconeManager(
    config.get("PINECONE_API_KEY"), config.get("PINECONE_ENVIRONMENT")
)
# aioredisdb: Redis = Redis(host=config.get("REDIS_HOST"), port=config.get("REDIS_PORT"))

__all__ = ["__version__"]
