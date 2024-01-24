from loguru import logger
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import uuid

# Azure Storage Account connection string
AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=gpuicomponents;AccountKey=PrW5sG4NaCAHl6N4XUVX04uPxAbcGyEjDSVbs8HJlYLDmk+jG0f6LmQ/64tLMwKHcov0Dd/NdYlW+AStGDOoaw==;EndpointSuffix=core.windows.net"
connection_string = "DefaultEndpointsProtocol=https;AccountName=gpuicomponents;AccountKey=PrW5sG4NaCAHl6N4XUVX04uPxAbcGyEjDSVbs8HJlYLDmk+jG0f6LmQ/64tLMwKHcov0Dd/NdYlW+AStGDOoaw==;EndpointSuffix=core.windows.net"

def log_to_azure_storage(user_id, message: str, system_logs: bool):
    filename = "audit.log"

    # Create a BlobServiceClient to interact with the Blob service
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

    if system_logs:
        # this si 
        container_name_parent = "system-logs"
    else:
        container_name_parent = "user-logs/"+str(user_id)
    
    try:        
        # Use get_container_client on the parent container to create the nested user container
        container_client_user = blob_service_client.get_container_client(container_name_parent)


        # Upload the log message to the blob in the user's container
        blob_client = container_client_user.get_blob_client(filename)
        blob_client.upload_blob(message)

        logger.info(f"Log message uploaded to Azure Storage for user {user_id}")

    except Exception as e:
        logger.error(f"Failed to upload log message for user {user_id}. Error: {e}")

# # Example of how to use the log_to_azure_storage method
# user_id = "123e4567-e89b-12d3-a456-426614174001"  # Replace with the actual user ID
# log_message = "This is a sample log message."

# log_to_azure_storage(user_id, log_message)
# log_to_azure_storage("user_id", "something", True)