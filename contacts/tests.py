from django.test import TestCase
from contacts.models import Contact

class TestAPI(TestCase):
    def setUp(self):
        pass

    def test_create_new_contact(self):
        raise NotImplementedError

    def test_create_new_contact_unauthenticated(self):
        raise NotImplementedError

    def test_get_contact(self):
        raise NotImplementedError

    def test_replace_contact_data(self):
        raise NotImplementedError

    def test_replace_contact_data_unauthenticated(self):
        raise NotImplementedError

    def test_get_contact_list(self):
        raise NotImplementedError

    def test_delete_contact(self):
        raise NotImplementedError

    def test_delete_contact_unauthenticated(self):
        raise NotImplementedError
