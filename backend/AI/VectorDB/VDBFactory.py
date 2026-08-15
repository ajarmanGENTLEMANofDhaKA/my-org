from .providers import QdrantProvider
from .VDBEnums import VectorDBType
from utils.enums import ResponseSignals

class VDBProviderFactory:
    def __init__(self, config):
        self.config = config

    def create(self, provider: str):
        if provider == VectorDBType.QDRANT.value:
            return QdrantProvider(
                host= self.config.VECTOR_DB_HOST,
                port= self.config.VECTOR_DB_PORT,
                grpc_port= self.config.VECTOR_DB_GRPC_PORT,
                distance_metric= self.config.VECTOR_DB_DISTANCE_METHOD,
            )
        else:
            raise ValueError(ResponseSignals.VDB_UNSUPPORTED_PROVIDER.value)
        