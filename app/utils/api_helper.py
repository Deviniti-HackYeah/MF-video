
from threading import Thread
from app import app


from dotenv import load_dotenv
from pathlib import Path
import os
import json

import smtplib
from email.mime.text import MIMEText

from app.utils.mail_service import send_email
from app.utils.data_manager import DataManager
from app.utils.transcript_video import TranscriptVideo
from app.utils.postgres_manager import PostgresManager
from app.utils.functions import generate_hash, read_from_file_with_lock

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
    
def send(download_url, email):
    try:
        with app.app_context():
            send_email(template="mail_template.html",
                    title="Raport z analizy wideo",
                    message=f"Twoje podsumowanie materiału wideo jest już gotowe. Możesz je obejrzeć klikając w link poniżej {download_url}",
                    to_email=email)
    except:
        return {
            "status": "ERROR",
            "message": f"Error with sending mail to {email}"
            }
    
def send_mail_ok(params):
        
    email = params.get('email')
    user_id = params.get('user_id')
    session = params.get('session')

    if email:
        download_url = f"{os.environ.get('VIEW_URL')}/{user_id}/{session}"
        send(download_url, email)
        return {
            "status": "OK",
            "message": f"Mail sent to {email}"
        }
    else:
        return {
            "status": "ERROR",
            "message": "No mail provided"
        }
        
def send_gmail(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())
    print("Mail sent")

    

