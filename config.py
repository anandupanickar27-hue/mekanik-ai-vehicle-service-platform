from urllib.parse import quote_plus

password = quote_plus("Nripan@15")

class Config:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:{password}@localhost/mekanik"
    SQLALCHEMY_TRACK_MODIFICATIONS = False