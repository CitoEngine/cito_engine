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

from fabric.api import run, local, env, sudo, put, warn_only
from fabric.context_managers import cd, prefix
from fabric.colors import yellow, green
from fabric.contrib.files import append
from fabric.operations import prompt
from getpass import getpass
import inspect
import random

env.app_dir = '/opt/cito'
env.venv_dir = '/opt/virtualenvs/citovenv'
env.pip_file = 'requirements.txt'


def install_virtualenv():
    print(yellow('Starting >> %s()' % _fn()))
    sudo('pip -q install virtualenv')


def setup_virtualenv():
    print(yellow('Starting >> %s()' % _fn()))
    run('virtualenv --no-site-packages %(venv_dir)s' % env, pty=True)


def update_requirements():
    print(yellow('Starting >> %s()' % _fn()))
    with cd(env.app_dir):
        ve_run('pip install -q --upgrade setuptools')
        ve_run('pip install -q -r %s' % env.pip_file)


def mkdirs():
    print(yellow('Starting >> %s()' % _fn()))
    sudo('mkdir -p %(app_dir)s && chown %(user)s %(app_dir)s' % env)
    sudo('mkdir -p %(venv_dir)s && chown %(user)s %(venv_dir)s' % env)


def upload_reqs():
    print(yellow('Starting >> %s()' % _fn()))
    put('requirements.txt', env.app_dir)


def install_build_deps():
    print(yellow('Starting >> %s()' % _fn()))
    _detect_pkg_manager()
    with warn_only():
        sudo('%(pkg_manager)s -y install build-essential python-dev python-mysqldb python-pip  libmysqlclient-dev' % env)


def install_mysql():
    print(yellow('Starting >> %s()' % _fn()))
    _detect_pkg_manager()
    with warn_only():
        sudo('%(pkg_manager)s -y install mysql-server mysql-client' % env)


def bootstrap():
    install_build_deps()
    install_virtualenv()
    mkdirs()
    upload_reqs()
    setup_virtualenv()
    update_requirements()
    install_mysql()


def deploy():
    dj_copy_vagrant()
    dj_create_secret()
    dj_dbconfig()
    dj_syncdb()
    dj_create_superuser()


#################
# Django specific methods
#################

# noinspection PyBroadException
def dj_dbconfig(createdb=False):
    """
    Setup mysql root password, create the db and update the config
    """
    env.mysql_user = prompt(green("Enter MySQL username: "))
    env.mysql_password = getpass(green("Enter MySQL password (will not display on screen): "))
    env.mysql_dbname = prompt(green("Enter MySQL DB Name (default=cito): "), default='cito')
    if createdb:
        run('mysqladmin -u %(mysql_user)s -p%(mysql_password)s create %(mysql_dbname)s' % env)

    with cd(env.app_dir):
        sudo('chown %(user)s %(app_dir)s/%(django_settings_file)s' % env)
        append('%(app_dir)s/%(django_settings_file)s' % env, "\nDATABASES['default']['USER'] = '%(mysql_user)s'" % env)
        append('%(app_dir)s/%(django_settings_file)s' % env, "DATABASES['default']['PASSWORD'] = '%(mysql_password)s'" % env)
        append('%(app_dir)s/%(django_settings_file)s' % env, "DATABASES['default']['NAME'] = '%(mysql_dbname)s'" % env)


def dj_create_superuser():
    """
    Creates django superuser
    """
    print(yellow('Starting >> %s()' % _fn()))
    with cd(env.app_dir):
        ve_run('python manage.py createsuperuser --settings=%s' % env.django_settings_module)


def dj_copy_vagrant(from_dir='/vagrant/'):
    """
    Copies the files from /vagrant onto env.app_dir. Can be used as an alternate to git clone <repo>
    """
    print(yellow('Starting >> %s(from:%s to:%s)' % (_fn(), from_dir, env.app_dir)))
    with cd(env.app_dir):
        sudo('cp -Rpf %s/* ./ ' % from_dir)
        sudo('chown -R %(user)s %(app_dir)s/logs' % env)


def dj_syncdb():
    """
    Initial db sync
    """
    print(yellow('Starting >> %s()' % _fn()))
    with cd(env.app_dir):
        ve_run('python manage.py syncdb --noinput --migrate --settings=%s' % env.django_settings_module)


def dj_create_secret():
    """
    Creates new SECRET_KEY everytime its run
    """
    print(yellow('Starting >> %s()' % _fn()))
    with cd(env.app_dir):
        sudo('chown %(user)s %(app_dir)s/cito/settings/secret_key.py' % env)
        secret_sauce = "".join([random.SystemRandom().choice("abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)") for i in range(50)])
        append('%(app_dir)s/cito/settings/secret_key.py' % env, "SECRET_KEY = '%s'" % secret_sauce)




#################
# Helper methods
#################


def _fn():
    return inspect.stack()[1][3]


def e(environment='dev'):
    env.environment = environment
    env.django_settings_module = 'cito.settings.%s' % environment
    env.django_settings_file = 'cito/settings/%s.py' % environment
    print(green('django setttings set to %(django_settings_module)s' % env))
    return


def _get_vagrant_ssh_config():
    result = local('vagrant ssh-config', capture=True)
    conf = {}
    for line in iter(result.splitlines()):
        parts = line.split()
        conf[parts[0]] = ' '.join(parts[1:])
    return conf


def ve_run(command, func=run, base_dir=env.app_dir, *args, **kwargs):
    with cd(base_dir):
        with prefix('source %(venv_dir)s/bin/activate' % env):
            return func(command, *args, **kwargs)


def _detect_pkg_manager():
    print(yellow('Starting >> %s()' % _fn()))
    managers = ['apt-get', 'yum', 'zypper']
    with warn_only():
        for v in managers:
            env.pkg_manager = run('which %s' % v).stdout
            print(green('Package manager is %(pkg_manager)s' % env))
            return


def hostname():
    print(yellow('Starting >> %s()' % _fn()))
    run("uname -a")


def vagrant(user='vagrant'):
    print(yellow('Starting >> %s()' % _fn()))
    print(yellow('Setting user as %s' % user))
    env.user = user
    vagrant.config = _get_vagrant_ssh_config()
    env.key_config = vagrant.config['IdentityFile']
    env.hosts = ['%s:%s' % (vagrant.config['HostName'], vagrant.config['Port'])]
    env.user = vagrant.config['User']
