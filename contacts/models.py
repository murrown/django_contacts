from django.db import models
from django.core.serializers import serialize
import json

class Contact(models.Model):
    name = models.TextField(default=None)
    phone_number = models.CharField(max_length=15, default='')
    address = models.TextField(default='')
    email = models.CharField(max_length=254, default='')

    @property
    def json(self):
        data = json.loads(serialize('json', [self]))[0]['fields']
        data['pk'] = self.pk
        return data
