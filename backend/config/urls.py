from django.urls import path,re_path
from core.views import api,frontend
urlpatterns=[path('api/<str:resource>/',api),path('api/<str:resource>/<int:pk>/',api),re_path(r'^(?P<path>.*)$',frontend)]
