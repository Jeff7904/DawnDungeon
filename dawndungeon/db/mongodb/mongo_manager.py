
from dawndungeon.db.mongodb.entities.session import Session
from dawndungeon.db.mongodb.entities.user import UserInDB, User
from dawndungeon.db.mongodb.entities.world import World
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult
from typing import Optional, Any, List, overload
from uuid import uuid4


class MongoManager:
    client: MongoClient
    database: Database
    collection: Collection

    def __init__(
        self,
        uri: str,
        database_name: str
    ):
        self.client = self._get_mongo_client(uri)
        self.database = self._get_mongo_database(database_name)

    def _get_mongo_client(self, uri: str) -> MongoClient:
        return MongoClient(uri)

    def _get_mongo_database(self, database_name: str) -> Database:
        return self.client[database_name]

    def _get_mongo_collection(self, collection_name) -> Collection:
        return self.database[collection_name]

    def get_worlds(self) -> List[World]:
        """Get all worlds from the database.

        Returns:
            List[World]: If nothing, then an empty list is returned.
        """
        return [
            World(**document)
            for document in self._get_mongo_collection('world').find()
        ]

    def get_world(self, id_: str="", random: bool=False) -> Optional[World]:
        """Get a world from the database.

        Args:
            id (str): The world id.

        Returns:
            World: The world dataclass.
        """
        collection: Collection[Any] = self._get_mongo_collection('worlds')

        if random is True:
            if collection.count_documents({}) == 0:
                return None

            document: Optional[Any] = collection.find().next()
        else:
            document: Optional[Any] = collection.find_one({ '_id': id_ })

        if document is None:
            return None

        world: World = World(**document)
        return world

    def get_user(self, username: str) -> Optional[UserInDB]:
        """Get a user from the database.

        Args:
            username (str): The username.

        Returns:
            Optional[UserInDB]: If nothing, then None is returned.
        """
        document: Optional[Any] = self._get_mongo_collection('users').find_one({ 'username': username })

        if document is None:
            return None

        user: UserInDB = UserInDB(**document)
        return user

    def insert_user(self, user: UserInDB) -> None:
        """Insert a user into the database.

        Args:
            user (UserInDB): The user dataclass.

        Raises:
            Exception: User already exists.
        """
        document: Optional[Any] = self._get_mongo_collection('users').find_one({ 'username': user.username })

        if document is not None:
            raise Exception('User already exists')

        user_dict: dict = user.dict()
        user_dict["id_"] = str(uuid4())
        user_dict["_id"] = user_dict["id_"]

        self._get_mongo_collection('users').insert_one(user_dict)

    def get_user_sessions(self, user: User) -> List[Session]:
        """Get a user's sessions from the database.

        Args:
            user (UserInDB): The user dataclass.

        Returns:
            List[Session]: If nothing, then an empty list is returned.
        """
        user_db: Optional[UserInDB] = self.get_user(user.username)
        if user_db is None:
            return []

        return [
            Session(**document)
            for document in self._get_mongo_collection('sessions').find({ 'user_id': user_db.id_ })
        ]

    def update_session(self, session: Session) -> None:
        """Insert a session into the database.

        Args:
            session (Session): The session dataclass.
        """
        self._get_mongo_collection('sessions') \
            .update_one({ '_id': session.id_ }, { '$set': session.dict() }, upsert=True)
