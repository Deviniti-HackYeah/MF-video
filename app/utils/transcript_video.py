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
        
        whisper_model = whisper.load_model('large')
        # result = whisper.transcribe(whisper_model, file_path, fp16=False, beam_size=5, best_of=5, temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0))
        
        result = whisper.transcribe(whisper_model, 
                                    file_path, 
                                    fp16=False, 
                                    beam_size=5, 
                                    best_of=5, 
                                    temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0), 
                                    detect_disfluencies=True)
        
        
        
        print(f"Transcpition result: {result["text"]}")
        print(f"Result: {result}")
        output = {
            "result": result
        }
        
        return output        
        # return jsonify({"status": "OK", "message": "Video is now processing. You can check if result is ready using ready_suffix"})
        
    def word_dict(self,
                      transcription_output: dict) -> list[dict]:
        
        print(f"Transcription text: {transcription_output['result']['text']}")        
        segments = transcription_output['result']['segments']
        
        words = segments[0]['words']        
        word_dict = []
        
        for word in words:
            temp = {}
            w = word['text']
            start = word['start']
            end = word['end']
            length = end - start
            if "*" in w:
                print(f"Text: PAUSE | Start: {start} | End: {end} | Length: {length:.2f}s | ")
                temp = {
                    "text": "[*]",
                    "start": start,
                    "end": end,
                    "length": length
                }                
                word_dict.append(temp)
            else:
                print(f"Text: {w} | Start: {start} | End: {end} | Length: {length:.2f}s | ")
                temp = {
                    "text": w,
                    "start": start,
                    "end": end,
                    "length": length
                }                
                word_dict.append(temp)
                
        return word_dict
                
                
    def get_full_text(self, transcription_output: dict) -> str:
        return transcription_output['result']['text']
    
    
    def text_stats(self, word_dict: dict) -> dict:
        for word in word_dict:
            if "*" not in word['text']:
                start = word['start']
                print(f"START: {start}")
                break
                
        for word in reversed(word_dict):
            if "*" not in word['text']:
                end = word['end']
                print(f"END: {end}")
                break
    
        total_talking_time = end - start
        print(total_talking_time)
    
    
tv = TranscriptVideo()
fp = "/Users/pkiszczak/Downloads/wetransfer_hackyeah-2024-breakwordtraps_2024-09-28_0449/HY_2024_film_08.mp4"
tv.convert_to_mp3(file_path=fp,
                    output_name=f"{fp.split("/")[-1].split(".")[0]}.mp3")
output = tv.transcript_video("123", "321", "TEST", "/Users/pkiszczak/projects/deviniti/MF-video/app/utils/HY_2024_film_08.mp3")
word_dict = tv.word_dict(output)
full_text = tv.get_full_text(output)
tv.text_stats(word_dict)