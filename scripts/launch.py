"""Start only on loopback; second launch opens the existing instance."""
import json,os,sys,threading,time,urllib.request,webbrowser
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
URL='http://127.0.0.1:8765'
def health():
 try:
  with urllib.request.urlopen(URL+'/api/health/',timeout=2) as r:
   return json.load(r).get('app')=='lekcje-local'
 except Exception: return False
if health():
 webbrowser.open(URL);sys.exit(0)
if not (BASE/'backend'/'.env').exists():
 print('Brak backend/.env. Skopiuj .env.example i skonfiguruj bazę zgodnie z README.');sys.exit(1)
os.chdir(BASE/'backend');sys.path.insert(0,str(BASE/'backend'))
from config.wsgi import application
from waitress import serve
# Permit demo-only use before the real database has been prepared.
from django.conf import settings
from core.models import Student
available=[]
for alias in settings.DATABASES:
 try:
  Student.objects.using(alias).count();available.append(alias)
 except Exception: pass
if not available:
 print('Nie można odczytać żadnej bazy. Skonfiguruj bazę rzeczywistą lub uruchom Przygotuj-demo.cmd.');sys.exit(1)
if 'default' not in available:
 print('Baza rzeczywista nie jest gotowa. W aplikacji wybierz Dane testowe (demo).')
def open_when_ready():
 for _ in range(40):
  if health(): webbrowser.open(URL);return
  time.sleep(.25)
threading.Thread(target=open_when_ready,daemon=True).start()
print('Lekcje: '+URL+'\nZamknij to okno lub naciśnij Ctrl+C, aby zatrzymać aplikację.')
try: serve(application,host='127.0.0.1',port=8765,threads=4)
except OSError:
 if health(): webbrowser.open(URL)
 else: print('Port 8765 jest zajęty przez inny program.');sys.exit(1)
