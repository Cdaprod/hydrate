"""
And here's how you can use it in your Jupyter notebook:

```python
from hydrate import main

# Define the URLs and bucket name
urls = ["https://example.com", "https://another-example.com"]
bucket_name = "cda-datasets"

# Call the main function from the hydrate.py script
main(urls, bucket_name)
```

In the notebook, you import the main function from the hydrate.py script. Then, you define the urls and bucket_name variables with the desired values. Finally, you call the main function, passing the urls and bucket_name as arguments.
This approach allows you to use the hydrate.py script as a modular component within your notebook, providing the necessary input directly from the notebook environment.
Make sure that the hydrate.py script and the notebook are in the same directory, so that the notebook can import the script correctly.
"""
from dotenv import load_dotenv
import requests
from minio import Minio
import weaviate
import os
import tempfile
import re
from unstructured.partition.auto import partition
import io
from pydantic import BaseModel, Field, validator
from typing import List, Optional

load_dotenv()  # This loads the environment variables from .env file

class ClientConfig(BaseModel):
    minio_endpoint: str = os.getenv('MINIO_ENDPOINT', 'play.min.io:443')
    minio_access_key: str = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
    minio_secret_key: str = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
    weaviate_endpoint: str = os.getenv('WEAVIATE_ENDPOINT', 'http://localhost:8080')

class MinioClient(BaseModel):
    config: ClientConfig = Field(default_factory=ClientConfig)

    @property
    def client(self) -> Minio:
        return Minio(
            self.config.minio_endpoint,
            access_key=self.config.minio_access_key,
            secret_key=self.config.minio_secret_key,
            secure=True  # Set to False if you are not using https
        )

class WeaviateClient(BaseModel):
    config: ClientConfig = Field(default_factory=ClientConfig)

    @property
    def client(self) -> weaviate.Client:
        return weaviate.Client(
            url=self.config.weaviate_endpoint,
            timeout_config=(5, 15)
        )

class Document(BaseModel):
    source: str
    content: str

    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v

class DocumentProcessor:
    def __init__(self, minio_client: MinioClient, weaviate_client: WeaviateClient):
        self.minio_client = minio_client
        self.weaviate_client = weaviate_client

    def sanitize_url_to_object_name(self, url):
        clean_url = re.sub(r'^https?://', '', url)
        clean_url = re.sub(r'[^\w\-_\.]', '_', clean_url)
        return clean_url[:250] + '.txt'

    def prepare_text_for_tokenization(self, text):
        clean_text = re.sub(r'\s+', ' ', text).strip()
        return clean_text

    def store_in_minio(self, url, bucket_name) -> Optional[str]:
        object_name = self.sanitize_url_to_object_name(url)
        
        exists = self.minio_client.client.bucket_exists(bucket_name) and \
            any(obj.object_name == object_name for obj in self.minio_client.client.list_objects(bucket_name, prefix=object_name, recursive=True))
        
        if exists:
            print(f"'{object_name}' already exists in MinIO bucket '{bucket_name}'. Skipping.")
            return None

        try:
            response = requests.get(url)
            response.raise_for_status()
            html_content = io.BytesIO(response.content)
            elements = partition(file=html_content, content_type="text/html")
            combined_text = "\n".join([e.text for e in elements if hasattr(e, 'text')])
            combined_text = self.prepare_text_for_tokenization(combined_text)

            with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".txt") as tmp_file:
                tmp_file.write(combined_text)
                tmp_file_path = tmp_file.name

            self.minio_client.client.fput_object(bucket_name, object_name, tmp_file_path)
            print(f"Stored '{object_name}' in MinIO bucket '{bucket_name}'.")
            os.remove(tmp_file_path)
            return object_name

        except requests.RequestException as e:
            print(f"Failed to fetch URL {url}: {e}")
        except Exception as e:
            print(f"Error processing {url}: {e}")
        
        return None

    def process_documents_in_minio(self, bucket_name, processed_object_names):
        for object_name in processed_object_names:
            print(f"Processing document: {object_name}")
            file_path = object_name
            self.minio_client.client.fget_object(bucket_name, object_name, file_path)
            elements = partition(filename=file_path)
            text_content = "\n".join([e.text for e in elements if hasattr(e, 'text')])
            data_object = Document(source=object_name, content=text_content)
            self.weaviate_client.client.data_object.create(data_object.dict(), "Document")
            print(f"Inserted document '{object_name}' into Weaviate.")
            os.remove(file_path)
            print(f"MinIO and Weaviate have ingested '{object_name}'! :)")

    ## v0.1.0 - Latest working from Juno (Modular usage)
    # def fetch_and_process_urls(self, urls, bucket_name):
    #     processed_object_names = []  # Track successfully processed URLs

    #     if not self.minio_client.client.bucket_exists(bucket_name):
    #         self.minio_client.client.make_bucket(bucket_name)
    #         print(f"Bucket '{bucket_name}' created.")

    #     for url in urls:
    #         object_name = self.store_in_minio(url, bucket_name)
    #         if object_name:
    #             processed_object_names.append(object_name)

    #     if processed_object_names:
    #         self.process_documents_in_minio(bucket_name, processed_object_names)
    #     else:
    #         print("No new documents to process.")

# # Example usage
# if __name__ == "__main__":
#     config = ClientConfig()
#     minio_client = MinioClient(config=config)
#     weaviate_client = WeaviateClient(config=config)

#     processor = DocumentProcessor(minio_client, weaviate_client)

#     urls = ["https://blog.min.io/author/david-cannan"]
#     bucket_name = "cda-datasets"
#     processor.fetch_and_process_urls(urls, bucket_name)

## 0.1.0 - Latest working from Juno (Modular usage) 
# def main(urls, bucket_name):
#     config = ClientConfig()
#     minio_client = MinioClient(config=config)
#     weaviate_client = WeaviateClient(config=config)

#     processor = DocumentProcessor(minio_client, weaviate_client)
#     processor.fetch_and_process_urls(urls, bucket_name)

## For GitHub Tailscale (tags=ci)
def fetch_and_process_urls(self, urls, bucket_name, log_file_path):
    processed_object_names = []  # Track successfully processed URLs
    with open(log_file_path, 'a') as log_file:
        if not self.minio_client.client.bucket_exists(bucket_name):
            self.minio_client.client.make_bucket(bucket_name)
            log_file.write(f"Bucket '{bucket_name}' created.\n")

        for url in urls:
            object_name = self.store_in_minio(url, bucket_name)
            if object_name:
                processed_object_names.append(object_name)
                log_file.write(f"Processed and stored: {url} -> {object_name}\n")
            else:
                log_file.write(f"Failed or skipped: {url}\n")

        if processed_object_names:
            self.process_documents_in_minio(bucket_name, processed_object_names, log_file)

def main(urls_file, bucket_name, log_file_path):
    config = ClientConfig()
    minio_client = MinioClient(config=config)
    weaviate_client = WeaviateClient(config=config)

    processor = DocumentProcessor(minio_client, weaviate_client)
    processor.fetch_and_process_urls(urls, bucket_name, log_file_path)
