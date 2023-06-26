
import pinecone
from loguru import logger


class PineconeManager:
    def __init__(self, api_key: str, environment: str, debug: bool=False):
        pinecone.init(
            api_key=api_key,
            environment=environment,
        )
        self.debug: bool = debug
        if self.debug:
            logger.debug(f"Indexes: {pinecone.list_indexes()}\nCollections: {pinecone.list_collections()}")

    def create_index(self, index_name: str, metric: str, dimension: int):
        pinecone.create_index(
            name=index_name,
            metric=metric,
            dimension=dimension,
        )

    def get_index(
        self,
        index_name: str,
        upsert: bool=False,
        metric: str="dotproduct",
        dimension: int=1536
    ) -> pinecone.Index:
        if index_name not in pinecone.list_indexes():
            if upsert:
                self.create_index(index_name, metric, dimension)

        index: pinecone.Index = pinecone.Index(index_name)
        if self.debug:
            logger.debug(f"Index: {index.describe_index_stats()}")

        return index

    # def get_grpc_index(self, index_name: str) -> pinecone.GRPCIndex:
    #     index: pinecone.GRPCIndex = pinecone.GRPCIndex(index_name)
    #     if self.debug:
    #         logger.debug(f"Index: {index.describe_index_stats()}")

    #     return index
