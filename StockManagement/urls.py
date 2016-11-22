"""
Definition of urls for StockManagement.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

import app.forms
from app.views import *


urlpatterns = [
    url(r'login', login, name='login'),
    url(r'logout', logout, name='logout'),
    url(r'buy', buy, name='buy'),
    url(r'index', index, name='index'),
]
