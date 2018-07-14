from django.db import models
from django.core.serializers import serialize
from django.contrib.auth.models import User
import json

class Contact(models.Model):
    name = models.TextField(default=None)
    phone_number = models.CharField(max_length=15, default='')
    address = models.TextField(default='')
    email = models.CharField(max_length=254, default='')
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL,
                                   related_name='contact_created_by')
    modified_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL,
                                    related_name='contact_modified_by')

    @property
    def data_dict(self):
        data = json.loads(serialize('json', [self]))[0]['fields']
        data['pk'] = self.pk
        return data
