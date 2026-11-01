from django.core.management.base import BaseCommand,CommandError
from core.demo import seed_demo
class Command(BaseCommand):
 help='Wypełnia wyłącznie osobną bazę demonstracyjną fikcyjnymi danymi.'
 def add_arguments(self,parser): parser.add_argument('--reset',action='store_true')
 def handle(self,*args,**options):
  try: result=seed_demo(reset=options['reset'])
  except Exception as e: raise CommandError(str(e))
  self.stdout.write(self.style.SUCCESS(str(result)))
