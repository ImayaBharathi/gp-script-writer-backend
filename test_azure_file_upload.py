from azure.storage.blob import BlobClient

blob = BlobClient.from_connection_string(
                    container_name="scripts-uploaded",
                    blob_name=f"13dew3423-32432rd2432-23423/311141/main.py",
                    conn_str="conntection string from environment")
with open("main.py", "r") as e:
    blob.upload_blob(e.read())