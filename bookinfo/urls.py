from django.urls import path
from . import views

app_name = 'bookinfo'
urlpatterns = [
    path('', views.index, name='index'),
]