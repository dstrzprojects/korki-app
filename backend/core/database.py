from contextvars import ContextVar
from django.conf import settings
active_database=ContextVar('active_database',default='default')
def demo_available():
 return 'demo' in settings.DATABASES and settings.DATABASES['demo']['NAME']!=settings.DATABASES['default']['NAME']
class DatasetRouter:
 def db_for_read(self,model,**hints): return active_database.get()
 def db_for_write(self,model,**hints): return active_database.get()
 def allow_relation(self,obj1,obj2,**hints): return obj1._state.db==obj2._state.db if obj1._state.db and obj2._state.db else True
 def allow_migrate(self,db,app_label,**hints): return True
