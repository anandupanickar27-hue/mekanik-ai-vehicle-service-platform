from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()

password = quote_plus("Nripan@15")

class Config:
    SECRET_KEY = "mysecretkey123"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:{password}@localhost/mekanik"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
