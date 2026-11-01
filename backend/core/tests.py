import json
from decimal import Decimal
from django.test import TestCase,Client
from .models import Student,Lesson,Payment
from .services import ledger
class LedgerTests(TestCase):
 def setUp(self): self.s=Student.objects.create(name='Uczeń testowy',hourly_rate=100,extra=20)
 def post(self,resource,data): return self.client.post('/api/'+resource+'/',data=json.dumps(data),content_type='application/json')
 def lesson(self,day=1,**kwargs):
  data={'student_id':self.s.id,'date':f'2026-10-{day:02}T15:00:00+02:00','minutes':90,'hourly_rate':'100','extra':'20','manual_price':False,'notes':''};data.update(kwargs)
  r=self.post('lessons',data);self.assertEqual(r.status_code,200,r.content);return r.json()['id']
 def pay(self,amount,ids=None):
  r=self.post('payments',{'student_id':self.s.id,'date':'2026-10-01','amount':amount,'method':'BLIK','lesson_ids':ids or [],'notes':''});self.assertEqual(r.status_code,200,r.content);return r.json()['id']
 def test_price_snapshot_override_and_rounding(self):
  id=self.lesson();self.assertEqual(Lesson.objects.get(pk=id).price,Decimal('170'))
  self.s.hourly_rate=200;self.s.save();self.assertEqual(Lesson.objects.get(pk=id).price,Decimal('170'))
  id2=self.lesson(2,manual_price=True,price='99.99');self.assertEqual(Lesson.objects.get(pk=id2).price,Decimal('99.99'))
  id3=self.lesson(3,minutes=1,hourly_rate='100',extra='0');self.assertEqual(Lesson.objects.get(pk=id3).price,Decimal('1.67'))
 def test_partial_combined_and_credit(self):
  self.lesson();self.lesson(2);self.pay('200');d=ledger();self.assertEqual([x['due'] for x in d['lessons']],['0.00','140.00'])
  self.pay('200');self.assertEqual(ledger()['students'][0]['credit'],'60.00')
  self.lesson(3);d=ledger();self.assertEqual(d['students'][0]['credit'],'0.00');self.assertEqual(d['lessons'][2]['due'],'110.00')
 def test_manual_targets_and_delete(self):
  a=self.lesson();b=self.lesson(2);p=self.pay('200',[b]);d=ledger();self.assertEqual(d['lessons'][0]['due'],'170.00');self.assertEqual(d['students'][0]['credit'],'30.00')
  r=self.client.delete(f'/api/lessons/{b}/');self.assertEqual(r.status_code,200);self.assertEqual(Payment.objects.get(pk=p).lesson_ids,[])
  self.assertEqual(ledger()['lessons'][0]['due'],'0.00')
 def test_reject_invalid_and_cross_student(self):
  b=self.lesson();other=Student.objects.create(name='Inny',hourly_rate=100)
  r=self.post('payments',{'student_id':other.id,'date':'2026-10-01','amount':20,'method':'BLIK','lesson_ids':[b]});self.assertEqual(r.status_code,400)
  r=self.post('payments',{'student_id':self.s.id,'date':'2026-10-01','amount':-1,'method':'BLIK'});self.assertEqual(r.status_code,400)
  self.assertEqual(self.client.delete(f'/api/students/{self.s.id}/').status_code,400)
 def test_csrf_and_origin(self):
  c=Client(enforce_csrf_checks=True);self.assertEqual(c.post('/api/students/',data='{}',content_type='application/json').status_code,403)
  self.assertEqual(self.client.get('/api/state/',HTTP_ORIGIN='https://example.com').status_code,403)
 def test_export(self):
  self.lesson();r=self.client.get('/api/export/');self.assertEqual(r.status_code,200);self.assertIn('zaplacono',r.content.decode('utf-8'))

class DatasetIsolationTests(TestCase):
 databases={'default','demo'}
 def setUp(self):
  self.real=Student.objects.using('default').create(name='Prawdziwy uczeń',hourly_rate=100)
 def demo_get(self,path='/api/state/'):
  return self.client.get(path,HTTP_X_LEKCJE_MODE='demo')
 def test_seed_and_reset_never_touch_real_data(self):
  from .demo import seed_demo
  data=seed_demo();self.assertEqual(data,{'ok':True,'students':8,'lessons':64,'payments':18})
  state=self.demo_get().json();self.assertEqual(state['dataset'],'demo');self.assertEqual(len(state['students']),8)
  self.assertNotIn('Prawdziwy uczeń',[s['name'] for s in state['students']])
  self.assertTrue(any(Decimal(s['credit'])>0 for s in state['students']))
  self.assertTrue(any(Decimal(s['due'])>0 for s in state['students']))
  r=self.client.post('/api/demo-reset/',data='{}',content_type='application/json',HTTP_X_LEKCJE_MODE='demo');self.assertEqual(r.status_code,200)
  self.assertEqual(Student.objects.using('default').get().name,'Prawdziwy uczeń')
  self.assertEqual(Lesson.objects.using('default').count(),0)
  self.assertEqual(Student.objects.using('demo').count(),8)
 def test_default_mode_reset_denied_and_no_context_leak(self):
  from .demo import seed_demo
  seed_demo();self.demo_get()
  r=self.client.get('/api/state/');self.assertEqual(r.json()['dataset'],'default');self.assertEqual(len(r.json()['students']),1)
  self.assertEqual(self.client.post('/api/demo-reset/',data='{}',content_type='application/json').status_code,403)
  self.assertEqual(self.client.get('/api/state/',HTTP_X_LEKCJE_MODE='other').status_code,400)
 def test_demo_form_write_delete_and_export_isolated(self):
  r=self.client.post('/api/students/',data=json.dumps({'name':'Nowy testowy','hourly_rate':120,'extra':0}),content_type='application/json',HTTP_X_LEKCJE_MODE='demo')
  self.assertEqual(r.status_code,200,r.content)
  self.assertEqual(Student.objects.using('default').count(),1)
  self.assertEqual(Student.objects.using('demo').get().name,'Nowy testowy')
  r=self.demo_get('/api/export/');self.assertNotIn('Prawdziwy uczeń',r.content.decode())
  r=self.client.delete('/api/students/'+str(Student.objects.using('demo').get().id)+'/',HTTP_X_LEKCJE_MODE='demo');self.assertEqual(r.status_code,200)
  self.assertEqual(Student.objects.using('default').count(),1)
 def test_demo_sql_uses_only_demo_credentials(self):
  from unittest.mock import patch,MagicMock
  from django.test import override_settings
  from django.conf import settings
  config={k:dict(v) for k,v in settings.DATABASES.items()};config['demo'].update({'USER':'demo_app','PASSWORD':'demo_pass','HOST':'127.0.0.1','PORT':'5432'})
  with override_settings(DATABASES=config),patch.dict('os.environ',{'DEMO_SQL_READ_USER':'demo_reader','DEMO_SQL_READ_PASSWORD':'demo_secret'}),patch('psycopg.connect') as connect:
   q=MagicMock();q.description=[];q.rowcount=0;q.statusmessage='SELECT 0'
   connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value=q
   r=self.client.post('/api/sql/',data=json.dumps({'query':'SELECT 1','write':False}),content_type='application/json',HTTP_X_LEKCJE_MODE='demo')
   self.assertEqual(r.status_code,200,r.content)
   self.assertEqual(connect.call_args.kwargs['dbname'],config['demo']['NAME'])
   self.assertEqual(connect.call_args.kwargs['user'],'demo_reader')
