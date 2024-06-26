import json
from azure.storage.blob import BlobServiceClient
from my_secrets import MySecrets

class StorageFunctions:
    
    @staticmethod
    def act_on_blob(blob_name, action='read', container_name='xxxxxx', account='usafactslzdev', data=None, metadata=None):
        blob_client = StorageFunctions.get_blob_client(blob_name, container_name, account)
        
        actions = {
            'read': lambda: blob_client.download_blob().readall(),
            'delete': blob_client.delete_blob,
            'list': lambda: [blob.name for blob in blob_client.list_blobs()],
            'write': lambda: blob_client.upload_blob(data),
            'properties': blob_client.get_blob_properties,
            'read_metadata': blob_client.get_blob_metadata,
            'write_metadata': lambda: blob_client.set_blob_metadata(metadata),
            'delete_metadata': blob_client.delete_blob_metadata,
            'change_properties': lambda: blob_client.set_http_headers(content_settings=metadata)
        }

        if action in actions:
            return actions[action]()
        else:
            return 'Invalid action'

    @staticmethod
    def get_blob_client(blob_name, container_name='xxxxxx', account='usafactslzdev'):
        blob_service_client = BlobServiceClient.from_connection_string(MySecrets.get_secret(f"{account}_connection_string"))
        container_client = blob_service_client.get_container_client(container_name)
        return container_client.get_blob_client(blob_name)

    @staticmethod
    def get_blob_url(blob_name, container_name='xxxxxx', account='usafactslzdev'):
        blob_client = StorageFunctions.get_blob_client(blob_name, container_name, account)
        return blob_client.url

    @staticmethod
    def generate_sas_url(blob_name, container_name='xxxxxx', account='usafactslzdev'):
        blob_client = StorageFunctions.get_blob_client(blob_name, container_name, account)
        sas_token = blob_client.generate_shared_access_signature()
        return f"{blob_client.url}?{sas_token}"

    @staticmethod
    def get_container_client(container_name, account='usafactslzdev'):
        blob_service_client = BlobServiceClient.from_connection_string(MySecrets.get_secret(f"{account}_connection_string"))
        return blob_service_client.get_container_client(container_name)

    @staticmethod
    def act_on_container(container_name, action='list', account='usafactslzdev'):
        container_client = StorageFunctions.get_container_client(container_name, account)
        
        actions = {
            'list': lambda: [blob.name for blob in container_client.list_blobs()],
            'create': container_client.create_container,
            'delete': container_client.delete_container
        }

        if action in actions:
            return actions[action]()
        else:
            return 'Invalid action'

    @staticmethod
    def get_container_url(container_name, account='usafactslzdev'):
        container_client = StorageFunctions.get_container_client(container_name, account)
        return container_client.url

    @staticmethod
    def generate_container_sas_url(container_name, account='usafactslzdev'):
        container_client = StorageFunctions.get_container_client(container_name, account)
        sas_token = container_client.generate_shared_access_signature()
        return f"{container_client.url}?{sas_token}"

    @staticmethod
    def get_blob_service_client(account='usafactslzdev'):
        return BlobServiceClient.from_connection_string(MySecrets.get_secret(f"{account}_connection_string"))

    @staticmethod
    def act_on_account(account, action='list'):
        blob_service_client = StorageFunctions.get_blob_service_client(account)
        
        if action == 'list':
            return [container.name for container in blob_service_client.list_containers()]
        else:
            return 'Invalid action'
