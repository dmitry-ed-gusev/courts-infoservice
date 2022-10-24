from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [

    # path('', index, name='main'),
    path('', views.StatsListView.as_view(), name='main'),  # processing <web-site-address>/stats/ url

]
