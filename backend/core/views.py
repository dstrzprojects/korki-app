import csv,io,json,mimetypes,os,subprocess,tempfile
from decimal import Decimal
from pathlib import Path
from datetime import date
from django.conf import settings
from django.db import transaction,connection
from django.http import JsonResponse,HttpResponse,FileResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from .models import Student,Lesson,Payment
from .services import money,ledger
from .database import active_database,demo_available

def api(request,resource='',pk=None):
 try:
  if request.method=='GET' and resource=='dataset': return JsonResponse({'demo_configured':demo_available()})
  if resource=='demo-reset' and request.method=='POST':
   if active_database.get()!='demo': return JsonResponse({'error':'Reset dostępny tylko w trybie testowym.'},status=403)
   from .demo import seed_demo
   return JsonResponse(seed_demo(reset=True))
  if request.method=='GET' and resource=='state': return JsonResponse({**ledger(),'dataset':active_database.get()})
  if request.method=='GET' and resource=='health':
   return JsonResponse({'app':'lekcje-local','ok':True})
  if resource=='sql' and request.method=='POST': return sql(request)
  if resource=='backup' and request.method=='POST': return backup()
  if resource=='export' and request.method=='GET': return export()
  model={'students':Student,'lessons':Lesson,'payments':Payment}.get(resource)
  if not model: return JsonResponse({'error':'Nie znaleziono.'},status=404)
  if request.method not in ('POST','PUT','DELETE'): return JsonResponse({'error':'Niedozwolona metoda.'},status=405)
  with transaction.atomic(using=active_database.get()):
   # Serializes changes to one student's ledger, including concurrent payments.
   list(Student.objects.select_for_update().order_by('id'))
   obj=model.objects.get(pk=pk) if pk else model()
   if request.method=='DELETE':
    if model is Lesson:
     for p in Payment.objects.all():
      if obj.id in p.lesson_ids:
       p.lesson_ids=[i for i in p.lesson_ids if i!=obj.id]; p.save()
    obj.delete(); return JsonResponse({'ok':True})
   data=json.loads(request.body)
   if model is Student:
    obj.name=str(data['name']).strip()
    if not obj.name: raise ValueError('Podaj nazwę ucznia.')
    obj.hourly_rate=money(data['hourly_rate']); obj.extra=money(data.get('extra',0))
   else:
    obj.student=Student.objects.get(pk=int(data['student_id']))
    if model is Lesson:
     obj.date=parse_datetime(data['date'])
     if obj.date is None: raise ValueError('Podaj datę i godzinę.')
     if timezone.is_naive(obj.date): obj.date=timezone.make_aware(obj.date)
     obj.minutes=int(data['minutes'])
     if not 1<=obj.minutes<=1440: raise ValueError('Czas: od 1 do 1440 minut.')
     obj.hourly_rate=money(data['hourly_rate']); obj.extra=money(data.get('extra',0))
     obj.manual_price=bool(data.get('manual_price',False))
     obj.price=money(data['price']) if obj.manual_price else money(obj.hourly_rate*Decimal(obj.minutes)/60+obj.extra)
     if pk and Lesson.objects.get(pk=pk).student_id!=obj.student_id: raise ValueError('Nie można zmienić ucznia istniejącej lekcji.')
    else:
     obj.date=date.fromisoformat(data['date']); obj.amount=money(data['amount'])
     if obj.amount<=0: raise ValueError('Wpłata musi być dodatnia.')
     obj.method=data['method']
     if obj.method not in ('BLIK','przelew','gotówka'): raise ValueError('Nieznana metoda płatności.')
     obj.lesson_ids=list(dict.fromkeys(int(x) for x in data.get('lesson_ids',[])))
     if Lesson.objects.filter(pk__in=obj.lesson_ids,student=obj.student).count()!=len(obj.lesson_ids): raise ValueError('Wybrane lekcje muszą należeć do ucznia.')
   obj.notes=str(data.get('notes',''))
   obj.full_clean(); obj.save()
   return JsonResponse({'ok':True,'id':obj.id})
 except Exception as e:
  from django.core.exceptions import ValidationError
  from django.db.models.deletion import ProtectedError
  if isinstance(e,ProtectedError): message='Najpierw usuń lekcje i wpłaty ucznia.'
  elif isinstance(e,(ValueError,KeyError,ValidationError,Student.DoesNotExist,Lesson.DoesNotExist,Payment.DoesNotExist)): message=str(e)
  else:
   import psycopg
   if isinstance(e,psycopg.Error) and resource=='sql': message=e.diag.message_primary or 'Błąd połączenia SQL. Sprawdź konta i hasła w .env.'
   elif isinstance(e,FileNotFoundError) and resource=='backup': message='Nie znaleziono pg_dump. Ustaw PG_DUMP w backend/.env.'
   else: message='Operacja nie powiodła się. Sprawdź połączenie i strukturę bazy.'
  return JsonResponse({'error':message},status=400)

def sql(request):
 import psycopg
 from psycopg import ClientCursor
 data=json.loads(request.body); query=str(data.get('query','')).strip(); write=data.get('write') is True
 if not query or len(query)>50000: raise ValueError('Wpisz zapytanie (maks. 50 000 znaków).')
 db=settings.DATABASES[active_database.get()]
 prefix='DEMO_' if active_database.get()=='demo' else ''
 user=os.getenv(prefix+('SQL_WRITE_USER' if write else 'SQL_READ_USER'),'lekcje_demo_sql_write' if prefix and write else 'lekcje_demo_sql_read' if prefix else 'lekcje_sql_write' if write else 'lekcje_sql_read')
 password=os.getenv(prefix+('SQL_WRITE_PASSWORD' if write else 'SQL_READ_PASSWORD'),'')
 # Separate least-privilege roles: read-only enforced by grants AND transaction.
 with psycopg.connect(dbname=db['NAME'],user=user,password=password,host=db['HOST'],port=db['PORT']) as conn:
  with conn.cursor() as cur:
   cur.execute('SET LOCAL statement_timeout = 5000')
   cur.execute('SET LOCAL lock_timeout = 1500')
   if not write: cur.execute('SET TRANSACTION READ ONLY')
   # Extended protocol with parameters rejects multiple SQL statements.
   with conn.cursor() as q:
    q.execute(query,(),prepare=True)
    columns=[c.name for c in q.description] if q.description else []
    rows=q.fetchmany(1001) if columns else []
    count=q.rowcount; status=q.statusmessage
    result={'columns':columns,'rows':[[str(v) if isinstance(v,(Decimal,date)) else v for v in row] for row in rows[:1000]],'truncated':len(rows)>1000,'status':status,'count':count}
 return JsonResponse(result,json_dumps_params={'default':str})

def export():
 out=io.StringIO(); writer=csv.writer(out,delimiter=';'); writer.writerow(['id','uczen','data','minuty','cena','zaplacono','do_zaplaty','metody','notatka'])
 for x in ledger()['lessons']: writer.writerow([x['id'],safe_csv(x['student']),x['date'],x['minutes'],x['price'],x['paid'],x['due'],', '.join(x['methods']),safe_csv(x['notes'])])
 r=HttpResponse('﻿'+out.getvalue(),content_type='text/csv; charset=utf-8'); r['Content-Disposition']='attachment; filename="lekcje.csv"'; return r

def safe_csv(v): return "'"+str(v) if str(v).startswith(('=','+','-','@','\t','\r')) else v

def backup():
 db=settings.DATABASES[active_database.get()]; env=os.environ.copy(); env['PGPASSWORD']=db['PASSWORD']
 with tempfile.TemporaryDirectory() as tmp:
  dest=Path(tmp)/'lekcje.dump'
  subprocess.run([os.getenv('PG_DUMP','pg_dump'),'-h',db['HOST'],'-p',str(db['PORT']),'-U',db['USER'],'-d',db['NAME'],'-Fc','-f',str(dest)],env=env,check=True,capture_output=True,timeout=120)
  r=HttpResponse(dest.read_bytes(),content_type='application/octet-stream'); r['Content-Disposition']='attachment; filename="lekcje-backup.dump"'; return r

@ensure_csrf_cookie
def frontend(request,path=''):
 base=settings.BASE_DIR.parent/'frontend'/'dist'/'browser'
 file=(base/path).resolve()
 if not file.is_relative_to(base.resolve()): return HttpResponse(status=404)
 if not path or not file.is_file(): file=base/'index.html'
 if not file.exists(): return HttpResponse('Najpierw wykonaj npm run build w folderze frontend.',status=503)
 return FileResponse(file.open('rb'),content_type=mimetypes.guess_type(str(file))[0] or 'application/octet-stream')
