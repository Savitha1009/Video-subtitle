import subprocess
import os

class FFmpegService:
    @staticmethod
    def burn_subtitles(input_video, subtitle_file, output_video):
        """Burns subtitles into the video using FFmpeg"""
        try:
            # On Windows, FFmpeg's subtitles filter expects the path to be properly escaped
            # E.g., C:\path\to\sub.srt -> C\:/path/to/sub.srt or just forward slashes
            safe_sub_path = subtitle_file.replace('\\', '/')
            if ':' in safe_sub_path:
                safe_sub_path = safe_sub_path.replace(':', '\\:')
                
            # ffmpeg command: ffmpeg -i input.mp4 -vf subtitles=sub.srt output.mp4
            command = [
                'ffmpeg',
                '-y',  # Overwrite output
                '-i', input_video,
                '-vf', f"subtitles='{safe_sub_path}'",
                output_video
            ]
            
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print(f"FFmpeg error: {result.stderr}")
                return False
            return True
        except Exception as e:
            print(f"Error executing FFmpeg: {e}")
            return False
