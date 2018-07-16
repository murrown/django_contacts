import json

from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.db import models


class Contact(models.Model):
    """
    The Contact model. Stores the information for a single contact.
    """
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


    READ_ONLY_FIELDS = {'pk', 'created', 'created_by',
                        'modified', 'modified_by'}
    WRITABLE_FIELDS = {'name', 'phone_number', 'address', 'email'}


    @property
    def data_dict(self):
        """
        @return: A data dictionary containing all of this contact's
            information, suitable for a JSON response to an API request.
        """
        data = json.loads(serialize('json', [self]))[0]['fields']
        data['pk'] = self.pk
        return data
