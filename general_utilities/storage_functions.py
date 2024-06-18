#storage_functions.py
import json
from azure.storage.blob import BlobServiceClient
from secrets import sh

def get_blob_service(blob_service_name=None):
    if not blob_service_name:
        blob_service_name = 'lzdev'
    return BlobServiceClient.from_connection_string(sh.blob_service_name)

def get_blob_container(container_name=None, blob_service_client=None, blob_service_name=None):
    if not container_name:
        container_name = 'robs-playground'
    if not blob_service_client and not blob_service_name:
        raise ValueError('Either blob_service_client or blob_service_name must be provided')
    if not blob_service_client:
        blob_service_client = get_blob_service(blob_service_name)
    return blob_service_client.get_container_client(container_name)

def get_blob_client(blob_name, container_client=None, container_name=None, blob_service_client=None, blob_service_name=None):
    if not blob_service_client:
        blob_service_client = get_blob_service(blob_service_name)
    if not container_client:
        container_client = get_blob_container(container_name=container_name, blob_service_client=blob_service_client)
    return container_client.get_blob_client(blob_name)