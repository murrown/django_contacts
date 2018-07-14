from django.db import models

class Contact(models.Model):
    name = models.TextField(null=False)
    phone_number = models.IntegerField(null=True)
    address = models.TextField(null=True)
    email = models.CharField(max_length=254, null=True)
