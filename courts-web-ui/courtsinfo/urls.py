"""courtsinfo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import os
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

# Up two folders to serve "site" content
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.join(BASE_DIR, 'site')

# Usual url patterns - routing
urlpatterns = [

    path('', include('home.urls')),  # [Home/Main Page] for the site

    path("admin/", admin.site.urls),  # django admin site

    # django embedded login/logout capability, see more:
    # https://docs.djangoproject.com/en/3.2/topics/auth/default/#module-django.contrib.auth.views
    path('accounts/', include('django.contrib.auth.urls')),  # django usual login/logout urls

    # processing the static content
    re_path(r'^site/(?P<path>.*)$', serve,
            {'document_root': SITE_ROOT, 'show_indexes': True},
            name='site_path'),  # serve static content by address /site

    re_path(r'^oauth/', include('social_django.urls', namespace='social')),

    # site applications
    path('courts/', include('courts.urls')),  # [Courts Page] for site
    path('stats/', include('stats.urls')),  # [Statistics Page] for site

]

# Serve the favicon for the site
urlpatterns += [
    path('favicon.ico', serve, {
            'path': 'favicon.ico',
            'document_root': os.path.join(BASE_DIR, 'home/static'),
        }
    ),
]

# # Switch to social login if it is configured - Keep for later
# try:
#     from . import github_settings
#     social_login = 'registration/login_social.html'
#     urlpatterns.insert(0, path('accounts/login/',
#                        auth_views.LoginView.as_view(template_name=social_login)))
#     print('Using', social_login, 'as the login template')
# except:
#     print('Using registration/login.html as the login template')
