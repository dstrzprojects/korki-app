from pathlib import Path
import os
from dotenv import load_dotenv
BASE_DIR=Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
SECRET_KEY=os.getenv('SECRET_KEY','local-only-no-public-deployment')
DEBUG=False
ALLOWED_HOSTS=['127.0.0.1','localhost','testserver']
INSTALLED_APPS=['core']
MIDDLEWARE=['core.middleware.LocalOnly','django.middleware.security.SecurityMiddleware','django.middleware.csrf.CsrfViewMiddleware']
ROOT_URLCONF='config.urls'
DATABASES={'default':{'ENGINE':'django.db.backends.postgresql','NAME':os.getenv('DB_NAME','lekcje'),'USER':os.getenv('DB_USER','lekcje_app'),'PASSWORD':os.getenv('DB_PASSWORD',''),'HOST':os.getenv('DB_HOST','127.0.0.1'),'PORT':os.getenv('DB_PORT','5432')}}
if os.getenv('DEMO_DB_PASSWORD'):
 DATABASES['demo']={**DATABASES['default'],'NAME':os.getenv('DEMO_DB_NAME','lekcje_demo'),'USER':os.getenv('DEMO_DB_USER','lekcje_demo_app'),'PASSWORD':os.getenv('DEMO_DB_PASSWORD')}
DATABASE_ROUTERS=['core.database.DatasetRouter']
if os.getenv('TEST_SQLITE')=='1':
 DATABASES={alias:{'ENGINE':'django.db.backends.sqlite3','NAME':':memory:'} for alias in ('default','demo')}
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
USE_TZ=True
TIME_ZONE='Europe/Warsaw'
LANGUAGE_CODE='pl'
