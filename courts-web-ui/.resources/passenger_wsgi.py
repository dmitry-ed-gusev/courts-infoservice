# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, '/var/www/u1747464/data/www/courts.itech-lab.ru/courtsinfo')
sys.path.insert(1, '/var/www/u1747464/data/.venv-courts/lib/python3.10/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'courtsinfo.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

