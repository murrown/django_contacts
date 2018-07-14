from django.core.management.base import BaseCommand
from django.core import management
from django.contrib.auth.models import User
from contacts.models import Contact

class Command(BaseCommand):
    help = 'Generates test fixture database in JSON format.'

    def handle(self, *args, **options):
        management.call_command('migrate', verbosity=0)
        User.objects.create_user(username='test_user',
                                 password='test_password')
        data = [
            {'name': 'Sylvester', 'phone_number': '3162020',
             'address': 'Tynewear', 'email': 'smallpoisonman@beattle.edu'},
            {'name': 'Helen', 'address': 'Lambsbridge'},
            {'name': 'Lillian', 'phone_number': '1921311',
             'address': 'Radham Academy'},
            {'name': 'Mary', 'address': 'Lambsbridge',
             'email': 'cuttingmetaldancer@radham.edu'},
            {'name': 'Jamie', 'address': 'Tynewear'},
        ]
        for d in data:
            Contact.objects.create(**d)
        management.call_command('dumpdata')
