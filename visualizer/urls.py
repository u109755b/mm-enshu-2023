from django.urls import path
from . import views

app_name = 'visualizer'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:gutenbergID>', views.index, name='index'),
    path('<int:gutenbergID>/init/', views.init, name='init'),
    path('<int:gutenbergID>/section/', views.select_chapter, name='section'),
    path('<int:gutenbergID>/prev/', views.prev_chapter, name='prev'),
    path('<int:gutenbergID>/next/', views.next_chapter, name='next'),
    path('<int:gutenbergID>/sample/', views.select_sample, name='sample'),
]