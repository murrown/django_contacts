from django.urls import re_path
from contacts.views import call_api, call_api_pk

urlpatterns = [
    re_path(r'^api/(?P<pk>\d+)/?$', call_api_pk),
    re_path(r'^api/?$', call_api),
]
