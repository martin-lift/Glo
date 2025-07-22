import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://glo_db_user:-67df^&DF.@localhost/glo_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
