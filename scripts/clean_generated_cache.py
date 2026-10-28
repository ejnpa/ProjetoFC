from database import sessionLocal
from storage import get_storage_provider
from repositories.generated_cache_repository import GeneratedCacheRepository
from config import settings


def main() -> None:
    db = sessionLocal()
    
    try:
        storage = get_storage_provider()
        repo = GeneratedCacheRepository(
            db=db,
            ttl_days= settings.generated_cache_ttl_days
        )

        deleted_count = repository.delete_expired(storage)
        print(f"Artefactos expirados eliminados: {deleted_count}")
    finally:
        db.close()
        
if __name__ == "__main__": 
    main()
