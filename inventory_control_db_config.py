from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

host_name = os.getenv('DB_HOST')
user_name = os.getenv('DB_USER')
user_password = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')
