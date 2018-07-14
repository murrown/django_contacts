from django.db import models
from django.core.serializers import serialize
import json

class Contact(models.Model):
    name = models.TextField(null=False)
    phone_number = models.IntegerField(null=True)
    address = models.TextField(null=True)
    email = models.CharField(max_length=254, null=True)

    @property
    def json(self):
        data = json.loads(serialize('json', [self]))[0]['fields']
        data['pk'] = self.pk
        return data
