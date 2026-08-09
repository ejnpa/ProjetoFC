import os
from .IStorage import StorageInterface
from .LocalStorage import LocalStorage
from .GCPStorage import GCPStorage
from .AzureStorage import AzureStorage


def get_storage_provider() -> StorageInterface:
    provider = os.getenv("CLOUD_PROVIDER", "AZURE").upper()
    
    if provider == "LOCAL":
        return LocalStorage()
    elif provider == "GCP":
        return GCPStorage()
    elif provider == "AZURE":
        return AzureStorage()