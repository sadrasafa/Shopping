# Create your tests here.

import unittest
from django.test import Client
from shopping.models import ShoppingUser, User

class SigninTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        user1 = User.objects.create_user(username='ahbar', password='1')
        user1.is_active = True
        user2 = User.objects.create_user(username='asgar', password='1')
        user2.is_active = True

        user1.save()
        user2.save()

        print(user1.password)
        ShoppingUser.objects.create(user=user1, first_name='ahbar', last_name='ahbari', email='aarash95@gmail.com')
        ShoppingUser.objects.create(user=user2, first_name='asgar', last_name='asgari', email='aarash95@gmail.com')

    # @classmethod
    # def setUpTestData(cls):
    #     pass
    #     # user = User.objects.create()

    def test_signin(self):
        user = User.objects.get(username='ahbar')
        print(user.username)
        response = self.client.post('/shopping/signin', {'username': 'ahbar', 'password': 'cc'})
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/shopping/signin', {'username': 'ahbar', 'password': '1'})
        self.assertEqual(response.status_code, 302)

        #send message to asgar
        asgar_id = ShoppingUser.objects.filter(first_name='asgar')[0].id
        response = self.client.post('/shopping/send_message/' + str(asgar_id), {'text': 'Can you hear me?'})
        self.assertEqual(response.status_code, 302)

        #ahbar signout
        response = self.client.post('/shopping/signout')
        self.assertEqual(response.status_code, 302)

        #asgar signin
        response = self.client.post('/shopping/signin', {'username': 'asgar', 'password': '1'})
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/shopping/messages')
        ahbar = ShoppingUser.objects.filter(first_name='ahbar')[0]
        asgar = ShoppingUser.objects.filter(first_name='asgar')[0]
        self.assertEqual(response.context['received'].all()[0].text, 'Can you hear me?')
        self.assertEqual(response.context['received'].all()[0].sender, ahbar)
        self.assertEqual(response.context['received'].all()[0].receiver, asgar)

        # print(b'Can you hear me?' in response.content)

        # self.assertEqual(response.status_code, 403)


    # def test_correct_login(self):
    #     response = self.client.post('/shopping/signin', {'username': 'aa', 'password': 'bb'})
    #     self.assertEqual(response.status_code, 200)
