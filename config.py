import os
import re
from urllib.parse import urlparse, parse_qs

# Load .env file manually or with python-dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback manual loader for .env
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))

# Default Database Settings
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'anemiadb')
SECRET_KEY = os.getenv('SECRET_KEY', 'anemify-secret-key-default')

# Handle DB_URL if provided (e.g. jdbc:mysql://... or mysql+pymysql://...)
db_url_env = os.getenv('DB_URL', '').strip()

if db_url_env:
    if db_url_env.startswith('jdbc:mysql://'):
        # Convert JDBC URL format to components
        # Format: jdbc:mysql://localhost:3306/anemiadb?user=root&password=123
        raw_url = db_url_env[13:] # trim jdbc:mysql://
        parsed = urlparse('http://' + raw_url)
        DB_HOST = parsed.hostname or DB_HOST
        DB_PORT = parsed.port or DB_PORT
        DB_NAME = parsed.path.lstrip('/') or DB_NAME
        query_params = parse_qs(parsed.query)
        if 'user' in query_params:
            DB_USER = query_params['user'][0]
        if 'password' in query_params:
            DB_PASSWORD = query_params['password'][0]
    elif '://' in db_url_env:
        # Standard connection URI
        parsed = urlparse(db_url_env)
        DB_HOST = parsed.hostname or DB_HOST
        DB_PORT = parsed.port or DB_PORT
        DB_USER = parsed.username or DB_USER
        DB_PASSWORD = parsed.password or ''
        DB_NAME = parsed.path.lstrip('/') or DB_NAME

# Construct SQLAlchemy URI
if DB_PASSWORD:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
