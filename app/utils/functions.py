import fcntl
import hashlib
import os
import json

def generate_hash(password):
    hash_salt = os.getenv("HASH_SALT", '123')
    return hashlib.sha256((password + hash_salt).encode()).hexdigest()

def check_hash(password, hash):
    return generate_hash(password) == hash

def write_to_file_with_lock(file_path, data, **kwargs):
    mode = kwargs.get('mode', 'w')
    encoding = kwargs.get('encoding', 'utf-8')
    ensure_ascii = kwargs.get('ensure_ascii', False)
    indent = kwargs.get('indent', 4)

    with open(file_path, mode=mode, encoding=encoding) as file:
        # Acquire an exclusive lock for writing
        fcntl.flock(file, fcntl.LOCK_EX)
        try:
            json.dump(data, file, indent=indent, ensure_ascii=ensure_ascii)
            return True
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return False
        finally:
            # Release the lock
            fcntl.flock(file, fcntl.LOCK_UN)

def read_from_file_with_lock(file_path, **kwargs):

    mode = kwargs.get('mode', 'r')
    encoding = kwargs.get('encoding', 'utf-8')
    with open(file_path, mode=mode, encoding=encoding) as file:
        # Acquire a shared lock for reading
        fcntl.flock(file, fcntl.LOCK_SH)
        try:
            data = json.load(file)
            if not data:
                return {}
            return data
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return {}
        finally:
            # Release the lock
            fcntl.flock(file, fcntl.LOCK_UN)

def manage_results(data_dir, user_id, session):
    result_folder = os.path.join(data_dir, str(user_id), str(session))
    jsons_in_folder = [f for f in os.listdir(result_folder) if f.endswith(".json")]
    mp4_file = [f for f in os.listdir(result_folder) if f.endswith(".mp4")][0]
    mp4_file_path = os.path.join(result_folder, mp4_file)
    full_result = {}
    full_result['transcription'] = []
    full_result['results']= {}
    full_result['video'] = []
    full_result['audio'] = []
    full_result['videoUrl'] = mp4_file_path
    for json_file in os.listdir(jsons_in_folder):
        if json_file == "clarity_check.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            data['videoExample'] = "--"
            full_result['transcription'].append(data)
        elif json_file == "readibility_measures.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            data['videoExample'] = "--"
            full_result['transcription'] = data
        elif json_file == "sentiment.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            data['videoExample'] = "--"
            full_result['transcription'] = data
        elif json_file == "text_structure.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            data['videoExample'] = "--"
            full_result['transcription'] = data
        elif json_file == "language_rate.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            data['videoExample'] = "--"
            full_result['transcription'] = data
        elif json_file == "overall_rating.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            data['videoExample'] = "--"
            full_result['transcription'] = data
        elif json_file == "pause_check.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            pauses = data.get('pauses', [])
            if len(pauses) == 0:
                fixed_data = {
                    "recommendations": "--",
                    "videoExample": "--",
                    "comment": "--",
                    "score": pauses.get('score', 0),
                    "area": pauses.get('area', '')
                }
                full_result['audio'] = fixed_data
            for pause in pauses:
                fixed_data = {
                    "recommendations": pause.get('recommendations', ''),
                    "videoExample": pause.get('pause_start', '--'),
                    "comment": pause.get('comment', ''),
                    "score": pauses.get('score', 0),
                    "area": pauses.get('area', '')
                }
                full_result['audio'] = fixed_data
        elif json_file == "topic_change.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            data['videoExample'] = "--"
            full_result['transcription'] = data
        elif json_file == "false_words.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            falses = data.get('falses', [])
            if len(falses) == 0:
                fixed_data = {
                    "recommendations": "--",
                    "videoExample": "--",
                    "comment": "--",
                    "score": falses.get('score', 0),
                    "area": falses.get('area', '')
                }
                full_result['transcription'] = fixed_data
            for false in falses:
                fixed_data = {
                    "recommendations": false.get('recommendations', ''),
                    "videoExample": false.get('false_start', '--'),
                    "comment": false.get('comment', ''),
                    "score": falses.get('score', 0),
                    "area": falses.get('area', '')
                }
                full_result['transcription'] = fixed_data
        elif json_file == "variety_of_statements.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            data['videoExample'] = "--"
            full_result['transcription'] = data
        elif json_file == "active_form_check.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            data['videoExample'] = "--"
            full_result['transcription'] = data
        elif json_file == "clarity_of_information_check.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            data['videoExample'] = "--"
            full_result['transcription'] = data
        elif json_file == "interjections_and_anecdotes_check.json":
            data = read_from_file_with_lock(os.path.join(result_folder, json_file))
            data['videoExample'] = "--"
            full_result['audio'] = data
        elif json_file == "visual_anomalies.json":
            try:
                data = read_from_file_with_lock(os.path.join(result_folder, json_file))
                if not "videoExample" in data:
                    data['videoExample'] = "--"
                full_result['video'] = data
            except:
                pass
        elif json_file == "presenter_check.json":
            try:
                data = read_from_file_with_lock(os.path.join(result_folder, json_file))
                if not "videoExample" in data:
                    data['videoExample'] = "--"
                full_result['video'] = data
            except:
                pass
        elif json_file == "compare_transciption.json":
            try:
                data = read_from_file_with_lock(os.path.join(result_folder, json_file))
                if not "videoExample" in data:
                    data['videoExample'] = "--"
                full_result['video'] = data
            except:
                pass

    
    transcription_results = full_result.get('transcription', [])
    sum_transcription_score = 0
    for element in transcription_results:
        element_score = element.get('score', 0)
        sum_transcription_score += element_score

    video_results = full_result.get('video', [])
    sum_video_score = 0
    for element in video_results:
        element_score = element.get('score', 0)
        sum_video_score += element_score
    
    audio_results = full_result.get('audio', [])
    sum_audio_score = 0
    for element in audio_results:
        element_score = element.get('score', 0)
        sum_audio_score += element_score

    transcription_score = sum_transcription_score / len(transcription_results) if len(transcription_results) > 0 else 0
    video_score = sum_video_score / len(video_results) if len(video_results) > 0 else 0
    audio_score = sum_audio_score / len(audio_results) if len(audio_results) > 0 else 0

    summary_score = (sum_transcription_score + sum_video_score + sum_audio_score) / (len(transcription_results) + len(video_results) + len(audio_results))

    full_result['results'] = {
        "transcription": transcription_score,
        "yourScore": summary_score,
        "video": video_score,
        "audio": audio_score
    }
    
    return full_result