from django.db import models
from cito_engine.models import Incident


class AuditLog(models.Model):
    LOG_TYPE_CHOICES = (('info', 'info'),
                        ('warn', 'warn'),
                        ('error', 'error'),
                        )
    date_added = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    level = models.CharField(choices=LOG_TYPE_CHOICES, default='info', max_length=5)


class IncidentAuditLog(AuditLog):
    incident = models.ForeignKey(Incident, db_index=True)

    def __unicode__(self):
        return '%s:%s:%s' % (self.date_added, self.level, self.message[:10])