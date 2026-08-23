# Project Documentation: Automated Cloud Video Subtitle Burner

## 1. Abstract
The Automated Cloud Video Subtitle Burner is an intermediate-level cloud-based web application designed to automatically generate and permanently embed subtitles into uploaded video files. Leveraging modern cloud technologies like AWS Transcribe, AWS S3, and MongoDB, the system processes raw video files, extracts speech to text, converts the text into standard SRT subtitle format, and utilizes FFmpeg to burn the subtitles directly onto the video stream. This application simplifies the often tedious process of manual subtitling and demonstrates a practical integration of cloud micro-services in a monolithic Flask backend.

## 2. Introduction
Video content is a dominant medium on the internet, and subtitles are critical for accessibility, multi-lingual support, and silent viewing. Generating subtitles manually is time-consuming. This project introduces an automated solution where users simply upload a video, and the cloud handles speech-to-text generation and video rendering, offering the user a final subtitled video ready for download.

## 3. Problem Statement
Content creators frequently struggle with the manual process of creating subtitles. Existing solutions either require complex desktop software (like Premiere Pro) or charge high fees for simple transcription and subtitle burning. There is a need for an easy-to-use, web-based platform that automates this workflow efficiently.

## 4. Existing System
Currently, users often rely on separate tools to transcribe audio (e.g., uploading to YouTube for auto-captions, downloading the `.vtt` file, converting it to `.srt`, and using Handbrake or Premiere Pro to burn the text into the video). This process is fragmented and requires technical knowledge of multiple software applications.

## 5. Proposed System
The proposed system unifies this workflow into a single web application. A user uploads a video file, which is securely stored in AWS S3. The backend orchestrates an AWS Transcribe job to convert the audio track into a transcript. A custom Python service translates the Transcribe JSON output into an SRT file. Finally, an FFmpeg process runs to hard-encode the subtitles into the video, and the result is provided as a direct download to the user.

## 6. Objectives
- Provide a simple web interface for video uploads.
- Securely authenticate and manage users.
- Automatically generate highly accurate subtitles using AWS Transcribe.
- Render subtitles directly into the video stream via FFmpeg.
- Track and display the processing progress in real-time.

## 7. System Requirements
- **Hardware:** Standard PC/Mac for usage. For deployment, a 2vCPU, 4GB RAM instance is recommended due to FFmpeg rendering overhead.
- **Software:** Python 3.10+, FFmpeg, MongoDB Atlas, AWS Account (S3, Transcribe, IAM).

## 8. Technologies Used
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript
- **Backend:** Python 3, Flask, JWT
- **Database:** MongoDB (pymongo)
- **Cloud:** AWS S3 (Storage), AWS Transcribe (Speech-to-Text)
- **Video Processing:** FFmpeg
- **Containerization:** Docker

## 9. System Architecture
The user interacts with the Web Frontend, which makes REST API calls to the Flask backend. When a video is uploaded, the Flask app stores it locally and pushes a copy to AWS S3. It then triggers an AWS Transcribe job, polls for completion, downloads the result, builds the SRT file, runs FFmpeg locally (or within its Docker container), pushes the final output back to S3, and updates the MongoDB database throughout every stage.

## 10. Database Design
MongoDB is utilized with three main collections:
- `users`: Stores user credentials (hashed) and IDs.
- `videos`: Stores video metadata, current status, input/output S3 URLs, and language.
- `subtitles`: Stores generated subtitle metadata.
- `processing_logs`: Stores granular timeline events for each video processing job.

## 11. Data Flow Diagram
User -> Uploads Video -> Flask API -> Uploads to S3 -> Starts AWS Transcribe -> Polling -> Download JSON -> Parse to SRT -> FFmpeg burn -> Upload Output to S3 -> User Downloads Video.

## 12. Implementation
The project is modularized into `routes/` for API endpoints, `models/` for MongoDB operations, and `services/` for handling cloud integrations and video processing. Background threading is used to ensure the upload API returns immediately while the heavy processing continues asynchronously.

## 13. Cloud Deployment
The system can be deployed using Docker. A `Dockerfile` encapsulates the Python environment and installs the system-level dependency, FFmpeg. The container can be deployed to an AWS EC2 instance, with environment variables (`.env`) passed during the container launch.

## 14. Testing
Testing focuses on unit testing the SRT generation logic and integration testing the AWS S3 and Transcribe services. Manual end-to-end testing involves uploading a short test video and ensuring the downloaded output contains properly synced subtitles.

## 15. Results
The application successfully processes short to medium-length videos. The processing time is directly proportional to the length of the video (Transcribe time + FFmpeg rendering time). The dashboard accurately reflects the current state of the pipeline.

## 16. Advantages
- Fully automated workflow.
- Cloud-backed storage ensures high availability and durability.
- Scalable architecture (the background worker can be detached to a separate celery queue in future iterations).

## 17. Limitations
- FFmpeg rendering is currently synchronous and blocking within the worker thread, which could lead to high CPU usage on the host server.
- AWS Transcribe has associated costs per minute of audio.
- Large video files may exceed basic upload limits or timeout the S3 upload if not handled via multipart upload.

## 18. Future Enhancements
- Implement Celery + Redis for robust background task queuing instead of simple Python threading.
- Implement multipart S3 uploads directly from the browser to reduce backend server load.
- Add a subtitle editor UI allowing users to correct the transcript before burning.

## 19. Conclusion
The Automated Cloud Video Subtitle Burner is a highly functional intermediate-level cloud project. It successfully stitches together multiple cloud services and open-source video tools to solve a real-world problem, providing an excellent foundation in cloud computing concepts, REST API design, and asynchronous task processing.

## 20. References
- AWS Boto3 Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- FFmpeg Documentation: https://ffmpeg.org/documentation.html
- Flask Documentation: https://flask.palletsprojects.com/
- MongoDB Documentation: https://www.mongodb.com/docs/
