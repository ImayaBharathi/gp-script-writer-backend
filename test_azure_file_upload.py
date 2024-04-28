from azure.storage.blob import BlobClient

blob = BlobClient.from_connection_string(
                    container_name="scripts-uploaded",
                    blob_name=f"13dew3423-32432rd2432-23423/311141/main.py",
                    conn_str="DefaultEndpointsProtocol=https;AccountName=gpbackendutilites;AccountKey=fsgXYOoVlQo5lJktRw0pk3AeXrAi9P8/uCshN4oiF1LQ8IVRDQXShO7p3MdpmNTHzsLxFNVSz5Tk+ASt1aNbWA==;EndpointSuffix=core.windows.net")
with open("main.py", "r") as e:
    blob.upload_blob(e.read())