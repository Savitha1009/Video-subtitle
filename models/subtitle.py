from config.db import get_db
import datetime
import uuid

class Subtitle:
    @staticmethod
    def get_collection():
        db = get_db()
        return db['subtitles'] if db is not None else None

    @staticmethod
    def create_subtitle(video_id, language, style="default"):
        collection = Subtitle.get_collection()
        if collection is None:
            return None
            
        subtitle_id = str(uuid.uuid4())
        subtitle_doc = {
            "subtitleId": subtitle_id,
            "videoId": video_id,
            "language": language,
            "subtitleFormat": "srt",
            "subtitleFileUrl": "",
            "subtitleStyle": style,
            "generatedAt": datetime.datetime.utcnow()
        }
        
        collection.insert_one(subtitle_doc)
        return subtitle_id

    @staticmethod
    def update_subtitle_url(subtitle_id, file_url):
        collection = Subtitle.get_collection()
        if collection is None:
            return
            
        collection.update_one(
            {"subtitleId": subtitle_id}, 
            {"$set": {"subtitleFileUrl": file_url}}
        )

    @staticmethod
    def get_subtitle_by_video_id(video_id):
        collection = Subtitle.get_collection()
        if collection is None:
            return None
            
        return collection.find_one({"videoId": video_id})
