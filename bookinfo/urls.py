from django.urls import path
from . import views

app_name = 'bookinfo'
urlpatterns = [
    path('<int:gutenbergID>', views.index, name='index'),
]