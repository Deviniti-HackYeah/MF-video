from flask import jsonify

class TranscriptVideo:
    def __init__(self):
        pass

    def __str__(self):
        return "Transcript Video using Whisper"
    
    def transcript_video(self, customer_id, session, action):
        print(f"Transcripting video for customer {customer_id} and session {session} using {action}")
        return jsonify({"status": "OK", "message": "Video is now processing. You can check if result is ready using ready_suffix"})