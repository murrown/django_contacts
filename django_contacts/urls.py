from django.urls import re_path
from contacts.views import call_api, call_api_pk

urlpatterns = [
    re_path('^api/(?P<pk>\d+)/?$', call_api_pk),
    re_path('^api/?$', call_api),
]
