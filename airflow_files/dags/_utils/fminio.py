

from dotenv import load_dotenv

import sys
import os
sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))

#Load env file
env_path_envFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '_env', '.env'))
load_dotenv(env_path_envFolder)


def upload_file(file, name, client, provider_info):

    BUCKET_NAME = os.getenv('MINIO_BUCKET')

    # The destination bucket and filename on the MinIO server
    destination_file = f"{provider_info['naas_user']}/{name}"
    source_file = file

    # Make the bucket if it doesn't exist.
    found = client.bucket_exists(BUCKET_NAME)
    if not found:
        client.make_bucket(BUCKET_NAME)
        print("Created bucket", BUCKET_NAME)
    else:
        print("Bucket", BUCKET_NAME, "already exists")

    # Upload the file, renaming it in the process
    client.fput_object(
        BUCKET_NAME, destination_file, source_file,
    )
    print(
        source_file, "successfully uploaded as object",
        destination_file, "to bucket", BUCKET_NAME,
    )


def download_file(file, name, client, provider_info):

    BUCKET_NAME = os.getenv('MINIO_BUCKET')
    NAAS_USER = provider_info['naas_user']
    
    source_file = f"{NAAS_USER}/{name}"

    destination_file = file

    # check if the bucket exist.
    found = client.bucket_exists(BUCKET_NAME)
    if not found:
        print("Bucket do not found", BUCKET_NAME)
    else:
        print("Bucket", BUCKET_NAME, " exists")

    # Upload the file, renaming it in the process
    client.fget_object(
        BUCKET_NAME, source_file, destination_file
    )
    print(
        source_file, "successfully downloaded in",
        destination_file, "from bucket", BUCKET_NAME,
    )

def fTest():
    print('This is a test function')