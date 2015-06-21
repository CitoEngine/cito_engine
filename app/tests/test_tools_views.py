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


class TestBulkUploadEventsViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hodor', password='hodor',
                                             first_name='Hodor', last_name='HodorHodor',
                                             email='hodor@hodor.hodor')
        Perms.objects.create(user=self.user, access_level=1).save()

    def login(self):
        self.client.login(username='hodor', password='hodor')

    def test_tools_views_without_login(self):
        """All user views without login"""
        for view in ['/bulkupload/events/']:
            response = self.client.get('/tools%s' % view)
            self.assertRedirects(response, '/login/?next=/tools%s' % view, msg_prefix='Error for view:%s' % view)

    def test_show_bulk_upload_form(self):
        """Test if we can show"""
        team1 = factories.TeamFactory.create(name='SupaTeam')
        category1 = factories.CategoryFactory(categoryType='SupaCategory')
        self.login()
        data = dict(listofitems='foo',
                    team=team1,
                    category=category1,
                    severity='S2',
                    )
        response = self.client.post('/tools/bulkupload/events/', data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/tools/bulkupload/events/confirm/')

    # TODO: extensive testing of bulk_upload_events view
    # def test_bulk_upload_events(self):
    #     """Tests if we can add events in bulk"""
    #     self.login()
    #     list_of_items = 'BulkEvent1, BulkEvent2, BulkEvent3'