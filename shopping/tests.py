# Create your tests here.

import unittest
from django.test import Client
from shopping.models import ShoppingUser, User

class SigninTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        user = User.objects.create_user(username='aa', password='1')
        user.is_active = True

        user.save()

        print(user.password)
        ShoppingUser.objects.create(user=user, first_name='aa', last_name='bb', email='aarash95@gmail.com')

    # @classmethod
    # def setUpTestData(cls):
    #     pass
    #     # user = User.objects.create()

    def test_signin(self):
        user = User.objects.get(username='aa')
        print(user.username)
        response = self.client.post('/shopping/signin', {'username': 'aa', 'password': 'cc'})
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/shopping/signin', {'username': 'aa', 'password': '1'})
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/shopping/edit_profile')

    # def test_correct_login(self):
    #     response = self.client.post('/shopping/signin', {'username': 'aa', 'password': 'bb'})
    #     self.assertEqual(response.status_code, 200)
