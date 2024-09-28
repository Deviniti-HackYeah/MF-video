from flask import jsonify
import whisper

class TranscriptVideo:
    def __init__(self):
        pass

    def __str__(self):
        return "Transcript Video using Whisper"
    
    def transcript_video(self, customer_id, session, action, file_path):
        print(f"Transcripting video for customer {customer_id} and session {session} using {action}")
        
        # Load Whisper Large model
        model = whisper.load_model("large")
        result = model.transcribe(file_path)
        print(f"Transcpition result: {result["text"]}")
        
        return jsonify({"status": "OK", "message": "Video is now processing. You can check if result is ready using ready_suffix"})
    
    
tv = TranscriptVideo()
tv.transcript_video("123", "321", "TEST", "/Users/pkiszczak/Downloads/wetransfer_hackyeah-2024-breakwordtraps_2024-09-28_0449/HY_2024_film_08.mp4")