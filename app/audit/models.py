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