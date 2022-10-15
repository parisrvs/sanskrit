import os

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

SENDER_NAME = os.getenv("SENDER_NAME")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

reserved_keywords = [
    "parijat",
    "sanskrit",
    "vishnu",
    "shiva",
    "krishna",
    "panini",
    "om"
]