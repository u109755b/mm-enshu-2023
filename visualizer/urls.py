from django.urls import path
from .views import Visualizer

urlpatterns = [
    path('', Visualizer.as_view(), name='index'),
]