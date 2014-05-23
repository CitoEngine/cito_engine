# Django settings for cito project.
# Copyright (c) 2012-2013 Cyrus Dasadia <cyrus@extremeunix.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import requests
import logging
from cito_engine.models import Plugin, PluginServer

logger = logging.getLogger('poller_logger')


def pluginpoller(server):
    url = server.url+'/getallplugins'

    try:
        response = requests.get(url, verify=server.ssl_verify)
    except BaseException, e:
        logger.error('Could not connect to PluginServer: %s [EXCEPTION] %s' % (url, e))
        return False

    try:
        jsondata = response.json()
    except:
        logger.error('PluginServer: %s gave invalid JSON response')
        return False

    logger.info("Found %s plugins" % len(jsondata))

    pluginNames = []

    #Add or update plugins
    for k in jsondata:
        pluginNames.append(k['plugins']['name'])
        try:
            p = Plugin.objects.get(server=server, name__iexact=k['plugins']['name'])
            p.description = k['plugins']['description']
            p.status = k['plugins']['status']
            p.save()
            logger.info("Plugin: %s already existed and updated" % k['plugins']['name'])
        except Plugin.DoesNotExist:
            Plugin.objects.create(server=server,
                                  name=k['plugins']['name'],
                                  description=k['plugins']['description'],
                                  status=k['plugins']['status'])
            logger.info('Plugin: %s added' % k['plugins']['name'])
        except Plugin.MultipleObjectsReturned:
            logger.error("More than one plugin exists for %s, remove the duplicates!" % k['plugins']['name'])
        except BaseException as e:
            logger.error("Could not add plugin: %s" % e.args)

    #Disable all deprecated plugins
    plugins = Plugin.objects.filter(server=server)
    if plugins is not None:
        for p in plugins:
            if p.name not in pluginNames:
                logger.info("Plugin: %s is deprecated on plugin server, disabling here" % p.name)
                p.description = 'WARNING: This plugin has been DEPRECATED on remote server!!!!\n'
                p.status = False
                p.save()
    return True


def update_plugins():
    pluginservers = PluginServer.objects.all()
    for server in pluginservers:
        if server.status:
            logger.info("Fetching from %s" % server.name)
            pluginpoller(server)
        else:
            logger.info("Server at %s ignored." % server.name)

