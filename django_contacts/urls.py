from django.contrib import admin
from django.urls import path
from django.db import connection

urlpatterns = [
]

if connection.settings_dict['NAME'] == ':memory:':
    from django.core import management
    management.call_command('migrate')
