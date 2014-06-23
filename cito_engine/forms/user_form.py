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

from django import forms
from django.contrib.auth.models import User
from appauth.models import Perms
from cito_engine.models import Team


class UserCreationForm(forms.Form):
    fname = forms.CharField(label='First name', max_length=100)
    lname = forms.CharField(label='Last name', max_length=100)
    username = forms.CharField(max_length=100)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    email = forms.EmailField()
    access_level = forms.ChoiceField(choices=Perms.PERMISSION_LEVEL)

    teams = forms.MultipleChoiceField()

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.team_list = []
        for team in Team.objects.all():
            self.team_list.append((team.id, team.name))
        self.fields['teams'].choices = self.team_list


    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(u"That username is already taken, please select another.")

    def clean(self):
        cleaned_data = super(UserCreationForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            msg = u"The passwords did not match. Please try again."
            self._errors["password1"] = self.error_class([msg])
            self._errors["password2"] = self.error_class([msg])
        return cleaned_data


class EditUserForm(forms.Form):
    first_name = forms.CharField(label='First name', max_length=100)
    last_name = forms.CharField(label='Last name', max_length=100)
    username = forms.CharField(max_length=100)
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, required=False)
    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields['password1'].help_text = "Leave blank if you dont want to change it"

    def clean(self):
        cleaned_data = super(EditUserForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            msg = u"The passwords did not match. Please try again."
            self._errors["password1"] = self.error_class([msg])
            self._errors["password2"] = self.error_class([msg])
        return cleaned_data