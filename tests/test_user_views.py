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

from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django import forms
from appauth.models import Perms
from cito_engine.models import Team
from . import factories


class TestUserViews(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hodor', password='hodor',
                                             first_name='Hodor', last_name='HodorHodor',
                                             email='hodor@hodor.hodor')
        Perms.objects.create(user=self.user, access_level=1).save()

    def login(self):
        self.client.login(username='hodor', password='hodor')

    def test_user_views_without_login(self):
        """All user views without login"""
        for view in ['/', '/create/', '/toggle/', '/team/add/', '/view/1/', '/edit/1/', '/perms/update/']:
            response = self.client.get('/users%s' % view)
            self.assertRedirects(response, '/login/?next=/users%s' % view, msg_prefix='Error for view:%s' % view)

    def test_view_all_users(self):
        """View all users"""
        self.login()
        response = self.client.get('/users/')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Hodor HodorHodor')

    def test_modify_user_team_membership(self):
        """Testing user team modification view"""
        t1 = factories.TeamFactory.create(name='Alpha')
        t2 = factories.TeamFactory.create(name='Beta')
        self.login()
        # Fail on GET
        response = self.client.get('/users/team/add/')
        self.assertEquals(response.status_code, 400)
        response = self.client.get('/users/team/remove/')
        self.assertEquals(response.status_code, 400)

        # Try adding
        response = self.client.post('/users/team/add/', data={'user_id': self.user.id, 'team_id': t1.id}, follow=True)
        self.assertRedirects(response, '/users/view/%d/' % self.user.id)
        self.assertEquals(self.user.team_set.get(id=t1.id), t1)
        self.assertNotIn(t2, self.user.team_set.filter(id=t2.id))

        # Try removing
        response = self.client.post('/users/team/remove/', data={'user_id': self.user.id, 'team_id': t1.id}, follow=True)
        self.assertRedirects(response, '/users/view/%d/' % self.user.id)
        self.assertNotIn(t1, self.user.team_set.filter(id=t1.id))

    def test_user_edit_view(self):
        """Testing edit user view"""
        self.login()
        data = dict(first_name='Burt',
                    last_name='Reynolds',
                    email='b@b.com',
                    username='burty',
                    password1='pass1',
                    password2='pass1')
        response = self.client.post('/users/edit/%d/' % self.user.id, data=data, follow=True)
        self.assertRedirects(response, '/users/view/%d/' % self.user.id)

    def test_user_toggle(self):
        """Test user_toggle view i.e setting is_active True/False"""
        self.login()
        response = self.client.post('/users/toggle/', data={'user_id': self.user.id})
        self.assertRedirects(response, '/users/view/%d/' % self.user.id)
        u = User.objects.get(pk=self.user.id)
        # Make sure we do not deactivate ourself
        self.assertEqual(u.is_active, True)

        # Try on a new piggy
        # First disable the user
        new_user = User.objects.create_user(username='archer', password='archer')
        response = self.client.post('/users/toggle/', data={'user_id': new_user.id})
        self.assertRedirects(response, '/users/view/%d/' % new_user.id)
        u = User.objects.get(pk=new_user.id)
        self.assertFalse(u.is_active)
        # Now enable the user
        response = self.client.post('/users/toggle/', data={'user_id': new_user.id})
        self.assertRedirects(response, '/users/view/%d/' % new_user.id)
        u = User.objects.get(pk=new_user.id)
        self.assertTrue(u.is_active)


class TestCreateUserByView(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hodor', password='hodor',
                                             first_name='Hodor', last_name='HodorHodor',
                                             email='hodor@hodor.hodor')
        Perms.objects.create(user=self.user, access_level=1).save()
        self.t1 = factories.TeamFactory.create(name='AlphaTeam')
        self.t2 = factories.TeamFactory.create(name='BetaTeam')
        self.t3 = factories.TeamFactory.create(name='ZetaTeam')

    def login(self):
        self.client.login(username='hodor', password='hodor')

    def test_validations_of_create_user_view(self):
        """Test validations for create_user view """
        data = dict(fname='',
                    lname='',
                    username='',
                    password1='',
                    password2='',
                    email='',
                    access_level='',
                    teams=''
                    )

        self.login()
        # Make sure all fields are required
        response = self.client.post('/users/create/', data=data, follow=True)
        self.assertContains(response, 'This field is required.', count=7)

        data = dict(fname='Doctor',
                    lname='Zoidberg',
                    username='drzoid',
                    password1='mojo',
                    password2='jojo',
                    email='mo@jo.com',
                    access_level='3',
                    teams='%s' % self.t2.id
                    )

        # Testing password matching
        response = self.client.post('/users/create/', data=data, follow=True)
        self.assertContains(response, 'The passwords did not match. Please try again.', count=2)

    # TODO Fix this test so it runs successfully even through the main testsuite
    # def test_create_user_view(self):
    #     """Testing create_user"""
    #     # self.login()
    #     client = Client()
    #     client.login(username='hodor', password='hodor')
    #     data = dict(fname='Doctor',
    #                 lname='Zoidberg',
    #                 username='drzoid',
    #                 password1='mojo',
    #                 password2='mojo',
    #                 email='mo@jo.com',
    #                 access_level='3',
    #                 teams='%s' % self.t2.id
    #                 )
    #     print Team.objects.all()
    #     # Test with legit form
    #     response = client.post('/users/create/', data=data, follow=True)
    #     # print response
    #     self.assertRedirects(response, '/users/', msg_prefix="Data is %s" % data)
    #     user = User.objects.get(username='drzoid')
    #     self.assertEquals(user.first_name, 'Doctor')
    #     self.assertEquals(user.last_name, 'Zoidberg')
    #     self.assertEquals(user.email, 'mo@jo.com')
    #     self.assertEquals(user.perms.access_level, 3)
    #     self.assertNotIn(self.t2, self.user.team_set.filter(id=self.t2.id))


class TestViewSingleUser(TransactionTestCase):
    def setUp(self):
        self.client = Client()

    def test_view_single_user(self):
        """View single user"""
        u1 = User.objects.create_user(username='pjfry', password='pjfry',
                                      first_name='Phillip', last_name='J Fry',
                                      email='phil.fry@planetexpress.com')
        client = Client()
        client.login(username='pjfry', password='pjfry')
        response = client.get('/users/view/%d/' % u1.id)
        self.assertEquals(response.status_code, 200, msg='Got response: \n %s' % response)
        self.assertIsNotNone(Perms.objects.get(pk=u1.id))
        self.assertContains(response, 'Phillip')
        self.assertContains(response, 'J Fry')
        self.assertContains(response, 'phil.fry@planetexpress.com')

        #  Lets check for an invalid user_id
        response = client.get('/users/view/9999/')
        self.assertEquals(response.status_code, 404)


class TestUpdateUserPerms(TransactionTestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hodor', password='hodor',
                                             first_name='Hodor', last_name='HodorHodor',
                                             email='hodor@hodor.hodor')
        Perms.objects.create(user=self.user, access_level=1).save()

    def test_update_user_perms(self):
        """Updating user permissions"""
        self.client.login(username='hodor', password='hodor')
        new_user = User.objects.create_user(username='phil', password='pjfry',
                                            first_name='Phillip', last_name='J Fry',
                                            email='phil.fry@planetexpress.com')

        #Test if perms are created for new user
        response = self.client.post('/users/perms/update/', data={'user_id': new_user.id, 'access_level': '5'}, follow=True)
        self.assertRedirects(response, '/users/view/%d/' % new_user.id)
        user = User.objects.get(pk=new_user.id)
        print user.perms, new_user.perms
        self.assertEquals(user.perms.access_level, 5)

        # Test updating once you have perms
        response = self.client.post('/users/perms/update/', data={'user_id': new_user.id, 'access_level': '2'}, follow=True)
        self.assertRedirects(response, '/users/view/%d/' % new_user.id)
        user = User.objects.get(pk=new_user.id)
        self.assertEquals(user.perms.access_level, 2)