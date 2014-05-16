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


class HourlyData(models.Model):
    event_id = models.IntegerField()
    team_id = models.IntegerField()
    severity = models.CharField(max_length=4)
    category = models.CharField(max_length=64)
    hour = models.DateTimeField()
    total_incidents = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return "EventID:%s,Team:%s,Severity:%s,Category:%s,Hour:%s,Total_Incidents:%s" % \
               (self.event_id, self.team_id, self.severity, self.category, self.hour, self.total_incidents)

    def csv_string(self):
        return ",".join([unicode(m) for m in
                         [self.event_id, self.team_id, self.severity, self.category, self.hour, self.total_incidents]])


class DailyData(models.Model):
    event_id = models.IntegerField()
    team_id = models.IntegerField()
    severity = models.CharField(max_length=4)
    category = models.CharField(max_length=64)
    day = models.DateField()
    total_incidents = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return "EventID:%s,Team:%s,Severity:%s,Category:%s,Day:%s,Total_Incidents:%s" % \
               (self.event_id, self.team_id, self.severity, self.category, self.day, self.total_incidents)

    def csv_string(self):
        return ",".join([unicode(m) for m in
                         [self.event_id, self.team_id, self.severity, self.category, self.day, self.total_incidents]])