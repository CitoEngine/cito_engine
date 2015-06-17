from collections import defaultdict
from glob import glob
import os
import re

if os.environ.get('USE_SETUPTOOLS'):
    from setuptools import setup
    setup_kwargs = dict(zip_safe=0)
else:
    from distutils.core import setup
    setup_kwargs = dict()

app_content = defaultdict(list)

for root, dirs, files in os.walk('app'):
    for filename in files:
        if not filename.endswith('pyc'):
            filepath = os.path.join(root, filename)
            app_content[root].append(filepath)

conf_files = [('conf', glob('app/settings/*-example'))]
bin_files = defaultdict(list)
for root, dirs, files in os.walk('bin'):
    for filename in files:
        filepath = os.path.join(root, filename)
        bin_files[root].append(filepath)
log_dir = [('logs', '')]


def find_version(file_path):
    """
    Build a path __init__
    """
    version_file = open(file_path+'__init__.py', 'r').read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string in %s" % version_file)
setup(
    name='citoengine',
    author='Cyrus Dasadia',
    author_email='cyrus@citoengine.org',
    description='Alert management and automation tool',
    version=find_version('app/'),
    url='http://www.citoengine.org',
    license='Apache Software License 2.0',
    package_dir={'': 'app'},
    data_files=app_content.items()+conf_files+bin_files.items()+log_dir,
    **setup_kwargs
)

