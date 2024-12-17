# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('translation/', views.translation_assistant, name='translation_assistant'),
    path('med/', views.med, name='med'),
    path('about/', views.about, name='about'),
    path('Communite/', views.communite, name='communite'),
    path('imgr/', views.imgr, name='imgr'),
    path('api/translate/', views.translate_text, name='translate_text'),

   
 ]


