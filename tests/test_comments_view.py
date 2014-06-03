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
from . import factories


class TestCommentsView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hodor', password='hodor',
                                             first_name='Hodor', last_name='HodorHodor',
                                             email='hodor@hodor.hodor')

    def test_add_comments_without_login(self):
        """Testing adding comments without login"""
        response = self.client.post('/comments/add/')
        self.assertRedirects(response, '/login/?next=/comments/add/')

    def login(self):
        self.client.login(username='hodor', password='hodor')

    def test_add_comments_without_perms(self):
        """Testing adding comments without login"""
        Perms.objects.create(user=self.user, access_level=5).save()
        self.login()
        response = self.client.post('/comments/add/')
        self.assertTemplateUsed(response, 'unauthorized.html')

    def test_doing_get_to_comments_add_view(self):
        """Doing an HTTP get instead of POST to comments view should silently
        fail to /incidents/
        """
        Perms.objects.create(user=self.user, access_level=4).save()
        self.login()
        response = self.client.get('/comments/add/')
        self.assertRedirects(response, '/incidents/')

    def test_post_a_comment(self):
        """Actual comments post"""
        incident = factories.IncidentFactory()
        Perms.objects.create(user=self.user, access_level=4).save()
        self.login()
        response = self.client.post('/comments/add/', data={'incident': incident.id,
                                                            'user': self.user.id,
                                                            'text': 'Do you remember bo2k?'}, follow=True)
        self.assertRedirects(response, '/incidents/view/%s/' % incident.id)
        self.assertContains(response, 'Do you remember bo2k?')