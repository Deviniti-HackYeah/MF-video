
from threading import Thread
from app import app


from dotenv import load_dotenv
from pathlib import Path
import os
import json

from app.utils.mail_service import send_email
from app.utils.data_manager import DataManager
from app.utils.transcript_video import TranscriptVideo
from app.utils.postgres_manager import PostgresManager
from app.utils.functions import generate_hash

load_dotenv(override=True)

data_dir = os.environ.get('DATA_DIR')

project_path = Path.cwd()
app_path = os.path.join(project_path, "app")
cache_path = os.path.join(app_path, "cache")
prompt_path = os.path.join(app_path, "prompts.json")

def post_video_action(request):
    user_id = request.form.get('user_id') 
    note_language = request.form.get('note_language', 'pl')
    video_file = request.files.get("video_file")
    if not video_file:
        return {"status": "ERROR", "message": "No video file provided"}
    
    filename = video_file.filename
    if not filename.endswith(".mp4"):
        return {"status": "ERROR", "message": "Wrong file format"}
    
    ok, code, session = DataManager(user_id, note_language, filename, video_file).save()
    file_size = os.path.getsize(os.path.join(data_dir, str(user_id), str(session), filename))
    _, _ = PostgresManager().create_file(name=filename, ftype="video", size=file_size, session=session, user_id=user_id, hash=generate_hash(filename)) #filename, "video", file_size, session, user_id, '')
    tv = TranscriptVideo()
    thread = Thread(target=tv.save_transcription, args=(data_dir, user_id, session, filename))
    thread.start()
    return {
                "status": ok,
                "message": "Video is now processing. You can check if result is ready using ready_suffix",
                "code": code,
                "user_id": user_id,
                "session": session,
                "ready_suffix": f"/api/result_ready/{user_id}/{session}"
            }

def result_ready(user_id, session):
    result_folder = os.path.join(data_dir, str(user_id), str(session))
    for result_file in os.listdir(result_folder):
        print(f"result file {result_file}")
        if result_file.endswith(".pdf"):
            return {
                "status": "Ok",
                "message": "Results ready. You can download them using download_suffix or get them by mail using mail_suffix",
                "download_suffix": f"/api/download/{user_id}/{session}",
                "mail_suffix": f"/api/send_email/{user_id}/{session}"
            }
    return {
                "status": "ERROR",
                "message": "Result is not ready yet!"
    }

def get_file_path(folder):
    for file_name in os.listdir(folder):
        if file_name.endswith(".pdf"):
            return file_name
        return None
    
def send(request_name, email, docx_file_path):
    try:
        with app.app_context():
            send_email(template="mail_template.html",
                    title="Notatka ze spotkania już jest gotowa",
                    message=f"W załączniku znajduje się notatka ze spotkania: {request_name}",
                    to_email=email,
                    docx_file_path=docx_file_path)
    except:
        return {
            "status": "ERROR",
            "message": f"Error with sending mail to {email}"
            }
    
def send_mail_ok(request, params):
    
    req = request.get_json()
    
    mail = req.get('mail', '')
    
    user_id = params.get('user_id')
    session = params.get('session')
    data_dir = os.environ.get('DATA_DIR')
    request_file = os.path.join(data_dir, str(user_id), str(session), "data.json")
    
    with open(request_file, 'r', encoding='utf-8') as f:
        request_json = json.load(f)
        
    request_name = request_json.get("name")
    docx_file_path = get_file_path(os.path.join(data_dir, str(user_id), str(session)))
    
    if not docx_file_path:
        return {
            "status": "ERROR",
            "message": f"Can not find result file for specific customer: {user_id} and session {session}!"
        }
    
    if mail:
        send(request_name, mail, docx_file_path)
        return {
            "status": "OK",
            "message": f"Mail sent to {mail}"
        }
    else:
        return {
            "status": "ERROR",
            "message": "No mail provided"
        }
        