#!/bin/bash
#    Copyright 2014-2015 Cyrus Dasadia
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
APP_ROOT=/opt/citoengine/
APP_DIR=${APP_ROOT}/app

cd ${APP_DIR}
source ${APP_ROOT}bin/activate
echo 'Starting CitoEngine Poller'
python manage.py poller

