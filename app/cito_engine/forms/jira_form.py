# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import logging
from django import forms
from django.conf import settings
from jira import JIRA
import jira.resources

logger = logging.getLogger('main')


class JIRAForm(forms.Form):

    project = forms.ChoiceField(label='JIRA Project', required=True)
    summary = forms.CharField(label='Ticket Summary', max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    issue_type = forms.ChoiceField(label='Issue Type', required=True)
    component = forms.ChoiceField(label='Component', required=True)
    incident_id = forms.IntegerField()
    confirm = forms.BooleanField(label='Confirm', required=True)

    def get_choice_fields(self, opt):
        opt_string = settings.JIRA_OPTS.get(opt)
        if ',' in opt_string:
            opt_string = opt_string.split(',')
        else:
            opt_string = [opt_string]

        CHOICES = []
        for p in opt_string:
            CHOICES.append([p.strip(), p.strip()])

        return CHOICES

    def __init__(self, *args, **kwargs):
        super(JIRAForm, self).__init__(*args, **kwargs)
        # Create choicefield for projects
        self.fields['project'].choices = self.get_choice_fields('PROJECTS')
        self.fields['component'].choices = self.get_choice_fields('COMPONENTS')
        self.fields['issue_type'].choices = self.get_choice_fields('ISSUE_TYPES')

    def create_jira(self, username):
        options = {
            'server': '%s' % settings.JIRA_OPTS['URL'],
            'verify': settings.JIRA_OPTS.get('VERIFY_SSL', False)
        }
        project = self.cleaned_data.get('project')
        summary = self.cleaned_data.get('summary')
        issue_type = self.cleaned_data.get('issue_type')
        component = self.cleaned_data.get('component')
        description = self.cleaned_data.get('description')
        description += '*JIRA Created by:* %s' % username

        try:
            jconn = JIRA(options, basic_auth=(settings.JIRA_OPTS['USER'], settings.JIRA_OPTS['PASSWORD']))
        except Exception as e:
            logger.error('Error creating JIRA ticket :%s' % e)
            raise forms.ValidationError(u"Error connecting to JIRA ticket, please check the server logs")

        try:
            jira_ticket = jconn.create_issue(project=project, summary=summary, description=description,
                                             issuetype={'name': issue_type}, components=[{'name': component}])
        except Exception as e:
            logger.error('Error creating JIRA ticket project=%s, summary=%s,  issue_type=%s, description=%s,' % (project,
                                                                                                               summary,
                                                                                                               issue_type,
                                                                                                               description))
            logger.error('Server message %s' % e)
            msg = u"Error creating JIRA ticket, please check the project name and issue type. If that doesn't work then check the server logs"
            raise forms.ValidationError(msg)

        if isinstance(jira_ticket, jira.resources.Issue):
            return jira_ticket.key
        else:
            raise forms.ValidationError(u"Error creating JIRA ticket, JIRA server did not return a ticket key.")