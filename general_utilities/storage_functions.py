#storage_functions.py
import json
from azure.storage.blob import BlobServiceClient
from secrets import sh


def blob(blob_name, data=None, action='read/write', container_name='spiderwalker', account='lzdev'):
    """
    Azure Blob Storage.

    """
    try:
        
        # Retrieve the Azure Blob connection string from secrets
        connection_string = sh.account
        
        # Initialize the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get the container client
        container_client = blob_service_client.get_container_client(container_name)
        
        # Get the blob client
        blob_client = container_client.get_blob_client(blob_name)
        if data and action == 'read/write':
            # Upload the data
            blob_client.upload_blob(json.dumps(data, ensure_ascii=False, indent=4), overwrite=True)
            print(f"Successfully uploaded to Azure Blob Storage: {blob_name}")
            return blob_name
        elif action == 'read/write':
            # Download the data
            data = json.loads(blob_client.download_blob().readall())
            print(f"Successfully downloaded from Azure Blob Storage: {blob_name}")
            return data
        else:
            print(f"Invalid action: {action}")
    except Exception as e:
        print(f"Failed working with Azure Blob Storage: {e}")

def list_lzdev(container_name='spiderwalker'):
    """
    Lists all the blobs in a container.

    Args:
        container_name (str, optional): The name of the container. If not provided, it will use the default container from secrets.

    Returns:
        list: A list of blob names.
    """
    try:
        
        # Retrieve the Azure Blob connection string from secrets
        connection_string = sh.lzdev
        
        # Initialize the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get the container client
        container_client = blob_service_client.get_container_client(container_name)
        
        # List the blobs
        blob_list = container_client.list_blobs()
        blobs = [blob.name for blob in blob_list]
        print(f"Successfully listed blobs in Azure Blob Storage: {container_name}")
        return blobs
    except Exception as e:
        print(f"Failed to list blobs in Azure Blob Storage: {e}")
        return None
def remove_from_lzdev(blob_name, container_name='spiderwalker'):
    """
    Removes a blob from Azure Blob Storage.

    Args:
        blob_name (str): The name of the blob to remove.
        container_name (str, optional): The name of the container. If not provided, it will use the default container from secrets.

    Returns:
        None
    """
    try:
        
        # Retrieve the Azure Blob connection string from secrets
        connection_string = sh.lzdev
        
        # Initialize the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Get the container client
        container_client = blob_service_client.get_container_client(container_name)
        
        # Get the blob client
        blob_client = container_client.get_blob_client(blob_name)
        
        # Delete the blob
        blob_client.delete_blob()
        print(f"Successfully removed from Azure Blob Storage: {blob_name}")
    except Exception as e:
        print(f"Failed to remove from Azure Blob Storage: {e}")
# Example usage:
# from storage import lzdev
# data = {"example_key": "example_value"}
# lzdev("example_blob.json", data)
