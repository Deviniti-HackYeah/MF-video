from flask import jsonify

from app import app


class TranscriptVideo:
    def __init__(self):
        pass

    def __str__(self):
        return "Transcript Video using Whisper"
    
    def transcript_video(self, customer_id, session, action):
        with app.app_context():
            print(f"Transcripting video for customer {customer_id} and session {session} using {action}")
        return {"status": "OK", "message": "Video is now processing. You can check if result is ready using ready_suffix"}, 200