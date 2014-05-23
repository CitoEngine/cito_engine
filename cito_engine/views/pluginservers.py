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

from django.db.models.query_utils import Q
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response, redirect
from cito_engine.models import PluginServer, Plugin
from cito_engine.forms import pluginserver
from cito_engine.poller import pluginpoller

@login_required(login_url='/login/')
def view_all_pluginservers(request):
    render_vars = dict()
    if request.user.perms.access_level > 3:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))

    search_form = pluginserver.PluginSearchForm()
    if request.method == "POST":
        search_form = pluginserver.PluginSearchForm(request.POST)
        if search_form.is_valid():
            search_term = search_form.cleaned_data.get('search_term')
            render_vars['plugins'] = Plugin.objects.filter(Q(name__icontains=search_term) |
                                                           Q(description__icontains=search_term))
            render_vars['search_term'] = search_term
    if request.method == "GET":
        try:
            render_vars['servers'] = PluginServer.objects.all()
        except PluginServer.DoesNotExist:
            render_vars['servers'] = None

    render_vars[search_form] = search_form
    return render_to_response('view_all_pluginservers.html', render_vars, context_instance=RequestContext(request))


@login_required(login_url='/login/')
def view_single_pluginserver(request, pluginserver_id):
    if request.user.perms.access_level > 3:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'View plugin server'
    box_title = page_title
    pluginserver = get_object_or_404(PluginServer, pk=pluginserver_id)
    return render_to_response('view_pluginserver.html', locals(), context_instance=RequestContext(request))

@login_required(login_url='/login/')
def add_pluginserver(request):
    if request.user.perms.access_level > 2:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'Add a plugin server'
    box_title = page_title
    if request.method == "POST":
        form = pluginserver.PluginServerForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data.get('url')
            if PluginServer.objects.filter(url__iexact=url).count() > 0:
                errors = ['A server with URL: %s already exists.' % url]
            else:
                form.save()
                return redirect('/pluginservers/')
    else:
        form = pluginserver.PluginServerForm()
    return render_to_response('generic_form.html', locals(), context_instance=RequestContext(request))

@login_required(login_url='/login/')
def edit_pluginserver(request, pluginserver_id):
    if request.user.perms.access_level > 2:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    page_title = 'Editing plugin server'
    box_title = page_title
    ps = get_object_or_404(PluginServer, pk=pluginserver_id)
    if request.method == "POST":
        form = pluginserver.PluginServerForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            url = form.cleaned_data.get('url')
            status = form.cleaned_data.get('status')
            ssl_verify = form.cleaned_data.get('ssl_verify')
            if PluginServer.objects.filter(~Q(pk=pluginserver_id), url__iexact=url).count() > 0:
                errors = ['A server with URL: %s already exists' % url]
            else:
                query = dict(name=name, url=url, status=status, ssl_verify=ssl_verify)
                PluginServer.objects.filter(pk=pluginserver_id).update(**query)
                return redirect('/pluginservers/view/%s/' % pluginserver_id)
    else:
        form = pluginserver.PluginServerForm(instance=ps)
    return render_to_response('generic_form.html', locals(), context_instance=RequestContext(request))

@login_required(login_url='/login/')
def refresh_pluginserver(request, pluginserver_id):
    if request.user.perms.access_level > 2:
        return render_to_response('unauthorized.html', context_instance=RequestContext(request))
    plugin_server = get_object_or_404(PluginServer, pk=pluginserver_id)
    pluginpoller.pluginpoller(plugin_server)
    return redirect('/pluginservers/view/%s/' % pluginserver_id)
