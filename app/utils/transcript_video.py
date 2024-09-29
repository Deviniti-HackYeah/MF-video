import os
from flask import jsonify
from openai import AzureOpenAI
import whisper_timestamped as whisper
from pydub import AudioSegment
import numpy as np
from app.utils.text_analyzer import TextAnalyzer
import os
from openai import AzureOpenAI
from text_analyzer import TextAnalyzer
from dotenv import load_dotenv

load_dotenv()
# from app import whisper_model

class TranscriptVideo:
    def __init__(self):
        pass

    def __str__(self):
        return "Transcript Video using Whisper"
    
    def convert_to_mp3(self, file_path: str, output_name: str) -> bool:
        """
        The function `convert_to_mp3` takes a file path and output name as input, converts the file to
        .mp3 format, and returns a boolean indicating the success of the conversion.
        
        :param file_path: The `file_path` parameter in the `convert_to_mp3` function is a string that
        represents the path to the audio file that you want to convert to MP3 format. This parameter
        should include the file name and extension (e.g., "audio.wav", "music.mp4")
        :type file_path: str
        :param output_name: The `output_name` parameter in the `convert_to_mp3` function is a string that
        represents the name of the output file after the conversion process. This is the name that the
        converted audio file will be saved as in .mp3 format
        :type output_name: str
        :return: The function `convert_to_mp3` is returning a boolean value. It returns `True` if the
        conversion is successful and `False` if the conversion fails.
        """
        
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
        """
        The function `transcript_video` transcribes a video for a customer and session using a specified
        action and returns the transcription result.
        
        :param customer_id: The `customer_id` parameter is a string that represents the unique
        identifier of the customer for whom the video is being transcribed. It helps in identifying and
        associating the transcripted video with the specific customer
        :type customer_id: str
        :param session: The `session` parameter in the `transcript_video` function is typically used to
        identify a specific session or interaction related to the customer. It could be a unique
        identifier for a particular video session or conversation between the customer and your system.
        This parameter helps in tracking and organizing the transcripts based on different
        :type session: str
        :param action: The `action` parameter in the `transcript_video` method represents the specific
        action or process that will be used during the transcription of the video for the given customer
        and session. It could be a description of the transcription method being applied, such as the
        model or algorithm used for transcription
        :type action: str
        :param file_path: The `file_path` parameter in the `transcript_video` function represents the
        file path to the video file that you want to transcribe. This should be the location of the
        video file on your system that you want to process and generate a transcript from. Make sure to
        provide the full path to
        :type file_path: str
        :return: The `transcript_video` method returns a dictionary with the transcription result under
        the key "result".
        """
        
        print(f"Transcripting video for customer {customer_id} and session {session} using {action}")
        
        if not os.environ.get("WHISPER_API_KEY"):
            whisper_model = whisper.load_model('small')
        
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
        
        else:
            if os.environ.get("WHISPER_API_KEY"):
                client = AzureOpenAI(
                api_key=os.environ.get('WHISPER_API_KEY'),
                api_version="2024-08-01-preview",
                azure_endpoint=os.environ.get('WHISPER_API_URL'),
            )
                model = "whisper"
                
            try:
                audio_file= open(file_path, "rb")
                print(f"Transcribing audio file: {file_path.split("/")[-1]}")
                output = client.audio.transcriptions.create(model=model, file=audio_file, response_format="verbose_json", timestamp_granularities=["word", "segment"])
                return output
            except Exception as e:
                print(f"Error: {e}")
            except Exception as e:
                self.logger.error(" *** Error: ", str(e))
                print("Error: ", str(e))
                return ""
        # return jsonify({"status": "OK", "message": "Video is now processing. You can check if result is ready using ready_suffix"})
        
    def word_dict(self, transcription_output: dict) -> list[dict]:        
        """
        This Python function processes transcription output to create a list of dictionaries containing
        information about words and pauses.
        
        :param transcription_output: The `word_dict` function takes a transcription output in the form
        of a dictionary and extracts information about the words in the transcription. It prints details
        about each word such as the text, start time, end time, and length. If a word contains "*", it
        prints "PAUSE" instead of the
        :type transcription_output: dict
        :return: The function `word_dict` returns a list of dictionaries where each dictionary
        represents a word from the transcription output. The dictionaries contain the text of the word,
        its start and end timestamps, and the calculated length of the word. If the word contains a "*",
        it is represented as "[*]" in the text field of the dictionary.
        """
        
        print(f"Transcription output: {transcription_output}")
        # print(f"Transcription text: {transcription_output['result']['text']}")        
        # segments = transcription_output['result']['segments']
        
        # words = segments[0]['words']        
        word_dict = []
        
        for word in transcription_output.words:
            temp = {}
            w = word.word
            start = word.start
            end = word.end
            length = end - start
            print(f"Text: {w} | Start: {start} | End: {end} | Length: {length:.2f}s")
            temp = {
                "text": w,
                "start": start,
                "end": end,
                "length": length
            }                
            word_dict.append(temp)
           
        return word_dict
    
    
    def find_pauses(self, word_dict):
        word_dict_w_pauses = []
        
        for idx, word in enumerate(word_dict):
            if word['end'] != word_dict[idx+1]['start']:
                print('diff')
            else:
                print('no diff')
            
            
                
                
    def get_full_text(self, transcription_output: dict) -> str:
        """
        This Python function `get_full_text` extracts and returns the full text from a transcription
        output dictionary.
        
        :param transcription_output: The `get_full_text` function takes two parameters: `self` and
        `transcription_output`. The `transcription_output` parameter is expected to be a dictionary
        containing the transcription result. The function retrieves the full text from the transcription
        output dictionary and returns it as a string
        :type transcription_output: dict
        :return: The function `get_full_text` is returning the value of the 'text' key from the 'result'
        dictionary within the `transcription_output` dictionary as a string.
        """
        
        return transcription_output.text
    
    
    def total_talking_time(self, word_dict: list[dict]) -> float:
        """
        This function calculates the total talking time based on the start and end timestamps of words
        in a list of dictionaries, excluding words containing "*".
        
        :param word_dict: The `word_dict` parameter is a list of dictionaries where each dictionary
        represents a word spoken during a conversation. Each dictionary contains the keys 'text',
        'start', and 'end'. The 'text' key holds the spoken word, the 'start' key holds the start time
        of when the word
        :type word_dict: list[dict]
        :return: the total talking time calculated as the difference between the end time and the start
        time of the words in the provided word dictionary.
        """
        
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
        return total_talking_time
    
    
    def pause_counter(self, word_dict: list[dict]) -> tuple[float, float]:
        """
        This Python function calculates the total number of pauses and the total pause time based on a
        list of dictionaries containing text and timing information.
        
        :param word_dict: A list of dictionaries where each dictionary represents a word with the
        following keys:
        :type word_dict: list[dict]
        :return: The function `pause_counter` returns a tuple containing two values: the number of
        pauses (`pause_count`) and the total pause time (`total_pause_time`).
        """
        
        pause_count = 0
        total_pause_time = 0
        for word in word_dict:
            if "*" in word['text'] and not np.isclose(word['start'], 0):
                pause_count += 1
                total_pause_time += word['end'] - word['start']
                
        return pause_count, total_pause_time
    
    
    def get_full_text_from_words(self, word_dict: list[dict]) -> str:
        """
        This function filters out words containing "*" from a list of dictionaries and returns a list of
        the remaining words.
        
        :param word_dict: A list of dictionaries where each dictionary represents a word. Each
        dictionary has a key 'text' which contains the text of the word. The function
        `get_full_text_from_words` iterates through this list and appends the 'text' value of each
        dictionary to `full_text_list` if the
        :type word_dict: list[dict]
        """
        full_text_list = []
        for w in word_dict:
            if "*" not in w['text']:
                full_text_list.append(w['text'])
            
        print(full_text_list)
        
        full_text = " ".join(full_text_list)
        return full_text
    
    
    def word_count(self, word_dict: list[dict]) -> int:
        """
        The function `word_count` returns the length of a list of dictionaries representing word counts.
        
        :param word_dict: The `word_dict` parameter in the `word_count` function is a list of
        dictionaries. Each dictionary in the list likely represents a word and its corresponding count
        or some other related information. The function simply returns the length of the `word_dict`
        list, which would give the number of dictionaries (
        :type word_dict: list[dict]
        :return: the length of the list `word_dict`, which represents the number of dictionaries in the
        list.
        """
        return len(word_dict)
    
    
    def text_stats(self, word_dict: dict) -> dict:
        """
        The `text_stats` function calculates various statistics such as total talking time, number of
        pauses, word count, words per second, and readability metrics for a given text.
        
        :param word_dict: The `text_stats` method you provided seems to be a part of a class and it
        calculates various statistics based on the input `word_dict`. The `word_dict` parameter likely
        contains information about words spoken or written during a specific text or speech
        :type word_dict: dict
        :return: The `text_stats` method returns a dictionary containing various statistics related to
        the input text data. The dictionary includes information such as total talking time, number of
        pauses, total pause time, word count, words per second, and readability metrics like Gunning Fog
        index, Flesch Reading Ease score, Flesch-Kincaid Grade Level, and Dale-Chall readability score.
        """
        
        # Total talking time
        total_talking_time = self.total_talking_time(word_dict)
        
        # No of pauses
        pause_count, total_pause_time = self.pause_counter(word_dict)
        
        # Word count
        word_count = self.word_count(word_dict)
        
        # Words per second
        words_per_second = word_count / total_talking_time
        
        # Readibility metrics
        ta = TextAnalyzer()
        full_text = self.get_full_text_from_words(word_dict)
        full_text_cleared = full_text.replace(".", "").replace(",", "").replace(" ", "")
        gunning_fog = ta.gunning_fog(full_text)
        reading_ease, grade, dale_chall = ta.readibility(full_text)
                        
        stats = {
            'total_talking_time': total_talking_time,
            'pause_count': pause_count,
            'total_pause_time': total_pause_time,
            'word_count': word_count,
            'words_per_second': words_per_second,
            'letter_count': len(full_text_cleared),
            'readibility':
                {
                    'gunning_fog': gunning_fog,
                    'flesch_reading_ease': reading_ease,
                    'flesch_kincaid_grade_level': grade,
                    'dale_chall_readibility_score': dale_chall
                }
        }
        print(stats)
        return stats
    
    
# tv = TranscriptVideo()
# fp = "/Users/pkiszczak/Downloads/wetransfer_hackyeah-2024-breakwordtraps_2024-09-28_0449/HY_2024_film_08.mp4"
# tv.convert_to_mp3(file_path=fp,
#                     output_name=f"{fp.split("/")[-1].split(".")[0]}.mp3")
# output = tv.transcript_video("123", "321", "TEST", "/Users/pkiszczak/projects/deviniti/MF-video/app/utils/HY_2024_film_08.mp3")
# word_dict = tv.word_dict(output)
# full_text = tv.get_full_text(output)
# tv.text_stats(word_dict)