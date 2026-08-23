from config.aws_config import get_s3_client, get_bucket_name
from botocore.exceptions import ClientError
import os

class S3Service:
    @staticmethod
    def upload_file(file_path, object_name=None):
        """Upload a file to an S3 bucket"""
        if object_name is None:
            object_name = os.path.basename(file_path)

        s3_client = get_s3_client()
        bucket_name = get_bucket_name()
        if not bucket_name:
            print("S3_BUCKET_NAME not set.")
            return False

        try:
            s3_client.upload_file(file_path, bucket_name, object_name)
            
            # Construct URL (assumes public bucket or pre-signed will be used later)
            # Standard S3 URL format
            url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
            return url
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return None

    @staticmethod
    def generate_presigned_url(object_name, expiration=3600):
        """Generate a presigned URL to share an S3 object"""
        s3_client = get_s3_client()
        bucket_name = get_bucket_name()
        
        try:
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': bucket_name,
                                                                'Key': object_name},
                                                        ExpiresIn=expiration)
            return response
        except ClientError as e:
            print(f"Error generating presigned url: {e}")
            return None
            
    @staticmethod
    def download_file(object_name, download_path):
        """Download a file from S3 to a local path"""
        s3_client = get_s3_client()
        bucket_name = get_bucket_name()
        
        try:
            s3_client.download_file(bucket_name, object_name, download_path)
            return True
        except ClientError as e:
            print(f"Error downloading from S3: {e}")
            return False

    @staticmethod
    def delete_file(object_name):
        s3_client = get_s3_client()
        bucket_name = get_bucket_name()
        try:
            s3_client.delete_object(Bucket=bucket_name, Key=object_name)
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False
