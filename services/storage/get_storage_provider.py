import os
from .strategy import StorageStrategy
from .local_storage import LocalStorage
from .gcp_storage import GCPStorage
from .azure_storage import AzureStorage


def get_storage_provider() -> StorageStrategy:
    provider = os.getenv("CLOUD_PROVIDER", "AZURE").upper()
    
    if provider == "LOCAL":
        return LocalStorage()
    elif provider == "GCP":
        return GCPStorage()
    elif provider == "AZURE":
        return AzureStorage()