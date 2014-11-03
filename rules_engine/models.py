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
from cito_engine.models import Event


class ParentEvents(models.Model):
    """
    A ParentEvent, if alerted on, would mute all other alerts for that element i.e. EventActions on
    other alerts on this element would not be executed.
    """
    element = models.CharField(db_index=True, max_length=255)
    event = models.ForeignKey(Event)

    def __unicode__(self):
        return unicode('%s|%s' % (self.element, self.event))


class EventSuppressor(models.Model):
    """
    Suppress an event
    """
    event = models.ForeignKey(Event, db_index=True)
    suppressed_by = models.ForeignKey(User)
    date_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode('%s|%s' % (self.event, self.suppressed_by))


class ElementSuppressor(models.Model):
    """
    Suppress an element
    """
    element = models.CharField(db_index=True, max_length=255)
    suppressed_by = models.ForeignKey(User)
    date_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode('%s|%s' % (self.element, self.suppressed_by))


class EventAndElementSuppressor(models.Model):
    """
    Suppresses an Event + Element combination
    """
    event = models.ForeignKey(Event, db_index=True)
    element = models.CharField(db_index=True, max_length=255)
    suppressed_by = models.ForeignKey(User)
    date_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode('%s|%s|%s' % (self.element, self.event, self.suppressed_by))
