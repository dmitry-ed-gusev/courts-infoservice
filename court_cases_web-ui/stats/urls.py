from django.urls import path
from .views import index

app_name = 'stats'

urlpatterns = [
    path('', index, name='main'),
]
