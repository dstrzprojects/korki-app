from django.http import JsonResponse
class LocalOnly:
 def __init__(self,get_response): self.get_response=get_response
 def __call__(self,request):
  if request.META.get('REMOTE_ADDR') not in ('127.0.0.1','::1',None):
   return JsonResponse({'error':'Dostęp wyłącznie lokalny.'},status=403)
  origin=request.headers.get('Origin')
  if origin and origin not in ('http://127.0.0.1:8765','http://localhost:8765'):
   return JsonResponse({'error':'Niedozwolone źródło żądania.'},status=403)
  from .database import active_database,demo_available
  mode=request.headers.get('X-Lekcje-Mode','real')
  if mode not in ('real','demo'):
   return JsonResponse({'error':'Nieznany zestaw danych.'},status=400)
  if mode=='demo' and not demo_available():
   return JsonResponse({'error':'Najpierw uruchom Przygotuj-demo.cmd, aby utworzyć osobną bazę testową.'},status=503)
  token=active_database.set('demo' if mode=='demo' else 'default')
  try:
   response=self.get_response(request)
   response['X-Lekcje-Mode']=mode
   response['Cache-Control']='no-store'
   return response
  finally: active_database.reset(token)
