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
