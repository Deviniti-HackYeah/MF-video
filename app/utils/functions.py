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
