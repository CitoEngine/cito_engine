"""Copyright 2014 Cyrus Dasadia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from appauth.models import Perms
from appauth.views import *
from . import factories


class TestAppauthViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hodor', password='hodor',
                                             first_name='Hodor', last_name='HodorHodor',
                                             email='hodor@hodor.hodor')

    def test_check_and_create_perms(self):
        """Default perm creation of users"""
        # Test for a superuser
        self.user.is_superuser = True
        self.assertTrue(check_and_create_perms(self.user))
        self.assertEquals(self.user.perms.access_level, 1)

        # Purge perms
        Perms.objects.all().delete()

        # Test for a normal report user (lowest perms)
        self.user.is_superuser = False
        self.assertTrue(check_and_create_perms(self.user))
        self.assertEquals(self.user.perms.access_level, 3)

    def test_login_view(self):
        """Test user login"""
        # Test for a SuperUser user
        self.user.is_superuser = True
        self.user.save()
        response = self.client.post('/login/', data=dict(username='hodor', password='hodor'), follow=True)
        self.assertRedirects(response, '/incidents/')

        # Purge perms
        Perms.objects.all().delete()

        # Test for a normal report user (lowest perms)
        self.user.is_superuser = False
        self.user.save()
        response = self.client.post('/login/', data=dict(username='hodor', password='hodor'), follow=True)
        self.assertRedirects(response, '/incidents/')

    def test_login_with_bad_username_and_password(self):
        """
         Use a bad username or password
        """
        # Wrong user
        response = self.client.post('/login/', data=dict(username='dumbledor', password='hodor'), follow=True)
        self.assertContains(response, 'Username/Password incorrect')

        # Wrong password
        response = self.client.post('/login/', data=dict(username='hodor', password='odor'), follow=True)
        self.assertContains(response, 'Username/Password incorrect')

    def test_inactive_user(self):
        """Login with an inactive user
        """
        self.user.is_active = False
        self.user.save()
        response = self.client.post('/login/', data=dict(username='hodor', password='hodor'), follow=True)
        self.assertContains(response, 'Username/Password incorrect')

    def test_logout(self):
        """Logout user
        """
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('logout.html')

