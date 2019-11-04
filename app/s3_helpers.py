import boto3

def upload_file(file_name, bucket):
    """
    Function to upload user avatars to S3 bucked
    """
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket)

    return response