import re
from openai import OpenAI
import os
import hashlib
import tiktoken
import json
# from json_corrector import JSONCorrector

from dotenv import load_dotenv
load_dotenv(override=True)

class LLMAnalyzer:

    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        os.makedirs(self.cache_dir, exist_ok=True)


    def _get_client(self, model):
        if "bielik" in model.lower():
            print(" * Using Bielik via vLLM w/ OpenAI API")
            api_key = os.getenv("BIELIK_API_KEY")
            base_url = os.getenv("BIELIK_MODEL_URL")
            self.model = os.getenv("BIELIK_MODEL_NAME")                              
            return OpenAI(api_key=api_key, base_url=base_url)
        
        else:
            print(" * Using OpenAI API")
            api_key = os.getenv("OPENAI_API_KEY")
            self.model = os.getenv("OPENAI_MODEL_NAME")
            return OpenAI(api_key=api_key)
            
    def fix_invalid_json(self, json_string, default_data):

        fixed_json_string = JSONCorrector().extract_json(json_string)

        print(f" * is valid: {JSONCorrector().is_valid(fixed_json_string)}")
        print(f" \n\n* is valid 2: {JSONCorrector().is_valid(json_string)[1]}")
        if JSONCorrector().is_valid(fixed_json_string) and fixed_json_string is not None:
            return True, json.loads(fixed_json_string, strict=False)
        
        if JSONCorrector().is_valid(json_string)[1] == "EMPTY_JSON":
            print(" * JSON is empty")
            return False, {}
        
        else:
        
            top_p = 1.0
            frequency_penalty = 0.0
            presence_penalty = 0.0
            model = "gpt-4-0613"

            if fixed_json_string is None:
                return False, default_data
            
            max_tokens = len(self.tokenizer.encode(fixed_json_string)) + 20
            
            if default_data == {}:
                prompt = "Popraw podany obiekt json tj. usuń ewentualne teksty, cudzysłowy nadmiarowe w wartości kluczy i inne niedozwolone znaki. Wynikiem musi być prawidłowy obiekt JSON. "
            elif default_data == []:
                prompt = "Popraw podaną tablicę obiektów json tj. usuń ewentualne teksty, cudzysłowy nadmiarowe w wartości kluczy i inne niedozwolone znaki. Wynikiem musi być prawidłowa tablica JSON. "
            
            temperature = 0.00001
            ok, data, error =  self.send_to_chat(model = model, task = prompt, text = json_string, max_tokens = max_tokens, temperature=temperature, top_p=top_p, frequency_penalty=frequency_penalty, presence_penalty=presence_penalty)

            if ok:
                try:
                    d = json.loads(data, strict=False)
                    return True, d
                except Exception as e: 
                    print("Error conversion (fix_invalid_json): " + str(e))
                    return False, default_data 
            else:
                print("Error LLM (fix_invalid_json): " + error)
                return False, default_data

    # NOT USED IN CURRENT WORKFLOW #
    def run_analisys(self, prompt, text, default_data, temperature, mt, model = "gpt-4o"):
        
        print(" * Prompt: " + prompt[:120] + "...")
        text = self.shorten_text(text, 4096)

        result = default_data  
        max_tokens = mt
        top_p = 1.0
        frequency_penalty = 0.0
        presence_penalty = 0.0
        
        ok, data, error =  self.send_to_chat(model = model, task = prompt, text = text, max_tokens = max_tokens, temperature=temperature, top_p=top_p, frequency_penalty=frequency_penalty, presence_penalty=presence_penalty)

        json_data = False

        if ok and data != []:
            try:
                if default_data == "":
                    result = data
                else:
                    data = data.replace("```json", "")
                    data = data.replace("```", "")
                    json_data = True
                    if data is not None:
                        result = json.loads(data, strict=False)
            except Exception as e:
                    
                    if json_data:
                        print(" * fixing invalid json")
                        ok_json, result = self.fix_invalid_json(data, default_data)
                        if ok_json:
                            return result
                        
                    params = prompt + text + str(temperature) + str(max_tokens) + str(top_p) + str(frequency_penalty) + str(presence_penalty) + str(data)
                    file_name = hashlib.md5(params.encode()).hexdigest() + "_error.txt"
                    file_path = os.path.join(self.cache_dir, file_name)
                    self._write_to_cache_wrong_answer(file_path, data)
                    print("Error conversion (" + prompt + "): " + str(e))

        else:
            print("Error LLM (" + prompt + "): " + error)

        return result


    def get_tokens_count(self, txt):
        return len(self.tokenizer.encode(txt))

    def shorten_text (self, txt, tokens_limit):
        
        sentences = txt.split(".")
        n_tokens = [len(self.tokenizer.encode(" " + sentence)) for sentence in sentences]
        
        chunks = []
        tokens_so_far = 0
        chunk = []

        for sentence, token in zip(sentences, n_tokens):

            if tokens_so_far + token >  tokens_limit:
                chunks.append(".".join(chunk) + ". ")
                chunk = []
                tokens_so_far = 0

            if token > tokens_limit:
                continue

            chunk.append(sentence)
            tokens_so_far += token + 1

        if len(chunk)>0:
            chunks.append(". ".join(chunk) + ".")

        return chunks[0]

    def _load_from_cache(self, file_path):
        with open(file_path, 'r') as f:
                result = f.read()
                ok = True
                error = ""
                print(" * chatGPT answer from cache")
        return ok, result, error
    
    def _write_to_cache_wrong_answer(self, file_path, result):
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(result)
            print(" * chatGPT wrong answer saved to cache")

    def _write_to_cache(self, file_path, result):
        with open(file_path, "w", encoding='utf-8') as f:
            f.write(result)
            print(" * chatGPT answer saved to cache")

    def send_to_chat(self, model, task, text, max_tokens, temperature=0.00001, top_p=1, frequency_penalty=0, presence_penalty=0):
        
        client = self._get_client('bielik')
        
        params = model + task + text + str(temperature) + str(max_tokens) + str(top_p) + str(frequency_penalty) + str(presence_penalty)
        file_name = hashlib.md5(params.encode()).hexdigest() + "_chat_gpt.txt"
        file_path = os.path.join(self.cache_dir, file_name)
        ok = False
        error = ""
        result = ""
        
        if os.path.isfile(file_path):
            ok, result, error = self._load_from_cache(file_path)
            if ok:
                return ok, result, error
            
        try:
            print(" * chatGPT answer from API")
            print(f" * model: {self.model}")
            chat_completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": task},
                    {"role": "user", "content": text},
                ],
                temperature = temperature,
                max_tokens = max_tokens,    
                top_p = top_p,
                frequency_penalty = frequency_penalty,
                presence_penalty = presence_penalty,
                # response_format= {"type": "json_object"},
            )
            choice_object = chat_completion.choices[0]
            result = choice_object.message.content
            ok = True
            self._write_to_cache(file_path, result)
            
        except Exception as e:
            print(e)
            error = str(e)
            
        return ok, result, error
    
    def send_to_chat_gpt(self, model, task, text, max_tokens, temperature=0.00001, top_p=1, frequency_penalty=0, presence_penalty=0):
        
        client = self._get_client('gpt-4o')
        
        params = model + task + text + str(temperature) + str(max_tokens) + str(top_p) + str(frequency_penalty) + str(presence_penalty)
        file_name = hashlib.md5(params.encode()).hexdigest() + "_chat_gpt.txt"
        file_path = os.path.join(self.cache_dir, file_name)
        ok = False
        error = ""
        result = ""
        
        if os.path.isfile(file_path):
            ok, result, error = self._load_from_cache(file_path)
            if ok:
                return ok, result, error
            
        try:
            print(" * chatGPT answer from API")
            print(f" * model: {self.model}")
            chat_completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": task},
                    {"role": "user", "content": text},
                ],
                temperature = temperature,
                max_tokens = max_tokens,    
                top_p = top_p,
                frequency_penalty = frequency_penalty,
                presence_penalty = presence_penalty,
                response_format= {"type": "json_object"},
            )
            choice_object = chat_completion.choices[0]
            result = choice_object.message.content
            ok = True
            self._write_to_cache(file_path, result)
            
        except Exception as e:
            print(e)
            error = str(e)
            
        return ok, result, error
    
    
# llm = LLMAnalyzer('cache')
# output = llm.send_to_chat("bielik", "Jesteś pomocnym asystentem, który ładnie odpowiada na pytania. Odpowiedz w formacie obiektu JSON z kluczami: powitanie, moje_imie", "Kim jesteś i ile masz lat?", max_tokens=100)
# print(output)
llm = LLMAnalyzer("cache")
output = llm.send_to_chat_gpt(model="gpt-4o", task="Jesteś pomocnym asystentem. Odpowiedz w formacie obiektu json z kluczami: witam, data", text="Jaki jest dzisiaj dzień?", max_tokens=1000)
print(output)
