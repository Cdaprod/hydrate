from langchain.llms import OpenAI
from langchain.runnables import Runnable, RunnableLambda
from dotenv import load_dotenv
import requests
from minio import Minio
import weaviate
from pydantic import BaseModel, Field
import os
import io
from unstructured.partition.auto import partition
import tempfile
import re

load_dotenv()

class ClientConfig(BaseModel):
    minio_endpoint: str = os.getenv('MINIO_ENDPOINT', 'play.min.io:443')
    minio_access_key: str = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
    minio_secret_key: str = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
    weaviate_endpoint: str = os.getenv('WEAVIATE_ENDPOINT', 'http://localhost:8080')

class FetchURL(Runnable):
    def _call(self, url: str) -> str:
        response = requests.get(url)
        response.raise_for_status()
        return response.content

class ProcessContent(Runnable):
    def _call(self, content: bytes) -> str:
        elements = partition(io.BytesIO(content), content_type="text/html")
        return "\n".join(e.text for e in elements if hasattr(e, 'text'))

class StoreInMinio(Runnable):
    def __init__(self, config: ClientConfig):
        self.client = Minio(
            config.minio_endpoint,
            access_key=config.minio_access_key,
            secret_key=config.minio_secret_key,
            secure=True
        )

    def _call(self, bucket_name: str, content: str, object_name: str) -> None:
        with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
            tmp_file.write(content.encode())
            tmp_file.flush()
            self.client.fput_object(bucket_name, object_name, tmp_file.name)

class InsertInWeaviate(Runnable):
    def __init__(self, config: ClientConfig):
        self.client = weaviate.Client(
            url=config.weaviate_endpoint,
            timeout_config=(5, 15)
        )

    def _call(self, document: str, object_name: str) -> None:
        self.client.data_object.create({"content": document, "source": object_name}, "Document")

# Define Chain
class HydrateChain(Chain):
    def __init__(self, config: ClientConfig, bucket_name: str):
        self.fetch = FetchURL()
        self.process = ProcessContent()
        self.store = StoreInMinio(config)
        self.insert = InsertInWeaviate(config)
        self.bucket_name = bucket_name

    def _call(self, url: str) -> None:
        content = self.fetch | self.process | RunnableLambda(lambda x: x)  # Example of using RunnableLambda for transformation if needed
        object_name = re.sub(r'\W+', '_', url)[:255] + '.txt'
        self.store(self.bucket_name, content, object_name)
        self.insert(content, object_name)

# Example Usage
if __name__ == "__main__":
    config = ClientConfig()
    urls = ["https://example.com", "https://another-example.com"]
    hydrate_chain = HydrateChain(config, "cda-datasets")
    for url in urls:
        hydrate_chain(url)