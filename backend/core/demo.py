from datetime import timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .database import demo_available,active_database
from .models import Student,Lesson,Payment
from .services import money

def seed_demo(reset=False):
 if not demo_available(): raise ValueError('Baza demo nie jest skonfigurowana lub wskazuje bazę rzeczywistą.')
 token=active_database.set('demo')
 try:
  with transaction.atomic(using='demo'):
   if Student.objects.exists() and not reset: raise ValueError('Baza testowa zawiera dane. Użyj resetowania w aplikacji.')
   if reset:
    Payment.objects.all().delete();Lesson.objects.all().delete();Student.objects.all().delete()
   today=timezone.localtime().replace(hour=16,minute=0,second=0,microsecond=0)
   names=['Anna Przykładowa','Bartosz Testowy','Celina Fikcyjna','Daniel Demonstracyjny','Ewa Próbna','Filip Symulowany','Gabriela Szkoleniowa','Hubert Ćwiczeniowy']
   scenarios=['pełne rozliczenie','wpłaty częściowe','brak wpłat','nadpłata','jedna wpłata za kilka lekcji','ręczny przydział','ceny wpisane ręcznie','różne metody płatności']
   for i,name in enumerate(names):
    s=Student.objects.create(name=name,hourly_rate=80+i*10,extra=20 if i%3==0 else 0,notes='DANE FIKCYJNE · '+scenarios[i])
    ls=[]
    for j in range(8):
     minutes=[45,60,90,120][(i+j)%4];when=today-timedelta(days=(7-j)*7+i)
     manual=i==6 and j%2==0
     price=Decimal('99.00') if manual else money(s.hourly_rate*Decimal(minutes)/60+s.extra)
     ls.append(Lesson.objects.create(student=s,date=when,minutes=minutes,hourly_rate=s.hourly_rate,extra=s.extra,price=price,manual_price=manual,notes='Przykład · '+['ułamki','równania','geometria','powtórka'][j%4]))
    total=sum((l.price for l in ls),Decimal(0))
    def pay(amount,method='BLIK',ids=None,offset=0):
     Payment.objects.create(student=s,date=(today-timedelta(days=offset)).date(),amount=amount,method=method,lesson_ids=ids or [],notes='Fikcyjna wpłata demonstracyjna')
    if i==0:
     for l in ls: pay(l.price,'przelew',offset=(today-l.date).days)
    elif i==1: pay(money(total*Decimal('.35')),'BLIK')
    elif i==2: pass
    elif i==3: pay(total+Decimal('150'),'gotówka')
    elif i==4: pay(sum((l.price for l in ls[:4]),Decimal(0)),'przelew',offset=7)
    elif i==5: pay(ls[-1].price+Decimal('20'),'BLIK',[ls[-1].id])
    elif i==6: pay(money(total/2),'gotówka')
    else:
     for j,l in enumerate(ls[:5]): pay(l.price,['BLIK','przelew','gotówka'][j%3],offset=5-j)
   return {'ok':True,'students':Student.objects.count(),'lessons':Lesson.objects.count(),'payments':Payment.objects.count()}
 finally: active_database.reset(token)
