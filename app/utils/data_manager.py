import os
import json
import random

class DataManager():

    def __init__(self, customer_id, language, file_name, file):
        self.data_dir = os.environ.get('DATA_DIR')
        self.customer_id = customer_id
        self.file = file
        self.file_name = file_name
        self.language = language       

    def save(self):

        customer_dir = os.path.join(self.data_dir, str(self.customer_id))
        session = random.randint(1, 999999999)
        session_dir = os.path.join(customer_dir, str(session))

        if not os.path.exists(customer_dir):
            os.makedirs(customer_dir)

        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        data = {
            "customer_id": self.customer_id,
            "language": self.language,
            "file_name": self.file_name,
            "session": session,
        }

        with open(os.path.join(session_dir, 'data.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        save_path = os.path.join(session_dir, self.file_name)
        print(f" * Saving file: {save_path}")
        self.file.save(save_path)
        return "OK", 200, session
