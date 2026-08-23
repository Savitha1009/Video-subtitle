import json
import datetime

class SubtitleService:
    @staticmethod
    def _format_timestamp(seconds):
        """Format seconds into SRT timestamp format: HH:MM:SS,mmm"""
        time_delta = datetime.timedelta(seconds=float(seconds))
        hours, remainder = divmod(time_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = time_delta.microseconds // 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    @staticmethod
    def json_to_srt(json_filepath, srt_filepath):
        """Convert AWS Transcribe JSON output to SRT format"""
        try:
            with open(json_filepath, 'r') as f:
                data = json.load(f)
            
            items = data['results']['items']
            srt_content = ""
            subtitle_index = 1
            
            current_sentence = ""
            start_time = None
            end_time = None
            
            for item in items:
                if item['type'] == 'pronunciation':
                    if start_time is None:
                        start_time = item['start_time']
                    end_time = item['end_time']
                    current_sentence += item['alternatives'][0]['content'] + " "
                elif item['type'] == 'punctuation':
                    # Remove the trailing space before adding punctuation
                    current_sentence = current_sentence[:-1] + item['alternatives'][0]['content'] + " "
                    
                    # If we reach sentence end punctuation or after some length, we can write a subtitle line
                    if item['alternatives'][0]['content'] in ['.', '?', '!']:
                        formatted_start = SubtitleService._format_timestamp(start_time)
                        formatted_end = SubtitleService._format_timestamp(end_time)
                        
                        srt_content += f"{subtitle_index}\n"
                        srt_content += f"{formatted_start} --> {formatted_end}\n"
                        srt_content += f"{current_sentence.strip()}\n\n"
                        
                        subtitle_index += 1
                        current_sentence = ""
                        start_time = None
                        
            # If any remaining text
            if current_sentence.strip() and start_time is not None:
                formatted_start = SubtitleService._format_timestamp(start_time)
                formatted_end = SubtitleService._format_timestamp(end_time)
                
                srt_content += f"{subtitle_index}\n"
                srt_content += f"{formatted_start} --> {formatted_end}\n"
                srt_content += f"{current_sentence.strip()}\n\n"
                
            with open(srt_filepath, 'w') as f:
                f.write(srt_content)
                
            return True
        except Exception as e:
            print(f"Error converting JSON to SRT: {e}")
            return False
