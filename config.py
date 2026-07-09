from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "")

    db_user = os.getenv("DB_USER", "root")
    db_password = quote_plus(os.getenv("DB_PASSWORD", ""))
    db_host = os.getenv("DB_HOST", "localhost")
    db_name = os.getenv("DB_NAME", "mekanik")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False