from config.db import get_db
import datetime
import uuid

class Video:
    @staticmethod
    def get_collection():
        db = get_db()
        return db['videos'] if db is not None else None
        
    @staticmethod
    def get_logs_collection():
        db = get_db()
        return db['processing_logs'] if db is not None else None

    @staticmethod
    def create_video(user_id, file_name, language):
        collection = Video.get_collection()
        if collection is None:
            return None
            
        video_id = str(uuid.uuid4())
        video_doc = {
            "videoId": video_id,
            "userId": user_id,
            "fileName": file_name,
            "inputS3Url": "",
            "outputS3Url": "",
            "language": language,
            "status": "UPLOADED",
            "uploadedAt": datetime.datetime.utcnow(),
            "completedAt": None
        }
        
        collection.insert_one(video_doc)
        Video.add_log(video_id, "UPLOADED", "SUCCESS", "Video metadata created in database")
        return video_id

    @staticmethod
    def update_video_status(video_id, status, output_s3_url=None):
        collection = Video.get_collection()
        if collection is None:
            return
            
        update_fields = {"status": status}
        if status == "COMPLETED":
            update_fields["completedAt"] = datetime.datetime.utcnow()
        if output_s3_url:
            update_fields["outputS3Url"] = output_s3_url
            
        collection.update_one({"videoId": video_id}, {"$set": update_fields})

    @staticmethod
    def get_videos_by_user(user_id):
        collection = Video.get_collection()
        if collection is None:
            return []
        
        # Sort by uploadedAt descending
        cursor = collection.find({"userId": user_id}).sort("uploadedAt", -1)
        return list(cursor)

    @staticmethod
    def get_video_by_id(video_id):
        collection = Video.get_collection()
        if collection is None:
            return None
            
        return collection.find_one({"videoId": video_id})
        
    @staticmethod
    def update_input_url(video_id, s3_url):
        collection = Video.get_collection()
        if collection is None:
            return
        collection.update_one({"videoId": video_id}, {"$set": {"inputS3Url": s3_url}})

    @staticmethod
    def add_log(video_id, stage, status, message):
        collection = Video.get_logs_collection()
        if collection is None:
            return
            
        log_doc = {
            "logId": str(uuid.uuid4()),
            "videoId": video_id,
            "processingStage": stage,
            "status": status,
            "message": message,
            "timestamp": datetime.datetime.utcnow()
        }
        collection.insert_one(log_doc)
        
    @staticmethod
    def get_video_logs(video_id):
        collection = Video.get_logs_collection()
        if collection is None:
            return []
        cursor = collection.find({"videoId": video_id}).sort("timestamp", 1)
        return list(cursor)
