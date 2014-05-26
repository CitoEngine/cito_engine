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
from cito_engine.models import Category
from . import factories


class TestCategoryViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hodor', password='hodor',
                                             first_name='Hodor', last_name='HodorHodor',
                                             email='hodor@hodor.hodor')
        self.category1 = factories.CategoryFactory(categoryType='TestCategoryType')
        self.category2 = factories.CategoryFactory(categoryType='AnotherTestCategoryType')

    def test_view_category_without_login(self):
        """
        Testing without user
        """
        response = self.client.get('/categories/')
        self.assertRedirects(response, '/login/?next=/categories/')

    def test_view_categories(self):
        """
        Testing with valid perms
        """
        Perms.objects.create(user=self.user, access_level=4).save()
        self.client.login(username='hodor', password='hodor')
        response = self.client.get('/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_categories.html')

    def test_view_all_categories_with_wrong_perms(self):
        """
        View all categories with invalid perms
        """
        self.client.login(username='hodor', password='hodor')
        Perms.objects.create(user=self.user, access_level=5).save()
        response = self.client.get('/categories/', {}, follow=True)
        self.assertTemplateUsed(response, 'unauthorized.html')

    def test_add_category_with_wrong_perms(self):
        """
        Add category with invalid perms
        """
        self.client.login(username='hodor', password='hodor')
        Perms.objects.create(user=self.user, access_level=4).save()
        response = self.client.post('/categories/add', {}, follow=True)
        self.assertTemplateUsed(response, 'unauthorized.html')

    def test_edit_category_with_wrong_perms(self):
        """
        Edit category with invalid perms
        """
        self.client.login(username='hodor', password='hodor')
        Perms.objects.create(user=self.user, access_level=4).save()
        response = self.client.post('/categories/edit/%d' % self.category1.id, {}, follow=True)
        self.assertTemplateUsed(response, 'unauthorized.html')

    def test_add_category_with_perms(self):
        """
        Testing with valid user and valid perms.
        """
        self.client.login(username='hodor', password='hodor')
        Perms.objects.create(user=self.user, access_level=2).save()
        response = self.client.post('/categories/add/', {'categoryType': 'tr0npr0n'})
        self.assertRedirects(response, '/categories/')

    def test_warning_on_duplicate_category(self):
        """
        Test that we warn when adding duplicate categories
        """
        self.client.login(username='hodor', password='hodor')
        Perms.objects.create(user=self.user, access_level=2).save()
        response = self.client.post('/categories/add/', {'categoryType': 'tr0npr0n'})
        self.assertRedirects(response, '/categories/')
        response2 = self.client.post('/categories/add/', {'categoryType': 'tr0npr0n'})
        self.assertContains(response2, "already exists")

    def test_edit_category(self):
        """
        Testing category edits
        """
        self.client.login(username='hodor', password='hodor')
        Perms.objects.create(user=self.user, access_level=2).save()
        # Edit the category
        postresponse = self.client.post('/categories/edit/%s' % self.category1.id, {'categoryType': 'tr0npr0n'})
        self.assertRedirects(postresponse, '/categories/')
        # Check if edit worked
        response = self.client.get('/categories/edit/%s' % self.category1.id)
        self.assertContains(response, "tr0npr0n")

    def test_edit_with_duplicate_name(self):
        """
        Check that we do not accept edit with duplicate category name
        """
        self.client.login(username='hodor', password='hodor')
        Perms.objects.create(user=self.user, access_level=2).save()
        # Edit the category
        response = self.client.post('/categories/edit/%s' % self.category1.id, {'categoryType': 'AnotherTestCategoryType'})
        self.assertContains(response, "already exists")

    def test_view_all_categories_without_any_records(self):
        """
        Check behaviour of view_all_categories if no category exists.
        We should not get any errors
        """
        self.client.login(username='hodor', password='hodor')
        Perms.objects.create(user=self.user, access_level=2).save()
        Category.objects.all().delete()
        response = self.client.get('/categories/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_categories.html')
        self.assertNotContains(response, 'TestCategoryType')
        self.assertNotContains(response, 'AnotherTestCategoryType')
