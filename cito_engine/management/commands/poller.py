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


from django.core.management.base import BaseCommand
from cito_engine.poller import event_poller


class Command(BaseCommand):

    help = 'Start CitoEngine Event Poller'

    def handle(self, *args, **options):
        e = event_poller.EventPoller()
        e.begin_event_poller()

