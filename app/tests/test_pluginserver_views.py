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
from mock import patch, call
from cito_engine.models import PluginServer
from . import factories


class TestIncidentViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hodor', password='hodor',
                                             first_name='Hodor', last_name='HodorHodor',
                                             email='hodor@hodor.hodor')
        Perms.objects.create(user=self.user, access_level=1).save()

    def login(self):
        self.client.login(username='hodor', password='hodor')

    def test_incident_views_without_login(self):
        """All pluginserver views without login
        """
        p1 = factories.PluginServerFactory.create()
        response = self.client.get('/pluginservers/')
        self.assertRedirects(response, '/login/?next=/pluginservers/')
        for page in ['view', 'edit', 'refresh']:
            response = self.client.get('/pluginservers/%s/%s/' % (page, p1.id))
            self.assertRedirects(response, '/login/?next=/pluginservers/%s/%s/' % (page, p1.id))

    def test_view_all_pluginservers(self):
        """Test that view_all_pluginservers
        """
        self.login()
        pluginserver_names = ['Alpha', 'Omega', 'Zoidberg']
        [factories.PluginServerFactory.create(name=name) for name in pluginserver_names]
        response = self.client.get('/pluginservers/')
        [self.assertContains(response, name) for name in pluginserver_names]

    def test_search_in_view_all_pluginservers(self):
        """Testing search for plugin in pluginservers
        """
        p1 = factories.PluginServerFactory.create(name='ServerAlpha')
        p2 = factories.PluginServerFactory.create(name='ServerBeta')
        plugin1 = factories.PluginFactory.create(name='PluginHermes', server=p1)
        plugin2 = factories.PluginFactory.create(name='PluginFarnsworth', server=p2)

        self.login()
        response = self.client.post('/pluginservers/', data={'search_term': 'PluginHermes'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'ServerAlpha')
        self.assertContains(response, 'PluginHermes')
        self.assertNotContains(response, 'ServerBeta')
        self.assertNotContains(response, 'PluginFarnsworth')

    def test_view_single_pluginserver(self):
        """Testing view_single_pluginserver
        """
        p1 = factories.PluginServerFactory.create(name='ServerAlpha')
        plugin1 = factories.PluginFactory.create(name='PluginHermes', server=p1)
        plugin2 = factories.PluginFactory.create(name='PluginFarnsworth', server=p1)
        self.login()
        response = self.client.get('/pluginservers/view/9999')
        self.assertEquals(response.status_code, 404)
        response = self.client.get('/pluginservers/view/%d/' % p1.id)
        self.assertContains(response, 'ServerAlpha')
        self.assertContains(response, 'PluginHermes')
        self.assertContains(response, 'PluginFarnsworth')

    def test_add_pluginserver(self):
        """Testing add_pluginserver
        """
        data = dict(name='MotherShip',
                    url='SomeURL',
                    status=True,
                    ssl_verify=True)

        self.login()
        response = self.client.post('/pluginservers/add/', data=data, follow=True)
        self.assertRedirects(response, '/pluginservers/')
        response = self.client.get('/pluginservers/')
        self.assertContains(response, 'MotherShip')
        self.assertContains(response, 'SomeURL')
        p1 = PluginServer.objects.get(name='MotherShip')
        self.assertIsNotNone(p1)
        self.assertEquals(p1.name, 'MotherShip')
        self.assertEquals(p1.url, 'SomeURL')
        self.assertEquals(p1.status, True)
        self.assertEquals(p1.ssl_verify, True)

    def test_edit_pluginserver(self):
        """Testing edit_pluginserver
        """
        data = dict(name='MotherShip',
                    url='SomeURL',
                    status=True,
                    ssl_verify=True)

        self.login()
        response = self.client.post('/pluginservers/add/', data=data, follow=True)
        p1 = PluginServer.objects.get(name='MotherShip')
        self.assertIsNotNone(p1)
        modified_data = dict(name='BrotherShip',
                             url='AnotherURL',
                             status=False,
                             ssl_verify=False)
        response = self.client.post('/pluginservers/edit/%d/' % p1.id, data=modified_data, follow=True)
        self.assertRedirects(response, '/pluginservers/view/%d/' % p1.id)
        p1 = PluginServer.objects.get(pk=p1.id)
        self.assertEquals(p1.name, 'BrotherShip')
        self.assertEquals(p1.url, 'AnotherURL')
        self.assertEquals(p1.status, False)
        self.assertEquals(p1.ssl_verify, False)

    @patch('cito_engine.poller.pluginpoller.requests')
    def test_refresh_pluginserver_view(self, mock_requests):
        """Tests refresh pluginserver view
        """
        p1 = factories.PluginServerFactory.create(name='MotherShip', url='http://foo.bar/')
        self.login()
        mock_requests.get.return_value.status_code = 200
        response = self.client.get('/pluginservers/refresh/%d/' % p1.id)
        self.assertRedirects(response, '/pluginservers/view/%d/' % p1.id)
        self.assertEqual(
            mock_requests.get.call_args_list,
            [call('%s/getallplugins' % p1.url, verify=p1.ssl_verify)]
        )
