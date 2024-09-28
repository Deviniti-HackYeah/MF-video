
from threading import Thread
from app import app

from flask import jsonify

from dotenv import load_dotenv
from pathlib import Path
import os
import json

from .data_manager import DataManager
from .transcript_video import TranscriptVideo

load_dotenv()

data_dir = os.environ.get('DATA_DIR')

project_path = Path.cwd()
app_path = os.path.join(project_path, "app")
cache_path = os.path.join(app_path, "cache")
prompt_path = os.path.join(app_path, "prompts.json")

def post_video_action(request):
    customer_id = request.form.get('customer_id') 
    note_language = request.form.get('note_language', '')
    video_file = request.files.get("video_file")
    if not video_file:
        return jsonify({"status": "ERROR", "message": "No video file provided"})
    
    filename = video_file.filename
    if not filename.endswith(".mp4"):
        return jsonify({"status": "ERROR", "message": "Wrong file format"})
    
    ok, code, session = DataManager(customer_id, note_language, filename, video_file).save()
    tv = TranscriptVideo()
    thread = Thread(target=tv.transcript_video, args=(customer_id, session, "transript_video"))
    thread.start()
    return jsonify({
                "status": ok,
                "message": "Video is now processing. You can check if result is ready using ready_suffix",
                "code": code,
                "customer_id": customer_id,
                "session": session,
                "ready_suffix": f"/api/result_ready/{customer_id}/{session}"
            })

def result_ready(customer_id, session):
    result_folder = os.path.join(data_dir, str(customer_id), str(session))
    for result_file in os.listdir(result_folder):
        print(f"result file {result_file}")
        if result_file.endswith(".docx"):
            return jsonify({
                "status": "Ok",
                "message": "Results ready. You can download them using download_suffix or get them by mail using mail_suffix",
                "download_suffix": f"/api/download/{customer_id}/{session}",
                "mail_suffix": f"/api/send_email/{customer_id}/{session}"
            })
    return jsonify({
                "status": "ERROR",
                "message": "Result is not ready yet!"
    })
