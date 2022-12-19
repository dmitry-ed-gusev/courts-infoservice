from django.urls import path

from . import views

app_name = "courts"

urlpatterns = [
    # path('', index, name='main'),  # 'courts:main'
    path(
        "", views.CourtsListView.as_view(), name="main"
    ),  # processing <web-site-address>/courts/ url
]
