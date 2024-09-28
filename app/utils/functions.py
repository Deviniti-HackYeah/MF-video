import datetime
import random
import hashlib
import os

def generate_hash(password):
    hash_salt = os.getenv("HASH_SALT", '123')
    return hashlib.sha256((password + hash_salt).encode()).hexdigest()

def check_hash(password, hash):
    return generate_hash(password) == hash