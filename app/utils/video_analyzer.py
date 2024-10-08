import os
import hashlib
import cv2
import base64
from dotenv import load_dotenv
import json
from ast import literal_eval

from openai import OpenAI
from llm_analyzer import LLMAnalyzer
from functions import write_to_file_with_lock

load_dotenv()

class VideoAnalyzer:
    def __init__(self, cache_dir, user_id, session, data_dir):
        self.cache_dir = cache_dir
        self.user_id = user_id
        self.session = session
        self.data_dir = data_dir

    def __str__():
        return "Analyzing images and videos"
    

    def extract_frames_from_video(self, 
                                  file_name:str, 
                                output_folder: str,
                                speech_start: float,
                                interval: float = 1) -> int:
        """
        Extracts frames from a video and saves them as images.

        Parameters:
        - video_path: Path to the video file.
        - output_folder: Folder where the images will be saved.
        - speech_start: Time in seconds to start frame extraction.
        - interval: Interval at which to capture frames (in seconds). Default is 0.5 seconds (2 FPS).
        """
        # Check if the file exists
        video_path = os.path.join(self.data_dir, user_id, session, file_name)
        if not os.path.isfile(video_path):
            print(f"Error: Video file '{video_path}' does not exist.")
            return

        # Video filename
        video_filename = os.path.splitext(os.path.basename(video_path))[0]
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Open the video file
        cap = cv2.VideoCapture(video_path)

        # Check if the video capture was successfully opened
        if not cap.isOpened():
            print(f"Error: Could not read video stream from file '{video_path}'.")
            return

        # Get the frames per second (fps) of the video
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"Video loaded. FPS: {fps}")

        # Calculate the frame intervals and start frame
        frame_interval = int(fps * interval)
        start_frame = int(speech_start * fps)
        print(f"Extracting frames starting from {speech_start} seconds (Frame: {start_frame}) at {interval} second intervals.")

        # Set the initial frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        # Frame extraction logic
        current_frame = start_frame

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            # Save the frame at the specified interval
            if (current_frame - start_frame) % frame_interval == 0:
                frame_filename = os.path.join(output_folder, f"{video_filename}_frame{current_frame}.jpg")
                cv2.imwrite(frame_filename, frame)
                print(f"Saved: {frame_filename}")

            current_frame += 1

        # Release the video capture object
        cap.release()
        print(f"Extraction complete. Frames saved to '{output_folder}'.")
        
        return fps
        
        
    def img_to_base64(self, img_path: str) -> str:
        with open(img_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
        
        
    def analyze_image(self, prompt: str, base64_image: str) -> str:
        if os.getenv('OPENAI_API_KEY'):
            print(" * Using OpenAI")
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""),)
            print(f" * Client: {client}")

        model = os.getenv('OPENAI_MODEL_NAME')
        print(f" * Model: {model}")

        max_tokens = 3000
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                "role": "system",
                "content": [
                    {
                    "type": "text",
                    "text": prompt
                    }
                ]
                },
                {
                "role": "user",
                "content": [
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64, {base64_image}", # base64 with prefix for example data:image/png;base64,[BASE64]
                    }
                    }
                ]
                }
            ],
            response_format= {"type": "json_object"},
            temperature=0,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        try:
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")
            return ""
        # message content sprawdzic przed return try catch (konwersja do struktury pythonowej) Do loga wsadzic prompt[:50]
        
        
    def anomaly_check(self, image_dir: str, fps: int) -> list[dict]:
        os.makedirs(image_dir, exist_ok=True)
        images = os.listdir(image_dir)
        images = [img for img in images if img.endswith(".jpg")]
        
        prompt = """
            You are an expert in video analysis, Shown image is a single picture from a video of a recorded presentation. 
            Your task is to detect an anomaly which is one of the following: someone in the background, overly expressive body 
            language, weird face mimic or something else that does not fit the picture of someone presenting in front of other people.
            Your answer needs to be formatted as a JSON object with keys: is_anomaly (True/False), anomaly_type.
            Anomaly_type key content SHOULD ALWAYS BE TRANSLATED TO POLISH.
            """
        
        anomalies = []
        
        for idx, image in enumerate(images):
            print(f"{idx} / {len(images)}")
            img_path = os.path.join(image_dir, image)
            base64_img = self.img_to_base64(img_path)
            
            bielik_response = json.loads(self.analyze_image(prompt, base64_img))
            print(bielik_response)
            if bielik_response['is_anomaly'] == True:
                frame_no = image.split("_")[-1].split(".")[0].replace("frame", "")
                timestamp = float(frame_no) / fps
                print(f"Timestamp: {timestamp}s")
                bielik_response['timestamp'] = timestamp
                print(bielik_response)
                anomalies.append(bielik_response)
                
        print(f"Anomalies: {anomalies}")
        
        try:
            temp = {"anomalies": []}
            for anomaly in anomalies:
                temp['anomalies'].append({
                    'timestamp': anomaly['timestamp'],
                    'anomaly_type': anomaly['anomaly_type']
                })
                llm = LLMAnalyzer(self.cache_dir)
                ok, final_response, error = llm.structurize_with_gpt(str(anomaly))
                final_response = json.loads(final_response)
                temp["area"] = "Ocena wizualnych anomalii (mimika, gestykulacja, osoby trzecie)"
                temp["score"] = final_response['score']
                print(f"Final response: {final_response}")
            if type(temp) == dict:
                temp["area"] = "Ocena wizualnych anomalii (tiki, gestykulacja, osoby trzecie)"
                temp["score"] = final_response['score']
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "visual_anomalies.json"), temp)      
                return temp
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "visual_anomalies.json"), {})
            return {}
                
                
    def presenter_check(self, image_dir: str, full_text: str):
        print(f"imgdir: {image_dir}")
        images = os.listdir(image_dir)
        images = sorted([img for img in images if img.endswith(".jpg")])
        
        prompt = """
            You are an expert in video analysis, Shown image is a single picture from a video of a recorded presentation. 
            Your task is to analyze what you can see on the picture and assess all important things that describe the presenter:
            clothing, mimics, body languagea and posture. All those information shall be formatted into a JSON object and provided with keys:
            clothing, mimics, body_language, posture.
            Contains of each and every key DO NEED TO BE TRANSLATED TO POLISH.
            """
        
        checks = []
        
        for idx, image in enumerate(images):
            print(f"{idx} / {len(images)}")
            img_path = os.path.join(image_dir, image)
            base64_img = self.img_to_base64(img_path)
            
            response = json.loads(self.analyze_image(prompt, base64_img))
            checks.append(response)
                
        print(f"Checks: {checks}")
        
        llm = LLMAnalyzer(self.cache_dir)
        task = f"""
            Jesteś mistrzem analizy opisów obrazów pod kątem oceny prezentera występującego przed publiką. Twoim zadaniem jest na podstawie otrzymanych danych
            dokonać oceny prezentera pod kątem ubioru, mimiki twarzy, mowy ciała oraz postury. Twoja ocena powinna być krótka i zwięzła oraz powinna dokładnie 
            opisać prezentera pod kątem określonych wcześniej cech. Ponadto odnieś się w swojej ocenie do treści jego wystąpienie oraz na ile koreluje ona z 
            otrzymanym opisem oraz czy tworzy całość.
            Treść wystąpienia prezentera: {full_text}
        """
        ok, bielik_data, error = llm.send_to_chat('bielik', task, str(checks), 3000)
        
        if ok:
            ok, final_response, error = llm.structurize_with_gpt(bielik_data)
            
            if ok:
                try:
                    final_response = json.loads(final_response)
                    final_response["area"] = "Wizualna ocena prezentera"
                    _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "presenter_check.json"), final_response)      
                    return final_response
                    
                except Exception as e:
                    print(f"Error: {e}")
                    _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "presenter_check.json"), {})
                    return {}
        
        
    def ocr(self, image_dir: str, fps: int):
        images = os.listdir(image_dir)
        images = sorted([img for img in images if img.endswith(".jpg")])
        
        prompt = """
            You are an expert in optical character recognition from the screenshots and movies. Today, your task is to
            read and return the subtitles from the provided images. You only should look at the subtitles that are present
            on the bottom part of the screen, at the middle. Return them in JSON object format with keys: subtitles.
            Contains of each and every key DO NEED TO BE TRANSLATED TO POLISH.
            """
        
        subtitles = []
        
        for idx, image in enumerate(images):
            print(f"{idx} / {len(images)}")
            img_path = os.path.join(image_dir, image)
            base64_img = self.img_to_base64(img_path)
            
            response = json.loads(self.analyze_image(prompt, base64_img))
            frame_no = image.split("_")[-1].split(".")[0].replace("frame", "")
            response['frame_no'] = frame_no
            
            print(response)
            subtitles.append(response)
            
        def sort_by_frame_no(d):
            return d['frame_no']
        
        subtitles = sorted(subtitles, key=sort_by_frame_no)
        
        merged_text = []
        
        for idx, sub in enumerate(subtitles):
            current = sub['subtitles']
            
            if idx == 0:
                merged_text.append(current)
            else:
                 if current.strip().lower() != merged_text[-1].strip().lower():
                     merged_text.append(current)
                     
        if merged_text:
            pass
                     
        return " ".join(merged_text)
    
    
    def compare_full_text(self, full_text, ocr_text):
        prompt = """
            Jako ekspert do spraw języka polskiego zawodowo zajmujesz się porównywaniem tekstów oraz oceną ich podobieństwa. Masz 
            dzisiaj przed sobą dwa teskty: jesten pochodzi z narzędzia OCR, drugi jest traskrybcją z pliku audio. Twoim zadaniem jest porównać 
            je pod kątem podobieństwa względem siebie, pod kątem treści, struktury wypowiedzi oraz użytego języka. Oceń także ich podobieństwo 
            względem siebie w skali od 0 do 10, gdzie 10 to identyczne teksty, zaś 0 to teksty zupełnie odmienne.
        """
        
        llm = LLMAnalyzer(self.cache_dir)
        text = f"Tekst z OCR: {ocr_text}\nTekst z transkrypcji: {full_text}"
        ok, bielik_response, error = llm.send_to_chat('bielik', prompt, text, 2000)
        
        try:
            if ok:
                ok, final_response, error = llm.structurize_with_gpt(bielik_response)
                final_response = json.loads(final_response)
                if type(final_response) == dict:
                    final_response["area"] = "Ocena jasności przekazu wypowiedzi (zrozumiałość)"
                _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "compare_transcription.json"), final_response)      
                return final_response
            
        except Exception as e:
            print(f"Error: {e}")
            _ = write_to_file_with_lock(os.path.join(self.data_dir, str(self.user_id), str(self.session), "compare_transcription.json"), {})
            return {}
                     




