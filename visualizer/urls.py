from django.urls import path
from . import views

app_name = 'visualizer'
urlpatterns = [
    path('', views.index, name='index'),
    path('init/', views.init, name='init'),
    path('section/', views.select_section, name='section'),
    path('prev/', views.prev_paragraph, name='prev'),
    path('next/', views.next_paragraph, name='next'),
]