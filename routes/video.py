from flask import Blueprint, request, jsonify
from utils.auth_decorator import token_required
from models.video import Video
from models.subtitle import Subtitle
from services.s3_service import S3Service
from services.transcribe_service import TranscribeService
from services.subtitle_service import SubtitleService
from services.ffmpeg_service import FFmpegService
import os
import threading
from werkzeug.utils import secure_filename

video_bp = Blueprint('video', __name__)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_video_background(video_id, local_video_path, filename, language):
    """Background task to handle the entire video processing pipeline"""
    try:
        # 1. Upload original video to S3
        Video.add_log(video_id, "UPLOADED", "SUCCESS", "Starting S3 upload")
        s3_url = S3Service.upload_file(local_video_path, f"uploads/{video_id}_{filename}")
        if not s3_url:
            raise Exception("Failed to upload video to S3")
        
        Video.update_input_url(video_id, s3_url)
        
        # 2. Transcribe
        Video.update_video_status(video_id, "TRANSCRIBING")
        Video.add_log(video_id, "TRANSCRIBING", "SUCCESS", "Started AWS Transcribe job")
        
        job_name = f"job_{video_id}"
        success = TranscribeService.start_transcription(job_name, s3_url, language)
        if not success:
            raise Exception("Failed to start transcription job")
            
        success = TranscribeService.wait_for_transcription(job_name)
        if not success:
            raise Exception("Transcription job failed")
            
        # 3. Download transcription JSON and convert to SRT
        Video.update_video_status(video_id, "SUBTITLE_GENERATED")
        Video.add_log(video_id, "SUBTITLE_GENERATED", "SUCCESS", "Transcription completed. Generating SRT")
        
        json_key = f"transcripts/{job_name}.json"
        local_json_path = os.path.join("processed", f"{video_id}.json")
        S3Service.download_file(json_key, local_json_path)
        
        local_srt_path = os.path.join("processed", f"{video_id}.srt")
        success = SubtitleService.json_to_srt(local_json_path, local_srt_path)
        if not success:
            raise Exception("Failed to convert JSON to SRT")
            
        # Create Subtitle record
        Subtitle.create_subtitle(video_id, language)
        
        # 4. Burn Subtitle
        Video.update_video_status(video_id, "BURNING_SUBTITLE")
        Video.add_log(video_id, "BURNING_SUBTITLE", "SUCCESS", "Burning subtitles using FFmpeg")
        
        output_video_path = os.path.join("processed", f"subtitled_{video_id}.mp4")
        success = FFmpegService.burn_subtitles(local_video_path, local_srt_path, output_video_path)
        if not success:
            raise Exception("FFmpeg failed to burn subtitles")
            
        # 5. Upload Output Video
        Video.update_video_status(video_id, "UPLOADING_OUTPUT")
        Video.add_log(video_id, "UPLOADING_OUTPUT", "SUCCESS", "Uploading processed video to S3")
        
        output_s3_url = S3Service.upload_file(output_video_path, f"processed/subtitled_{video_id}.mp4")
        if not output_s3_url:
            raise Exception("Failed to upload processed video to S3")
            
        # 6. Complete
        Video.update_video_status(video_id, "COMPLETED", output_s3_url)
        Video.add_log(video_id, "COMPLETED", "SUCCESS", "Video processing finished successfully")
        
    except Exception as e:
        Video.update_video_status(video_id, "ERROR")
        Video.add_log(video_id, "ERROR", "FAILED", str(e))
        print(f"Error processing video {video_id}: {e}")
    finally:
        # Cleanup local files (optional, leaving them for debugging is fine initially)
        pass

@video_bp.route('/upload', methods=['POST'])
@token_required
def upload_video(current_user):
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
        
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": "File format not supported"}), 400
        
    language = request.form.get('language', 'en-US')
    
    filename = secure_filename(file.filename)
    # Save temporarily to uploads folder
    local_path = os.path.join("uploads", filename)
    file.save(local_path)
    
    video_id = Video.create_video(current_user['userId'], filename, language)
    if not video_id:
        return jsonify({"error": "Failed to create video record"}), 500
        
    # Start background processing
    thread = threading.Thread(target=process_video_background, args=(video_id, local_path, filename, language))
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Video uploaded and processing started", "videoId": video_id}), 202

@video_bp.route('/videos', methods=['GET'])
@token_required
def get_videos(current_user):
    videos = Video.get_videos_by_user(current_user['userId'])
    # Convert ObjectId to string for JSON serialization
    for v in videos:
        v['_id'] = str(v['_id'])
    return jsonify({"videos": videos}), 200

@video_bp.route('/video/<video_id>', methods=['GET'])
@token_required
def get_video(current_user, video_id):
    video = Video.get_video_by_id(video_id)
    if not video:
        return jsonify({"error": "Video not found"}), 404
    
    if video['userId'] != current_user['userId']:
        return jsonify({"error": "Unauthorized"}), 403
        
    video['_id'] = str(video['_id'])
    return jsonify(video), 200

@video_bp.route('/status/<video_id>', methods=['GET'])
@token_required
def get_status(current_user, video_id):
    video = Video.get_video_by_id(video_id)
    if not video:
        return jsonify({"error": "Video not found"}), 404
        
    if video['userId'] != current_user['userId']:
        return jsonify({"error": "Unauthorized"}), 403
        
    logs = Video.get_video_logs(video_id)
    for log in logs:
        log['_id'] = str(log['_id'])
        
    return jsonify({
        "status": video['status'],
        "logs": logs
    }), 200

@video_bp.route('/download/<video_id>', methods=['GET'])
@token_required
def download_video(current_user, video_id):
    video = Video.get_video_by_id(video_id)
    if not video or video['status'] != 'COMPLETED':
        return jsonify({"error": "Video not found or not completed"}), 404
        
    if video['userId'] != current_user['userId']:
        return jsonify({"error": "Unauthorized"}), 403
        
    # Generate presigned url for outputS3Url
    object_name = f"processed/subtitled_{video_id}.mp4"
    presigned_url = S3Service.generate_presigned_url(object_name)
    
    if not presigned_url:
        return jsonify({"error": "Could not generate download link"}), 500
        
    return jsonify({"downloadUrl": presigned_url}), 200

@video_bp.route('/video/<video_id>', methods=['DELETE'])
@token_required
def delete_video(current_user, video_id):
    # Basic implementation: just mark as deleted or delete DB records.
    # Should ideally clean up S3 as well.
    return jsonify({"message": "Not implemented completely, but endpoint is here"}), 200
