from flask import jsonify
import whisper_timestamped as whisper
from pydub import AudioSegment
# from app import whisper_model

class TranscriptVideo:
    def __init__(self):
        pass

    def __str__(self):
        return "Transcript Video using Whisper"
    
    def convert_to_mp3(self, file_path: str, output_name: str) -> bool:
        print(f"Converting {file_path} to .mp3... ")
        try:
            format = file_path.split('.')[-1]
            audio = AudioSegment.from_file(file_path, format=format)
            audio.export(output_name, format="mp3")
            print("Conversion successful")
            return True
        except Exception as e:
            print(f" * Error: {e}")
            print("Conversion failed")
            return False
    
    def transcript_video(self, customer_id: str, session: str, action: str, file_path: str) -> dict:
        print(f"Transcripting video for customer {customer_id} and session {session} using {action}")
        
        # Load Whisper Large model
        whisper_model = whisper.load_model("large")
        result = whisper_model.transcribe(file_path, fp16=False)
        print(f"Transcpition result: {result["text"]}")
        
        output = {
            "result": result
        }
        
        return output        
        # return jsonify({"status": "OK", "message": "Video is now processing. You can check if result is ready using ready_suffix"})
    
    
tv = TranscriptVideo()
fp = "/Users/pkiszczak/Downloads/wetransfer_hackyeah-2024-breakwordtraps_2024-09-28_0449/HY_2024_film_08.mp4"
tv.convert_to_mp3(file_path=fp,
                    output_name=f"{fp.split("/")[-1].split(".")[0]}.mp3")
tv.transcript_video("123", "321", "TEST", "/Users/pkiszczak/projects/deviniti/MF-video/app/utils/HY_2024_film_08.mp3")