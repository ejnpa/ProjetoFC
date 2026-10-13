terraform {
    required_providers {
        docker = {
            source="kreuzwerker/docker"
            version="~>3.0.1"
        }
    }
}

provider "docker"{
    host="tcp://100.89.13.43:2375"
}

resource "docker_image" "postgres"{
    name="postgres:15"
    keep_locally=true
}

resource "docker_image" "azurite"{
    name="mcr.microsoft.com/azure-storage/azurite:latest"
    keep_locally=true
}

resource "docker_volume" "pgdata"{
    name="pgdata"
}

resource "docker_volume" "azurite_data"{
    name="azurite_data"
}

resource "docker_container" "executiva_db"{
    name="executiva_db"
    image=docker_image.postgres.image_id

    env=[
        "POSTGRES_USER=admin",
        "POSTGRES_PASSWORD=admin",
        "POSTGRES_DB=executiva" 
    ]

    ports{
        internal=5432
        external=5432
    }

    volumes{
        container_path="/var/lib/postgresql/data"
        volume_name=docker_volume.pgdata.name
    }    
}

resource "docker_container" "azurite_storage"{
    name="azurite_storage"
    image=docker_image.azurite.image_id

    env = [
        "AZURITE_SKIP_API_VERSION_CHECK=true"
    ]

    ports{
        internal=10000
        external=10000
    }

    ports{
        internal=10001
        external=10001
    }

    ports{
        internal=10002
        external=10002
    }

    volumes{
        container_path="/workspace"
        volume_name=docker_volume.azurite_data.name
    }
}