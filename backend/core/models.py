from django.db import models
from django.db.models import Q
class Student(models.Model):
 name=models.CharField(max_length=120)
 hourly_rate=models.DecimalField(max_digits=10,decimal_places=2)
 extra=models.DecimalField(max_digits=10,decimal_places=2,default=0)
 notes=models.TextField(blank=True)
 class Meta:
  db_table='uczniowie'
  constraints=[models.CheckConstraint(condition=Q(hourly_rate__gte=0)&Q(extra__gte=0),name='student_nonnegative')]
class Lesson(models.Model):
 student=models.ForeignKey(Student,on_delete=models.PROTECT)
 date=models.DateTimeField()
 minutes=models.PositiveIntegerField(default=60)
 hourly_rate=models.DecimalField(max_digits=10,decimal_places=2)
 extra=models.DecimalField(max_digits=10,decimal_places=2,default=0)
 price=models.DecimalField(max_digits=10,decimal_places=2)
 manual_price=models.BooleanField(default=False)
 notes=models.TextField(blank=True)
 class Meta:
  db_table='lekcje'
  ordering=['date','id']
  constraints=[models.CheckConstraint(condition=Q(minutes__gt=0)&Q(price__gte=0)&Q(hourly_rate__gte=0)&Q(extra__gte=0),name='lesson_valid_amounts')]
class Payment(models.Model):
 student=models.ForeignKey(Student,on_delete=models.PROTECT)
 date=models.DateField()
 amount=models.DecimalField(max_digits=10,decimal_places=2)
 method=models.CharField(max_length=10,choices=[('BLIK','BLIK'),('przelew','przelew'),('gotówka','gotówka')])
 # Empty list means oldest-first; explicit order is preserved and can be edited.
 lesson_ids=models.JSONField(default=list,blank=True)
 notes=models.TextField(blank=True)
 class Meta:
  db_table='wplaty'
  ordering=['date','id']
  constraints=[models.CheckConstraint(condition=Q(amount__gt=0),name='payment_positive'),models.CheckConstraint(condition=Q(method__in=['BLIK','przelew','gotówka']),name='payment_method')]
