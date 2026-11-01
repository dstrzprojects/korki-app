from decimal import Decimal, ROUND_HALF_UP
from .models import Student,Lesson,Payment
ZERO=Decimal('0.00')
def money(value):
 try: d=Decimal(str(value)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
 except Exception: raise ValueError('Nieprawidłowa kwota.')
 if not d.is_finite() or d<0 or d>Decimal('99999999.99'): raise ValueError('Kwota poza zakresem.')
 return d
def ledger():
 students=list(Student.objects.order_by('name','id')); lessons=list(Lesson.objects.all()); payments=list(Payment.objects.all())
 paid={x.id:ZERO for x in lessons}; credit={s.id:ZERO for s in students}; allocations=[]
 for p in payments:
  remaining=p.amount
  targets=[x for x in lessons if x.student_id==p.student_id]
  if p.lesson_ids: targets=sorted([x for x in targets if x.id in p.lesson_ids],key=lambda x:p.lesson_ids.index(x.id))
  for x in targets:
   part=min(remaining,x.price-paid[x.id])
   if part>0:
    paid[x.id]+=part; remaining-=part
    allocations.append({'payment_id':p.id,'lesson_id':x.id,'amount':str(part),'method':p.method})
  credit[p.student_id]+=remaining
 names={s.id:s.name for s in students}
 ls=[{'id':x.id,'student_id':x.student_id,'student':names[x.student_id],'date':x.date.isoformat(),'minutes':x.minutes,'hourly_rate':str(x.hourly_rate),'extra':str(x.extra),'price':str(x.price),'manual_price':x.manual_price,'notes':x.notes,'paid':str(paid[x.id]),'due':str(x.price-paid[x.id]),'methods':sorted(set(a['method'] for a in allocations if a['lesson_id']==x.id))} for x in lessons]
 ss=[]
 for s in students:
  due=sum((x.price-paid[x.id] for x in lessons if x.student_id==s.id),ZERO)
  ss.append({'id':s.id,'name':s.name,'hourly_rate':str(s.hourly_rate),'extra':str(s.extra),'notes':s.notes,'due':str(due),'credit':str(credit[s.id]),'balance':str(due-credit[s.id])})
 ps=[{'id':p.id,'student_id':p.student_id,'student':names[p.student_id],'date':p.date.isoformat(),'amount':str(p.amount),'method':p.method,'lesson_ids':p.lesson_ids,'notes':p.notes} for p in payments]
 return {'students':ss,'lessons':ls,'payments':ps,'allocations':allocations}
