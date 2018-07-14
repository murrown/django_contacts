from django.test import TestCase
from contacts.models import Contact
import json
from base64 import b64encode

class TestAPI(TestCase):
    fixtures = ['test_fixture.json']

    def test_create_new_contact(self):
        num_contacts = Contact.objects.count()
        data = json.dumps({'name': 'Ashton'})
        auth = b'Basic ' + b64encode(b'test_user:test_password')
        auth_headers = {'HTTP_AUTHORIZATION': auth.decode()}
        response = self.client.generic('POST', '/api/', data, **auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), num_contacts+1)

    def test_create_new_contact_unauthenticated(self):
        num_contacts = Contact.objects.count()
        data = json.dumps({'name': 'Duncan'})
        response = self.client.generic('POST', '/api/', data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Contact.objects.count(), num_contacts)

    def test_get_contact(self):
        pk = 1
        c = Contact.objects.get(pk=pk)
        response = self.client.generic('GET', '/api/%s' % pk)
        self.assertEqual(response.status_code, 200)
        for key, value in json.loads(response.content).items():
            self.assertEqual(getattr(c, key), value)

    def test_replace_contact_data(self):
        pk = 5
        data = json.dumps({'name': 'Jessie'})
        auth = b'Basic ' + b64encode(b'test_user:test_password')
        auth_headers = {'HTTP_AUTHORIZATION': auth.decode()}
        response = self.client.generic('PATCH', '/api/%s' % pk, data,
                                       **auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.get(pk=pk).name, 'Jessie')

    def test_replace_contact_data_unauthenticated(self):
        pk = 1
        data = json.dumps({'name': 'Evette'})
        response = self.client.generic('PATCH', '/api/%s' % pk, data)
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(Contact.objects.get(pk=pk).name, 'Evette')

    def test_get_contact_list(self):
        response = self.client.generic('GET', '/api/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)),
                         Contact.objects.count())
        data = json.dumps({'address': 'Lambsbridge'})
        response = self.client.generic('GET', '/api/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), 2)

    def test_delete_contact(self):
        pk = 1
        num_contacts = Contact.objects.count()
        auth = b'Basic ' + b64encode(b'test_user:test_password')
        auth_headers = {'HTTP_AUTHORIZATION': auth.decode()}
        response = self.client.generic('DELETE', '/api/%s' % pk,
                                       **auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), num_contacts-1)

    def test_delete_contact_unauthenticated(self):
        pk = 1
        num_contacts = Contact.objects.count()
        response = self.client.generic('DELETE', '/api/%s' % pk)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Contact.objects.count(), num_contacts)
