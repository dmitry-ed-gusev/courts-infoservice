from django.urls import path
from .views import index

app_name = 'courts'

urlpatterns = [
    path('', index, name='main'),  # 'courts:main'
]
