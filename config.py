import os

class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "C7u83mAn1AR3aLlyS3cr3"
    SCHEDULER_API_ENABLED = True
    DEBUG = True
