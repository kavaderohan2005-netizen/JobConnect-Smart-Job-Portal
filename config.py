import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'jobconnect-secret-key-2026-super-secure')
    
    # MySQL Database Configuration
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_DB = os.getenv('MYSQL_DB', 'jobconnect_db')
    
    # Default MySQL connection URI
    MYSQL_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}?charset=utf8mb4"
    
    # Fallback SQLite URI (ensures uninterrupted zero-config execution if MySQL server is offline)
    SQLITE_URI = f"sqlite:///{BASE_DIR / 'jobconnect.db'}"
    
    # Primary DB Selection
    DB_TYPE = os.getenv('DB_TYPE', 'auto') # 'mysql', 'sqlite', or 'auto'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    }
    
    # Upload configurations
    UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads' / 'resumes'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
