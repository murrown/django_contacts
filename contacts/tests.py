import json
from base64 import b64encode
from time import sleep

from django.test import TestCase
from contacts.models import Contact


class TestAPI(TestCase):
    fixtures = ['test_fixture.json']

    def test_create_new_contact(self):
        num_contacts = Contact.objects.count()
        data = json.dumps({'name': 'Ashton'})
        auth = b'Basic ' + b64encode(b'test_user:test_password')
        auth_headers = {'HTTP_AUTHORIZATION': auth.decode()}
        response = self.client.generic('POST', '/api/', data, **auth_headers)
        self.assertEqual(response.status_code, 200)
        response_dict = json.loads(response.content.decode())
        c = Contact.objects.get(pk=response_dict['pk'])
        self.assertEqual(Contact.objects.count(), num_contacts+1)
        self.assertEqual(c.created_by.username, 'test_user')
        self.assertEqual(c.modified_by, None)

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
        response_dict = json.loads(response.content.decode())
        for key, value in c.data_dict.items():
            self.assertEqual(response_dict[key], value)

    def test_replace_contact_data(self):
        pk = 5
        c = Contact.objects.get(pk=pk)
        old_data = c.data_dict
        self.assertGreaterEqual(old_data['modified'], old_data['created'])
        data = json.dumps({'name': 'Jessie'})
        auth = b'Basic ' + b64encode(b'test_user:test_password')
        auth_headers = {'HTTP_AUTHORIZATION': auth.decode()}
        response = self.client.generic('PATCH', '/api/%s' % pk, data,
                                       **auth_headers)
        self.assertEqual(response.status_code, 200)
        c = Contact.objects.get(pk=pk)
        new_data = c.data_dict
        self.assertEqual(Contact.objects.get(pk=pk).name, 'Jessie')
        self.assertEqual(c.modified_by.username, 'test_user')
        self.assertNotEqual(new_data['modified_by'], old_data['modified_by'])
        self.assertGreater(new_data['modified'], new_data['created'])
        self.assertGreater(new_data['modified'], old_data['modified'])

    def test_replace_contact_data_unauthenticated(self):
        pk = 1
        data = json.dumps({'name': 'Evette'})
        response = self.client.generic('PATCH', '/api/%s' % pk, data)
        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(Contact.objects.get(pk=pk).name, 'Evette')

    def test_get_contact_list(self):
        response = self.client.generic('GET', '/api/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content.decode())),
                         Contact.objects.count())
        data = json.dumps({'address': 'Lambsbridge'})
        response = self.client.generic('GET', '/api/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content.decode())), 2)

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

    def test_read_only_fields(self):
        auth = b'Basic ' + b64encode(b'test_user:test_password')
        auth_headers = {'HTTP_AUTHORIZATION': auth.decode()}
        pk = 1
        c = Contact.objects.get(pk=pk)
        data_dict = c.data_dict
        for (key, value) in data_dict.items():
            c = Contact.objects.get(pk=pk)
            old_modified = c.modified
            data = json.dumps({key: value})
            response = self.client.generic('PATCH', '/api/%s' % pk, data,
                                           **auth_headers)
            c = Contact.objects.get(pk=pk)
            if key in Contact.READ_ONLY_FIELDS:
                self.assertEqual(response.status_code, 400)
                self.assertEqual(c.modified, old_modified)
            else:
                self.assertIn(key, Contact.WRITABLE_FIELDS)
                self.assertEqual(response.status_code, 200)
                self.assertGreater(c.modified, old_modified)
                sleep(0.1)

            num_contacts = Contact.objects.count()
            if key != 'name':
                data = json.dumps({key: value, 'name': 'Abby'})
            response = self.client.generic('POST', '/api/', data,
                                           **auth_headers)
            if key in Contact.READ_ONLY_FIELDS:
                self.assertEqual(response.status_code, 400)
                self.assertEqual(Contact.objects.count(), num_contacts)
            else:
                self.assertIn(key, Contact.WRITABLE_FIELDS)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(Contact.objects.count(), num_contacts+1)
