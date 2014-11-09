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

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from ipware.ip import get_ip
from appauth.models import Perms
import logging
auth_logger = logging.getLogger('auth_logger')


def check_and_create_perms(user):
    try:
        Perms.objects.get(user=user)
    except Perms.DoesNotExist:
        # If its a django superuser
        if user.is_superuser:
            Perms.objects.create(user=user, access_level=1).save()
        #else we make it a reportuser
        else:
            Perms.objects.create(user=user, access_level=5).save()
    return True


def login_user(request):
    state = ''
    username = ''
    password = ''
    redirect_to = request.REQUEST.get('next')
    ip = get_ip(request)
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        redirect_to = request.POST.get('redirect_to')
        user = authenticate(username=username, password=password)
        if user is not None:
            auth_logger.info('User:%s logged in from %s' % (username, ip))
            if user.is_active:
                login(request, user)
                check_and_create_perms(user)
                if user.perms.access_level == 5:
                    return redirect(redirect_to or '/reports/')
                else:
                    return redirect(redirect_to or '/incidents/')
            else:
                state = "Your account is inactive, please contact the administrator."
        else:
            auth_logger.info('Failed login attempt from user:%s from %s' % (username, ip))
            state = "Username/Password incorrect"

    return render_to_response('login.html',
                              {'state': state, 'username': username, 'redirect_to': redirect_to},
                              context_instance=RequestContext(request))


def logout_user(request):
    logout(request)
    ip = get_ip(request)
    auth_logger.info('User:%s logged out from %s' % (request.user.username, ip))
    return render_to_response('logout.html', context_instance=RequestContext(request))
