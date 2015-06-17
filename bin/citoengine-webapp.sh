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

LOGFILE=${APP_ROOT}/logs/cito-webapp.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=2
PORT=8000
BIND_IP=0.0.0.0:${PORT}

# user/group to run as
USER=root
GROUP=root

if [ ${USER} != "www-data" ]; then
    echo "!!!WARNING!! You should probably run this script with www-data"
fi


# switch to project dir, activate
# virtual environment
cd ${APP_DIR}
source ${APP_ROOT}/bin/activate

test -d ${LOGDIR} || mkdir -p ${LOGDIR}


gunicorn settings.wsgi\
    --workers ${NUM_WORKERS} \
    --worker-class gevent  \
    --user=${USER} --group=${GROUP} \
    --log-level=debug --log-file=${LOGFILE} 2>>${LOGFILE} --bind ${BIND_IP}