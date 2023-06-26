
from dawndungeon import config, mongodb
from dawndungeon.api.prompts import (
    INIT_WORLD_TEMPLATE,
    EXECUTE_WORLD_TEMPLATE,
)
from dawndungeon.db.mongodb.entities.user import UserInDB
from dawndungeon.db.mongodb.entities.session import Session
from dawndungeon.db.mongodb.entities.world import World
from langchain import PromptTemplate
from langchain.chains import LLMChain, SequentialChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from streamlit.delta_generator import DeltaGenerator
from langchain.schema import HumanMessage, AIMessage
import streamlit as st
import json
from json import JSONDecodeError
from loguru import logger
from langchain.callbacks import get_openai_callback
from typing import Dict, List, Optional
import re
from textwrap import dedent
from langchain.schema import BaseMessage
from dawndungeon import pineconedb
from langchain.vectorstores import Pinecone
import pinecone
from pinecone import Index
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.agents import initialize_agent, Tool
from langchain.chains.retrieval_qa.base import BaseRetrievalQA


class StoryManager:
    def __init__(
        self,
        world: World,
        user: UserInDB,
        *,
        session: Optional[Session]=None,
        history: Optional[List[BaseMessage]]=None
    ):
        if session is None:
            session = Session(user_id=user.id_, world_id=world.id_)

        self.world: World = world
        self.user: UserInDB = user
        self.session: Session = session
        self._memory: ConversationBufferWindowMemory = ConversationBufferWindowMemory(
            k=10,
            return_messages=True,
        )

        if history is not None:
            self._set_memory(history)

        self.openai_llm: ChatOpenAI = ChatOpenAI(
            client=None,
            openai_api_key=config.get("OPENAI_API_KEY"),
            model="gpt-3.5-turbo",
            temperature=0.6,
        )
        self.openai_llm_16k: ChatOpenAI = ChatOpenAI(
            client=None,
            openai_api_key=config.get("OPENAI_API_KEY"),
            model="gpt-3.5-turbo-16k",
            temperature=0.6,
        )
        self.openai_embeddings: OpenAIEmbeddings = OpenAIEmbeddings(
            client=None,
            model="text-embedding-ada-002",
            openai_api_key=config.get("OPENAI_API_KEY"),
        )

        self.pinecone_namespace: str = self.session.id_
        self.pinecone_index: pinecone.Index = pineconedb.get_index(
            config.get("PINECONE_INDEX_NAME"),
            upsert=True,
        )
        self.vectorstore: Pinecone = Pinecone(
            index=self.pinecone_index,
            embedding_function=self.openai_embeddings.embed_query,
            text_key="text",
            namespace=self.pinecone_namespace,
        )

        self.retrieval_qa: BaseRetrievalQA = RetrievalQA.from_chain_type(
            llm=self.openai_llm_16k,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(),
        )

    def _get_tools(self) -> List[Tool]:
        knowledge_base: Tool = Tool(
            name="Knowledge Base",
            func=self.retrieval_qa.run,
            description="Use this tool when answering questions to get more information about the topic."
        )

        return [
            knowledge_base,
        ]

    def serialize(self) -> dict:
        history: List[dict] = [
            {
                **message.dict(),
                "type": message.type.lower() # "human" "ai"
            }
            for message in self._output_memory()
        ]

        return {
            "world": self.world.dict(),
            "user": self.user.hidden().dict(),
            "session": self.session.dict(),
            "memory": history,
        }

    @staticmethod
    def deserialize(data: dict) -> "StoryManager":
        history: List[BaseMessage] = [
            HumanMessage(**message) if message.get("type") == "human"
            else AIMessage(**message) if message.get("type") == "ai"
            else AIMessage(**message)
            for message in data["memory"]
        ]
        return StoryManager(
            World(**data["world"]),
            UserInDB(**data["user"]),
            session=Session(**data["session"]),
            history=history,
        )

    def _set_memory(self, history: List[BaseMessage]) -> None:
        self._memory.chat_memory.messages = history

    def _output_memory(self) -> List[BaseMessage]:
        return self._memory.chat_memory.messages

    @property
    def memory(self) -> ConversationBufferWindowMemory:
        return self._memory

    def get_storylines(self) -> str:
        """Returns the storylines for human to read.
        And also for AI references.
        """
        storylines = "\n\n".join(
            [
                "Action: " + history.content
                if isinstance(history, HumanMessage)
                else json.loads(history.content)["content"]

                for history in self.memory.load_memory_variables({})["history"]
                if (
                    isinstance(history, HumanMessage) or
                    isinstance(history, AIMessage)
                ) and
                    history.content != ""
            ]
        )
        return storylines

    def get_latest_messages(self) -> List[BaseMessage]:

        if len(self.memory.buffer) <= 1:
            return []

        return self.memory.buffer[-2:]

    def get_latest_metadata(self) -> dict:
        """Returns the latest metadata for AI to read.
        """
        if len(self.memory.buffer) == 0:
            return {}

        return json.loads(self.memory.buffer[-1].content)["metadata"]

    def _init_story(self) -> dict:
        """Initializes a new story.
        """
        starting_chain: LLMChain = LLMChain(
            llm=self.openai_llm_16k,
            prompt=INIT_WORLD_TEMPLATE,
            verbose=config.get("DEBUG"),
        )
        starting_sequence: SequentialChain = SequentialChain(
            chains=[starting_chain],
            input_variables=["world_name", "world_description"],
            verbose=config.get("DEBUG"),
        )

        while True:
            try:
                # Sometimes the AI returns invalid JSON, so we need to tell it to try again
                result: str = starting_sequence.run(
                    world_name=self.world.name,
                    world_description=self.world.description
                )
                return json.loads(result)
            except JSONDecodeError as err:
                logger.error(err)

    def execute(self, *, action: str="") -> dict:
        """Story execution.
        Generate the next storyline based on the action.
        """
        if len(self._memory.buffer) == 0:
            logger.debug("Initializing world...")
            with get_openai_callback() as cb:
                result: dict = self._init_story()
                self._memory.save_context({"human": ""}, {"ai": json.dumps(result)})
                logger.debug(f"Spent a total of {cb.total_tokens} tokens")
                return result

        logger.debug("Executing action...")
        story_chain: LLMChain = LLMChain(
            llm=self.openai_llm_16k,
            prompt=EXECUTE_WORLD_TEMPLATE,
            verbose=config.get("DEBUG"),
        )
        story_sequence: SequentialChain = SequentialChain(
            chains=[story_chain],
            input_variables=["storylines", "metadata", "action"],
            verbose=config.get("DEBUG"),
        )

        def __run(self) -> dict:
            while True:
                try:
                    result: str = story_sequence.run(
                        storylines=self.get_storylines(),
                        metadata=self.get_latest_metadata(),
                        action=action,
                    )
                    return json.loads(result)
                except JSONDecodeError as err:
                    logger.error(err)

        with get_openai_callback() as cb:
            result: dict = __run(self)
            self._memory.save_context({"human": action}, {"ai": json.dumps(result)})
            logger.debug(f"Spent a total of {cb.total_tokens} tokens")
            return result



    def save(self) -> None:
        """Save the story to the database.
        """
        raise NotImplementedError()
