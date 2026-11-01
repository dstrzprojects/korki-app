from django.core.management.base import BaseCommand,CommandError
from django.conf import settings
from core.models import Student,Lesson,Payment
import os,psycopg
class Command(BaseCommand):
 help='Sprawdza połączenia i uprawnienia PostgreSQL bez modyfikowania danych.'
 def handle(self,*args,**options):
  try:
   Student.objects.count();Lesson.objects.count();Payment.objects.count()
   self.stdout.write('OK: konto Django i tabele.')
   db=settings.DATABASES['default']
   for mode in ['READ','WRITE']:
    with psycopg.connect(dbname=db['NAME'],user=os.environ['SQL_'+mode+'_USER'],password=os.environ['SQL_'+mode+'_PASSWORD'],host=db['HOST'],port=db['PORT']) as conn:
     with conn.cursor() as cur:
      for table in ['uczniowie','lekcje','wplaty']:
       cur.execute('SELECT has_table_privilege(current_user,%s,%s)',(table,'SELECT'))
       if not cur.fetchone()[0]: raise ValueError('Brak SELECT: '+table)
       for privilege in ['INSERT','UPDATE','DELETE']:
        cur.execute('SELECT has_table_privilege(current_user,%s,%s)',(table,privilege))
        if cur.fetchone()[0] != (mode=='WRITE'): raise ValueError('Nieprawidłowe uprawnienia '+mode+' '+table+' '+privilege)
      cur.execute('SELECT * FROM lekcje LIMIT 1',(),prepare=True);cur.fetchall()
      if mode=='READ':
       cur.execute('SHOW default_transaction_read_only')
       if cur.fetchone()[0]!='on': raise ValueError('Konto odczytu nie ma default_transaction_read_only=on')
    self.stdout.write('OK: konto SQL '+mode+'.')
  except Exception as e:
   raise CommandError('Sprawdzenie nie powiodło się. Zweryfikuj .env, migracje i skrypt sql/02_permissions.sql. '+type(e).__name__)
  self.stdout.write(self.style.SUCCESS('Konfiguracja PostgreSQL jest poprawna.'))
