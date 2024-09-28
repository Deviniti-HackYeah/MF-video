import os
import hashlib
import yt_dlp
import ffmpeg
import whisper_timestamped as whisper
import json
import cv2
from app.utils.llm_analyzer import LLMAnalyzer
import base64
import assemblyai as aai
import re

class VideoManager:

    def __init__(self, video_path, audio_path, data_path, cache_dir):
        self.video_path = video_path
        self.audio_path = audio_path
        self.data_path = data_path
        self.cache_dir = cache_dir
        self.llm = LLMAnalyzer(cache_dir)

    def __get_frame_transcript(self, transcript, seconds, interval=5):
        segments = transcript.get('segments', [])
        text = ""
        t1 = seconds - interval
        t2 = seconds + interval
        for item in segments:
            if item['start'] >= t1 and item['end'] <= t2:
                text += item['text'] + " "
        return text.strip()

    def __parse_vtt(self, file_path):

        subtitles = []

        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

            blocks = content.strip().split('\n\n')

            for block in blocks:
                lines = block.strip().split('\n')

                if len(lines) >= 2:
                    time_range = lines[0]
                    text = ' '.join(lines[1:]).replace('\n', ' ')

                    match = re.match(r'(\d{1,2}:\d{2}:\d{2}\.\d{3}) --> (\d{1,2}:\d{2}:\d{2}\.\d{3})|(\d{1,2}:\d{2}\.\d{3}) --> (\d{1,2}:\d{2}\.\d{3})', time_range)
                    if match:
                        if match.group(1) and match.group(2):  # Format HH:MM:SS.mmm
                            start_time = match.group(1)
                            end_time = match.group(2)
                        else:  # Format MM:SS.mmm
                            start_time = match.group(3)
                            end_time = match.group(4)
                            start_time = '00:' + start_time  # Dodaj godziny
                            end_time = '00:' + end_time  # Dodaj godziny
                        
                        start_seconds = self.__convert_to_seconds(start_time)
                        end_seconds = self.__convert_to_seconds(end_time)
                        subtitles.append((start_seconds, end_seconds, text))

        return subtitles

    def __convert_to_seconds(self, time_str):
        parts = list(map(float, re.split('[:.]', time_str)))
        
        if len(parts) == 3:  # HH:MM:SS.mmm
            hours, minutes, seconds = parts
        elif len(parts) == 2:  # MM:SS.mmm
            hours = 0
            minutes, seconds = parts
        elif len(parts) == 4:  # HH:MM:SS:mmm
            hours, minutes, seconds, milliseconds = parts
            seconds += milliseconds / 1000
        else:
            raise ValueError("Nieprawidłowy format czasu.")
        
        return hours * 3600 + minutes * 60 + seconds

    def __get_subtitles_in_interval(self, subtitles, start_interval, end_interval):
        result = []
        for start, end, text in subtitles:
            if start < end_interval and end > start_interval:
                result.append(text)
        return "\n".join(result)

    def analize_frames(self, video_file_name, url, interval=5, vtt = None):

        ok = False
        error = ""
        frames_folder_path = os.path.join(self.data_path, video_file_name.replace(".mp4", ""))

        transcript = {}
        report = []

        if not vtt:
            transcript_file_name = os.path.join(self.data_path, video_file_name.replace(".mp4", ".json"))
            if os.path.exists(transcript_file_name):
                transcript = json.load(open(transcript_file_name))      
        else:
            vtt_path = os.path.join(self.data_path, vtt)
            vtt_data = self.__parse_vtt(vtt_path)

        if not os.path.exists(frames_folder_path):
            return False, frames_folder_path, "Frames not found"

        try:
            frames = [f for f in os.listdir(frames_folder_path) if f.endswith('.png')]
            frames.sort()

            all_frames = len(frames)
            all = ""
            pf = 0

            for frame in frames:
                pf += 1
                print(f"Analizing frame: {frame} {pf} of {all_frames}")
                frame_path = os.path.join(frames_folder_path, frame)
                seconds = round(float(frame.split("_")[1].replace(".png", "")))
                if not vtt:
                    text = self.__get_frame_transcript(transcript, seconds, interval)
                    all = transcript.get('text', "")
                else:
                    text = self.__get_subtitles_in_interval(vtt_data, seconds - interval, seconds + interval)

                    for t in vtt_data:
                        all += t[2] + "\n"

                b64 = "data:image/png;base64," + base64.b64encode(open(frame_path, "rb").read()).decode()
                prompt = f"Podany obraz to stopklatka z programu telewizyjnego/serialu/filmu w {seconds} sek. Dodatkowo dodano fragment transkrypcji w okolicach tej stopklatki. Przeanalizuj dokładnie obraz i połącz go z transkrypcją. Uważaj transkrypcja może mieć błędy przetwarzania, spróbuj je poprawić np. pomyłki literówki na podstawie pełnej transkrypcji. Opisz dokładnie co widzisz na obrazie: jakie obiekty (przedmioty, zwłaszcza dekoracje, wnętrza, wystrój), ludzie, emocje, miejsce, akcje itp. Dodatkowo stwórz tytuł fragmentu oraz ustal słowa kluczowe. Przeanalizuj scenę oraz transkrypcję i stwierdź czy scena zawiera elementy dekoracji wnętrz, inspiracyjne produkty, przydatne przyrządy i urządzenia domowe. Wynik przedstaw jako obiekt JSON z kluczami: description_pl, title_pl, keywords_pl (po przecinku maksymalnie 5 słów kluczowych), interiors (0 lub 1).\n\n"
                prompt += f"TRANSKRYPCJA W OKOLICACH STOP KLATKI: \n"
                prompt += text + "\n\n"
                
                data_txt_json = self.llm.analyze_image(system_message=prompt, base64_image=b64, model = "gpt-4o")
                data = json.loads(data_txt_json, strict=False)


                report.append({
                    "frame": frame,
                    "seconds": seconds,
                    "text": text,
                    "meta": data
                })

            report_data = {}
            report_data['url'] = url
            report_data['transcription'] = all
            report = sorted(report, key=lambda x: x['seconds'])
            report_data['frames'] = report

            report_mini = []
            for item in report:
                report_mini.append(item)   

            report_mini = report_mini[:30] 
            report_txt_mini = json.dumps(report_mini, indent=4, ensure_ascii=False)

            prompt = "Podany obiekt JSON to bardzo dokładnie opisane początkowe sceny programu telewizyjnego, serialu lub filmu. Opis zawiera dokładne informacje o obrazie, ludziach, emocjach, miejscu, akcjach itp. Dodatkowo zawiera pełną transkrypcje. Przeanalizuj dokłandie, a następnie stwórz streszczenia programu, serialu lub filmu. W streszczeniu nie skupiaj się na elementach wizualnych, a bardziej o czym jest program, jakiego typu, poruszane tematy, kategorie itp. Następnie tytuł i słowa kluczowe. Wynik przedstaw jako obiekt JSON z kluczami: title_pl, summary_pl, keywords_pl (po przecinku maksymalnie 20 słów kluczowych)."
            meta_data_all = self.llm.run_analisys(prompt = prompt, text = report_txt_mini, default_data= {}, temperature = 0.0, mt = 1200, model = "gpt-4o")

            if meta_data_all:
                report_data['title'] = meta_data_all["title_pl"]
                report_data['summary'] = meta_data_all["summary_pl"]
                report_data['keywords'] = meta_data_all["keywords_pl"]

            with open(os.path.join(frames_folder_path, "report.json"), 'w') as f:
                json.dump(report_data, f, indent=4, ensure_ascii=False)

        except Exception as e:
            error = str(e)
            ok = False
            print(f"Error analizing frames: {error}")

        return ok, frames_folder_path, error

    def transcribe_vtt_assembly(self, audio_file_name):

        ok = True
        error = ""
        aai.settings.api_key = os.getenv("ASSEMBLY_AI_API_KEY") 
        vtt_file_name = audio_file_name.replace(".mp3", ".vtt")
        vtt_file_path = os.path.join(self.data_path, vtt_file_name)

        if os.path.exists(vtt_file_path):
            print(f"Transcript already exists: {vtt_file_name}")
            return True, vtt_file_name, ""

        audio_file_path = os.path.join(self.audio_path, audio_file_name)
        config = aai.TranscriptionConfig(language_code="pl")
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(audio_file_path, config=config)

        if transcript.status == aai.TranscriptStatus.error:
            print(f"Transcription failed: {transcript.error}")
            error = transcript.error
            ok = False
        else:
            vtt = transcript.export_subtitles_vtt()
            with open(vtt_file_path, 'w') as f:
                f.write(vtt)

        return ok, vtt_file_name, error

    def transcribe(self, audio_file_name, lang = "pl", model = "large", device = "cpu"):

        ok = False
        error = ""
        transcript_file_name = audio_file_name.replace(".mp3", ".json")
        transcript_file_path = os.path.join(self.data_path, transcript_file_name)
        audio_file_path = os.path.join(self.audio_path, audio_file_name)

        if os.path.exists(transcript_file_path):
            print(f"Transcript already exists: {transcript_file_name}")
            return True, transcript_file_name, ""

        try:

            audio = whisper.load_audio(audio_file_path)
            model = whisper.load_model(model, device=device)
            result = whisper.transcribe(model, audio, language=lang)

            with open(transcript_file_path, 'w') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)

        except Exception as e:
            error = str(e)
            ok = False
            print(f"Error transcribing: {error}")

        return ok, transcript_file_name, error

    def extract_audio(self, video_file_name):

        ok = False
        error = ""

        try:
            audio_file_name = video_file_name.replace(".mp4", ".mp3")
            audio_file_path = os.path.join(self.audio_path, audio_file_name)
            video_file_path = os.path.join(self.video_path, video_file_name)

            if os.path.exists(audio_file_path):
                print(f"Audio already exists: {audio_file_name}")
                return True, audio_file_name, ""

            (
                ffmpeg
                .input(video_file_path)
                .output(audio_file_path, **{'vn': None, 'acodec': 'libmp3lame', 'ac': 2, 'ab': '160k', 'ar': '48000'})
                .run()
            )
            ok = True
        except Exception as e:
            error = str(e)
            ok = False
            print(f"Error extracting audio: {error}")

        return ok, audio_file_name, error

    def download_video(self, url, cookies_path):
        ok = False
        error = ""
        file_name = ""

        file_name = hashlib.md5(url.encode()).hexdigest()
        file_path = os.path.join(self.video_path, file_name)

        if os.path.exists(file_path + ".mp4"):
            print(f"Video already exists: {file_name}")
            return True, file_name + ".mp4", ""

        try:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': file_path,
                'noplaylist': True,
                'cookies': cookies_path,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'
                }]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                ok = True
        except Exception as e:
            error = str(e)
            ok = False
            print(f"Error downloading video: {error}")

        return ok, file_name + ".mp4", error

    def __resize_frame_if_needed(self, frame, output_filename):

        height, width = frame.shape[:2]

        if width > 1000:
            new_width = int(width * 0.5)
            new_height = int(height * 0.5)
            resized_frame = cv2.resize(
                frame, (new_width, new_height), interpolation=cv2.INTER_CUBIC
            )
            cv2.imwrite(output_filename, resized_frame)

        else:
            cv2.imwrite(output_filename, frame)

    def extract_frames(self, video_file_name, interval=5):

        ok = False
        error = ""
        video_file_path = os.path.join(self.video_path, video_file_name)

        frames_folder_path = os.path.join(self.data_path, video_file_name.replace(".mp4", ""))
        if not os.path.exists(frames_folder_path):
            os.makedirs(frames_folder_path)

        try:
            cap = cv2.VideoCapture(video_file_path)
            if not cap.isOpened():
                raise Exception(f"Error opening video file {video_file_path}")

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps

            current_frame = 0

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if current_frame % int(fps * interval) == 0:
                    frame_time = current_frame // fps
                    output_filename = os.path.join(frames_folder_path, f"frame_{frame_time}.png")
                    self.__resize_frame_if_needed(frame, output_filename)
                    print(f"Extracting frame: {frame_time}")

                current_frame += 1

            cap.release()
            ok = True
            print(f"Extracted frames: {video_file_name}")

        except Exception as e:
            error = str(e)
            ok = False
            print(f"Error extracting frames: {error}")

        return ok, frames_folder_path, error