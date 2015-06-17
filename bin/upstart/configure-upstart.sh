#!/bin/bash
#    Copyright 2014 Cyrus Dasadia
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

if [ $USER != 'root' ];then
    echo "You need to run this script as root"
    exit 1
fi

for mojofication in webapp poller; do
    echo "Configuring citoengine-$mojofication.."
    ln -sf /lib/init/upstart-job /etc/init.d/citoengine-$mojofication
    cp /opt/citoengine/bin/upstart/citoengine-$mojofication.conf /etc/init/
    /usr/sbin/update-rc.d citoengine-$mojofication defaults
done
