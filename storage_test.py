from azure.storage.blob import BlobServiceClient

# A tua string com o IP do Tailscale
connection_string = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://100.89.13.43:10000/devstoreaccount1;QueueEndpoint=http://100.89.13.43:10001/devstoreaccount1;TableEndpoint=http://100.89.13.43:10002/devstoreaccount1;"

try:
    print("A ligar ao Azurite no Desktop via Tailscale...")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Tenta criar um contentor de teste
    nome_contentor = "teste-ligacao"
    container_client = blob_service_client.get_container_client(nome_contentor)
    
    if not container_client.exists():
        container_client.create_container()
        print(f"✅ SUCESSO! Contentor '{nome_contentor}' criado no desktop.")
    else:
        print(f"✅ SUCESSO! Ligação estabelecida. O contentor '{nome_contentor}' já existe.")

except Exception as e:
    print(f"❌ ERRO de ligação: {e}")