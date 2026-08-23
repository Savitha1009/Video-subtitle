# Automated Cloud Video Subtitle Burner

An intermediate-level cloud-based web application that allows users to upload videos, automatically transcribes audio, generates SRT files, and uses FFmpeg to burn subtitles permanently into the video. The processed video is then stored in AWS S3 and made available for download.

## Features

- **Authentication**: JWT-based secure user registration and login.
- **Video Upload**: Allows uploading of MP4, AVI, MOV, and MKV files.
- **Automated Transcription**: Uses AWS Transcribe to convert speech to text.
- **Subtitle Generation**: Automatically converts transcription JSON to standard SRT format.
- **Subtitle Burning**: Uses FFmpeg to embed the generated SRT into the video permanently.
- **Cloud Storage**: Original and processed videos are stored securely in an AWS S3 bucket.
- **Dashboard Tracking**: Tracks the entire processing pipeline step-by-step (UPLOADED -> TRANSCRIBING -> SUBTITLE_GENERATED -> BURNING_SUBTITLE -> UPLOADING_OUTPUT -> COMPLETED).

## Tech Stack

- **Backend**: Python 3, Flask
- **Database**: MongoDB (via pymongo)
- **Cloud Infrastructure**: AWS S3, AWS Transcribe
- **Video Processing**: FFmpeg
- **Frontend**: Vanilla HTML/CSS/JS

## Setup & Installation

### Prerequisites
- Python 3.10+
- FFmpeg installed and in your system PATH
- MongoDB Cluster (e.g., MongoDB Atlas)
- AWS Account with S3 and Transcribe access

### Installation Steps

1. **Clone the repository** (if applicable).
2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables**:
   Update the `.env` file with your credentials:
   - `MONGO_URI`
   - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
   - `S3_BUCKET_NAME`
   - `JWT_SECRET_KEY`

4. **Run the Application**:
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000/`. You can navigate to it in your web browser.

### Docker Deployment

To run via Docker:
```bash
docker build -t subtitle-burner .
docker run -p 5000:5000 --env-file .env subtitle-burner
```

## Usage

1. Open the application, register a new account, and login.
2. From the Dashboard, click **Upload New Video**.
3. Select an MP4 video, choose the spoken language, and click **Upload & Process**.
4. The system will direct you to a result page where you can monitor the live status of the transcription and subtitle burning process.
5. Once completed, a **Download Final Video** button will appear.
