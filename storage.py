import os
from  azure.storage.blob import BlobServiceClient


AZURE_CONNECTION_STRING = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
CONTAINER_NAME = "notes"

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

try:
    container_client = blob_service_client.create_container(CONTAINER_NAME)
except Exception:
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)  
    
    
def upload_files_to_storage (data:bytes, filename:str):
    blob_client = container_client.get_blob_client(blob = filename) 
    blob_client.upload_blob(data, overwrite=True)
    return f"http://127.0.0.1:10000/devstoreaccount1/{CONTAINER_NAME}/{filename}"

def download_files_from_storage(filename:str) -> bytes:
    blob_client = container_client.get_blob_client(blob = filename)
    
    return blob_client.download_blob().readall()

def delete_file_from_storage(filename:str):
    blob_client = container_client.get_blob_client(blob = filename)
    blob_client.delete_blob(delete_snapshots="include")