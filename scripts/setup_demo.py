"""One-time setup of a separate PostgreSQL demo database, never the real one."""
import getpass,os,secrets,subprocess,sys
from pathlib import Path
from dotenv import dotenv_values
import psycopg
from psycopg import sql
BASE=Path(__file__).resolve().parents[1];env_file=BASE/'backend'/'.env'
if not env_file.exists():
 print('Najpierw uruchom Zainstaluj.cmd i skonfiguruj backend/.env.');sys.exit(1)
cfg=dict(dotenv_values(env_file));host=cfg.get('DB_HOST','127.0.0.1');port=cfg.get('DB_PORT','5432')
if cfg.get('DB_NAME','lekcje')=='lekcje_demo':
 print('Nazwa lekcje_demo jest zajeta przez baze rzeczywista. Przerwano.');sys.exit(1)
keys={'DEMO_DB_NAME':'lekcje_demo','DEMO_DB_USER':'lekcje_demo_app','DEMO_DB_PASSWORD':secrets.token_urlsafe(24),'DEMO_SQL_READ_USER':'lekcje_demo_sql_read','DEMO_SQL_READ_PASSWORD':secrets.token_urlsafe(24),'DEMO_SQL_WRITE_USER':'lekcje_demo_sql_write','DEMO_SQL_WRITE_PASSWORD':secrets.token_urlsafe(24)}
# Preserve credentials on rerun, but refuse unexpected role or database names.
for k,v in keys.items():
 if k in cfg and cfg[k]:
  if not k.endswith('PASSWORD') and cfg[k]!=v:
   print('Niestandardowa konfiguracja demo. Przerwano bez zmian.');sys.exit(1)
  keys[k]=cfg[k]
print('Utworzenie osobnej bazy lekcje_demo. Baza rzeczywista nie bedzie zmieniana.')
password=getpass.getpass('Haslo administratora PostgreSQL (postgres): ')
try:
 with psycopg.connect(host=host,port=port,dbname='postgres',user='postgres',password=password,autocommit=True) as admin:
  # Retain generated passwords before DDL so interrupted setup can be resumed.
  additions={k:v for k,v in keys.items() if not cfg.get(k)}
  if additions:
   with env_file.open('a',encoding='utf-8') as f:
    f.write('\n# Osobna baza demonstracyjna\n')
    for k,v in additions.items():f.write(k+'='+v+'\n')
  for user_key,pw_key in [('DEMO_DB_USER','DEMO_DB_PASSWORD'),('DEMO_SQL_READ_USER','DEMO_SQL_READ_PASSWORD'),('DEMO_SQL_WRITE_USER','DEMO_SQL_WRITE_PASSWORD')]:
   user=keys[user_key]
   if not admin.execute('SELECT 1 FROM pg_roles WHERE rolname=%s',(user,)).fetchone():
    admin.execute(sql.SQL('CREATE ROLE {} LOGIN PASSWORD {} NOSUPERUSER NOCREATEDB NOCREATEROLE').format(sql.Identifier(user),sql.Literal(keys[pw_key])))
  exists=admin.execute('SELECT pg_get_userbyid(datdba) FROM pg_database WHERE datname=%s',('lekcje_demo',)).fetchone()
  if exists and exists[0]!=keys['DEMO_DB_USER']:raise ValueError('Istniejaca baza lekcje_demo ma innego wlasciciela. Przerwano.')
  if not exists:admin.execute('CREATE DATABASE lekcje_demo OWNER lekcje_demo_app')
  admin.execute('REVOKE ALL ON DATABASE lekcje_demo FROM PUBLIC')
  admin.execute('GRANT CONNECT ON DATABASE lekcje_demo TO lekcje_demo_sql_read,lekcje_demo_sql_write')
 child_env=os.environ.copy();child_env.update({k:str(v) for k,v in keys.items()})
 # No --database default anywhere in this script.
 subprocess.run([sys.executable,str(BASE/'backend'/'manage.py'),'migrate','--database=demo'],env=child_env,check=True)
 with psycopg.connect(host=host,port=port,dbname='lekcje_demo',user='postgres',password=password) as admin:
  admin.execute('REVOKE CREATE ON SCHEMA public FROM PUBLIC')
  admin.execute('GRANT USAGE ON SCHEMA public TO lekcje_demo_sql_read,lekcje_demo_sql_write')
  admin.execute('GRANT SELECT ON uczniowie,lekcje,wplaty TO lekcje_demo_sql_read')
  admin.execute('GRANT SELECT,INSERT,UPDATE,DELETE ON uczniowie,lekcje,wplaty TO lekcje_demo_sql_write')
  admin.execute('GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO lekcje_demo_sql_write')
  admin.execute('CREATE SCHEMA IF NOT EXISTS cwiczenia AUTHORIZATION lekcje_demo_sql_write')
  admin.execute('GRANT USAGE ON SCHEMA cwiczenia TO lekcje_demo_sql_read')
  admin.execute('ALTER DEFAULT PRIVILEGES FOR ROLE lekcje_demo_sql_write IN SCHEMA cwiczenia GRANT SELECT ON TABLES TO lekcje_demo_sql_read')
  admin.execute('ALTER ROLE lekcje_demo_sql_read SET default_transaction_read_only=on')
  for role in ['lekcje_demo_sql_read','lekcje_demo_sql_write']:
   admin.execute(sql.SQL("ALTER ROLE {} SET statement_timeout='5s'").format(sql.Identifier(role)))
   admin.execute(sql.SQL('ALTER ROLE {} SET search_path=public,cwiczenia').format(sql.Identifier(role)))
 # Seed only a new/empty dataset, never reset existing demo changes on setup rerun.
 code="import django;django.setup();from core.models import Student;from core.demo import seed_demo;print(seed_demo() if not Student.objects.using('demo').exists() else 'Baza demo ma juz dane: pozostawiono bez zmian.')"
 child_env['DJANGO_SETTINGS_MODULE']='config.settings'
 subprocess.run([sys.executable,'-c',code],cwd=BASE/'backend',env=child_env,check=True)
 print('Gotowe. Uruchom ponownie aplikacje i wybierz Dane testowe (demo).')
except Exception as e:
 print('Nie udalo sie przygotowac demo. Sprawdz usluge PostgreSQL i haslo administratora. Typ bledu: '+type(e).__name__)
 sys.exit(1)
