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

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseBadRequest
from django.template import RequestContext
from cito_engine.models import Team
from cito_engine.forms import permissions, user_form
from appauth.models import Perms


@login_required(login_url='/login/')
def view_all_users(request):
    users = User.objects.all()
    return render(request=request, template_name='view_all_users.html', context={'users': users})


@login_required(login_url='/login/')
def view_single_user(request, user_id):
    status_text = ''
    view_user = get_object_or_404(User, pk=user_id)
    perms, create = Perms.objects.get_or_create(user=view_user)
    if create:
        status_text = 'This is the first time you are viewing the user perms.'
        perms.access_level = 4
        perms.save()
    permform = permissions.PermsForm(instance=perms)

    try:
        allteams = Team.objects.all()
    except Team.DoesNotExist:
        allteams = None
    return render(request, 'view_user.html', {'view_user': view_user, 'allteams': allteams, 'form': permform, 'status_text': status_text})


@login_required(login_url='/login/')
def modify_user_team_membership(request, toggle):
    if request.user.perms.access_level > 2:
        return render(request, 'unauthorized.html')
    if request.method == 'POST' and toggle in ['add', 'remove']:
        user_id = request.POST.get('user_id')
        team_id = request.POST.get('team_id')
        user = get_object_or_404(User, pk=user_id)
        team = get_object_or_404(Team, pk=team_id)
        if toggle == 'add':
            user.team_set.add(team)
        elif toggle == 'remove':
            user.team_set.remove(team)
        return redirect('/users/view/%s/' % user_id)
    else:
        return HttpResponseBadRequest()


@login_required(login_url='/login/')
def update_user_perms(request):
    if request.user.perms.access_level > 2:
        return render(request, 'unauthorized.html')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        form = permissions.PermsForm(request.POST)
        if form.is_valid():
            access_level = form.cleaned_data['access_level']
            try:
                u = Perms.objects.get(user=user)
                if u:
                    u.access_level = access_level
                    u.save()
            except Perms.DoesNotExist:
                Perms.objects.create(user=user, access_level=access_level)
            return redirect('/users/view/%s/' % user_id)
        else:
            return HttpResponseBadRequest()
    else:
        return redirect('/users/')


@login_required(login_url='/login/')
def create_user(request):
    if request.user.perms.access_level > 2:
        return render(request, 'unauthorized.html')
    render_vars = dict()
    form = user_form.UserCreationForm()
    if request.method == "POST":
        form = user_form.UserCreationForm(request.POST)
        if form.is_valid():
            fname = form.cleaned_data.get('fname')
            lname = form.cleaned_data.get('lname')
            username = form.cleaned_data.get('username')
            password1 = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            access_level = form.cleaned_data.get('access_level')
            teams = form.cleaned_data.get('teams')
            user = User.objects.create_user(first_name=fname, last_name=lname,
                                            password=password1, email=email, username=username)
            for team in teams:
                user.team_set.add(team)
            user.save()
            Perms.objects.create(user=user, access_level=access_level).save()
            return redirect('/users/')
    render_vars['form'] = form
    return render(request, 'generic_form.html', render_vars)


@login_required(login_url='/login/')
def edit_user(request, user_id):
    render_vars = dict()
    user = get_object_or_404(User, pk=user_id)
    if request.user.perms.access_level > 2 and request.user != user:
        return render(request, 'unauthorized.html')
    if request.method == "POST":
        form = user_form.EditUserForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.username = form.cleaned_data.get('username')
            user.email = form.cleaned_data.get('email')
            user.save()
            password = form.cleaned_data.get('password1')
            if password:
                user.set_password(password)
                user.save()
            return redirect('/users/view/%s/' % user.id)
    else:
        form_vars = {'first_name': user.first_name,
                     'last_name': user.last_name,
                     'email': user.email,
                     'username': user.username}
        form = user_form.EditUserForm(initial=form_vars)
    render_vars['form'] = form
    render_vars['page_title'] = render_vars['box_title'] = 'Editing user: %s ' % user.username
    return render(request, 'generic_form.html', render_vars)


@login_required(login_url='/login/')
def toggle_user(request):
    if request.user.perms.access_level > 2:
        return render(request, 'unauthorized.html')
    if request.method == 'POST':
        try:
            user_id = int(request.POST.get('user_id'))
        except:
            raise forms.ValidationError("Invalid user toggle form received!")
        user = get_object_or_404(User, pk=user_id)
        if user.is_active and user != request.user:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return redirect('/users/view/%s/' % user_id)
