import os
from dotenv import load_dotenv
load_dotenv()
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
port = os.getenv("DB_PORT")
db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"