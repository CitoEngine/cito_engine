# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
from django.views.generic.edit import FormView, View
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from cito_engine.forms.jira_form import JIRAForm
from cito_engine.models import JIRATickets, Incident
from braces.views import LoginRequiredMixin


class JIRAAddView(LoginRequiredMixin, FormView):
    """
    View to add Supression
    """
    template_name = 'generic_form.html'
    form_class = JIRAForm
    success_url = '/incidents/'

    def get_context_data(self, **kwargs):
        context = super(JIRAAddView, self).get_context_data(**kwargs)
        context['page_title'] = context['box_title'] = 'Add JIRA'
        return context

    def form_valid(self, form):
        try:
            incident = Incident.objects.get(pk=form.cleaned_data.get('incident_id'))
        except Incident.DoesNotExist, Incident.MultipleObjectsReturned:
            redirect('/incidents/')
            return
        try:
            ticket = form.create_jira(username=self.request.user.username)
        except Exception as e:
            return HttpResponse(status=500, content=e)
        JIRATickets.objects.create(user=self.request.user, incident=incident, ticket=ticket)
        return redirect('/incidents/view/%s/' % incident.id)
