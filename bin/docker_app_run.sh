#!/bin/bash
#    Copyright 2016-2017 K.G.R Vamsi
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


set -e

PORT=8000
BIND_IP=0.0.0.0:${PORT}

service rabbitmq-server  start

#Rabbitmq adding the necessary info
rabbitmqctl add_user citoengine changeme!
rabbitmqctl add_vhost /citoengine_event_listener
rabbitmqctl set_permissions -p /citoengine_event_listener citoengine_user ".*" ".*" ".*"
rabbitmqctl set_permissions -p /citoengine_event_listener citoengine ".*" ".*" ".*"

service mysql restart

echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'password')" | python app/manage.py shell

python app/manage.py runserver $BIND_IP
