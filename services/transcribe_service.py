from config.aws_config import get_transcribe_client, get_bucket_name
import time
import urllib.request
import json
import os

class TranscribeService:
    @staticmethod
    def start_transcription(job_name, file_uri, language_code="en-US"):
        transcribe = get_transcribe_client()
        try:
            # We output to the same bucket
            bucket_name = get_bucket_name()
            transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': file_uri},
                MediaFormat='mp4', # Defaulting to mp4, but AWS Transcribe supports multiple
                LanguageCode=language_code,
                OutputBucketName=bucket_name,
                OutputKey=f"transcripts/{job_name}.json"
            )
            return True
        except Exception as e:
            print(f"Error starting transcription: {e}")
            return False

    @staticmethod
    def get_transcription_status(job_name):
        transcribe = get_transcribe_client()
        try:
            response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            return response['TranscriptionJob']['TranscriptionJobStatus']
        except Exception as e:
            print(f"Error getting status: {e}")
            return "FAILED"

    @staticmethod
    def wait_for_transcription(job_name):
        """Wait synchronously for transcription to finish. (For background worker)"""
        while True:
            status = TranscribeService.get_transcription_status(job_name)
            if status in ['COMPLETED', 'FAILED']:
                return status == 'COMPLETED'
            time.sleep(10)
