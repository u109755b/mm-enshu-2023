from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('init/', views.init, name='init'),
    path('prev/', views.prev_paragraph, name='prev'),
    path('next/', views.next_paragraph, name='next'),
]