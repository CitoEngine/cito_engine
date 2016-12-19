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

from django.db import models
from django.contrib.auth.models import User


class PluginServer(models.Model):
    name = models.CharField(max_length=128)
    url = models.TextField()
    status = models.BooleanField(default=True)

    def __unicode__(self):
        return unicode(self.name)

    @property
    def activePlugins(self):
        return Plugin.objects.filter(server=self, status=True).count()

    @property
    def inactivePlugins(self):
        return Plugin.objects.filter(server=self, status=False).count()

    @property
    def plugins(self):
        return Plugin.objects.filter(server=self)

    ssl_verify = models.BooleanField(default=True)


class Plugin(models.Model):
    server = models.ForeignKey(PluginServer)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)
    dateAdded = models.DateTimeField(auto_now_add=True)
    lastUpdated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __unicode__(self):
        return unicode('%s -> %s' % (self.server.name, self.name))


class Category(models.Model):
    categoryType = models.CharField(max_length=64)

    def __unicode__(self):
        return unicode(self.categoryType)

    class Meta:
        ordering = ['categoryType']


class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    members = models.ManyToManyField(User, default=None, blank=True)

    def __unicode__(self):
        return unicode(self.name)
    
    class Meta:
        ordering = ['name']


class Event(models.Model):
    EVENT_SEVERITY = (
        ('S0', 'S0'),
        ('S1', 'S1'),
        ('S2', 'S2'),
        ('S3', 'S3'),
    )
    summary = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=2, choices=EVENT_SEVERITY, default='S3')
    team = models.ForeignKey(Team)
    category = models.ForeignKey(Category)
    status = models.BooleanField(default=True)

    def __unicode__(self):
        return unicode('%s|%s' % (self.id, self.summary))


class Incident(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Acknowledged', 'Acknowledged'),
        ('Cleared', 'Cleared')
    )
    event = models.ForeignKey(Event)
    element = models.CharField(max_length=255)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Active')
    firstEventTime = models.DateTimeField(auto_now_add=True)
    lastEventTime = models.DateTimeField(null=True, blank=True)
    acknowledged_time = models.DateTimeField(null=True, blank=True)
    close_time = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(User, null=True, blank=True, default=None, related_name='+')
    closed_by = models.ForeignKey(User, null=True, blank=True, default=None, related_name='+')
    total_incidents = models.IntegerField(default=0)
    is_suppressed = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode('%s:%s:%s' % (self.event.id, self.element, self.status))

    @property
    def incidentInfo(self):
        return u'EventID:%s,Element:%s' % (self.event.id, self.element)

    @property
    def is_open(self):
        if self.status != 'Cleared':
            return True
        else:
            return False

    def increment_count(self):
        self.total_incidents += 1
        self.save()

    def toggle_status(self, status, user, time):
        if self.status != 'Cleared' and status in ['Acknowledged', 'Cleared']:
            self.status = status
            if status == 'Acknowledged':
                self.acknowledged_by = user
                self.acknowledged_time = time
            elif status == 'Cleared':
                self.closed_by = user
                self.close_time = time
                # delete counters
                for counter in EventActionCounter.objects.filter(incident=self):
                    counter.delete()
        self.save()
        return

    def suppressed(self):
        """ Incident suppression flag set true
        """
        self.is_suppressed = True
        self.save()


class IncidentLog(models.Model):
    incident = models.ForeignKey(Incident)
    msg = models.TextField(max_length=255, default='No text provided')
    timestamp = models.DateTimeField()

    def __unicode__(self):
        return u'%s' % self.incident


class EventAction(models.Model):
    event = models.ForeignKey(Event)
    plugin = models.ForeignKey(Plugin)
    pluginParameters = models.TextField(null=True, blank=True)
    dateAdded = models.DateTimeField(auto_now_add=True)
    dateUpdated = models.DateTimeField(auto_now=True)
    isEnabled = models.BooleanField(default=True)
    # Following two vars set the threshold as to when an action
    # e.g. if 1 occurrences in 60 seconds -> trigger the action
    threshold_count = models.IntegerField(default=1)
    threshold_timer = models.IntegerField(default=60)  # Will be treated as seconds

    def __unicode__(self):
        return unicode('%s|%s' % (self.event, self.plugin))


class EventActionCounter(models.Model):
    incident = models.ForeignKey(Incident)
    event_action = models.ForeignKey(EventAction)
    count = models.IntegerField(default=1)
    timer = models.IntegerField(default=0)
    is_triggered = models.BooleanField(default=False)

    def update_counters(self, timer_value):
        """
        Updates timer (in seconds) upon each call but updates the counter until the threshold is met
        :param timer_value:
        """
        if self.count < self.event_action.threshold_count:
            self.count += 1
        self.timer += timer_value
        self.save()

    @property
    def is_action_required(self):
        # Got an incident outside the timer
        if self.timer > self.event_action.threshold_timer:
            # If threshold was one incident in Y secs, we have to return True
            if self.event_action.threshold_count == 1:
                self.is_triggered = True
                self._reset_all()
                return True

            # else
            self.is_triggered = False
            self._reset_all()

        # Check if X incidents occured in Y seconds
        elif self.count >= self.event_action.threshold_count and self.timer <= self.event_action.threshold_timer:
            if not self.is_triggered:
                self.is_triggered = True
                self.save()
                return True

        return False

    def _reset_all(self):
        self.count = 1
        self.timer = 0
        self.save()

    def __unicode__(self):
        return '%s:%s' % (self.incident.id, self.event_action.plugin)


class EventActionLog(models.Model):
    eventAction = models.ForeignKey(EventAction)
    incident = models.ForeignKey(Incident)
    dateAdded = models.DateTimeField(auto_now_add=True)
    text = models.TextField(default='No text provided')

    def __unicode__(self):
        return unicode('%s|%s' % (self.eventAction, self.dateAdded))

class JIRATickets(models.Model):
    incident = models.ForeignKey(Incident)
    user = models.ForeignKey(User)
    ticket = models.CharField(verbose_name='JIRA Ticket ID', max_length=64)
    creation_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode('%s' % self.ticket)
