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


class TestEventActionViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hodor', password='hodor',
                                             first_name='Hodor', last_name='HodorHodor',
                                             email='hodor@hodor.hodor')
        Perms.objects.create(user=self.user, access_level=1).save()
        self.event = factories.EventFactory()
        self.eventaction = factories.EventActionFactory()
        self.add_url = '/eventactions/add/%s' % self.event.id
        self.edit_url = '/eventactions/edit/%s' % self.eventaction.id

    def test_add_eventaction_without_login(self):
        """
        Add eventaction without login
        """
        response = self.client.get(self.add_url)
        self.assertRedirects(response, '/login/?next=%s' % self.add_url)

    def test_add_eventaction_with_wrong_perms(self):
        """
        Add eventaction with invalid prems
        """
        self.client.login(username='hodor', password='hodor')
        Perms.objects.filter(user=self.user).update(access_level=4)
        response = self.client.post(self.add_url, {}, follow=True)
        self.assertTemplateUsed(response, 'unauthorized.html')

    # TODO: Fix the assertRedirects error 200 != 302
    # def test_add_eventaction(self):
    #     """
    #     Add event actions
    #     """
    #     self.client.login(username='hodor', password='hodor')
    #     data = {'event': self.event.id,
    #             'plugin': 1,
    #             'isEnabled': 1,
    #             'threshold_count': 1,
    #             'threshold_timer': 60,
    #             'pluginParameters': 'HODOR_RULES'}
    #     response = self.client.post(self.add_url, data, follow=True)
    #     self.assertRedirects(response, '/events/view/%s' % self.event.id)
    #     response = self.client.get('/events/view/%s' % self.event.id)
    #     self.assertContains(response, 'HODOR_RULES')

    def test_edit_eventaction_without_login(self):
        """
        Edit eventaction without login
        """
        response = self.client.get(self.edit_url)
        self.assertRedirects(response, '/login/?next=%s' % self.edit_url)

    def test_edit_eventaction_with_wrong_perms(self):
        """
        Add eventaction with invalid prems
        """
        self.client.login(username='hodor', password='hodor')
        Perms.objects.filter(user=self.user).update(access_level=4)
        response = self.client.post(self.edit_url, {}, follow=True)
        self.assertTemplateUsed(response, 'unauthorized.html')

    def test_edit_eventaction(self):
        """
        Edit eventaction
        """
        self.client.login(username='hodor', password='hodor')
        data = {'event': self.event.id,
                'plugin': self.eventaction.plugin.id,
                'isEnabled': 1,
                'threshold_count': 1,
                'threshold_timer': 60,
                'pluginParameters': 'HODOR_RULES'}
        response = self.client.get(self.edit_url)
        self.assertContains(response, '__EVENTID__')
        postresponse = self.client.post(self.edit_url, data)
        self.assertRedirects(postresponse, '/events/view/%s' % self.eventaction.event.id)
        response = self.client.get(self.edit_url)
        self.assertContains(response, 'HODOR_RULES')
