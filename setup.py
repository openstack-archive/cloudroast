"""
Copyright 2013 Rackspace

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

import os
import sys

import cloudroast
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requires = open('pip-requires').readlines()

setup(
    name='cloudroast',
    version=cloudroast.__version__,
    description='CloudCAFE based automated test repository for OpenStack',
    long_description='{0}\n\n{1}'.format(
        open('README.md').read(),
        open('HISTORY.md').read()),
    author='Rackspace Cloud QE',
    author_email='cloud-cafe@lists.rackspace.com',
    url='http://rackspace.com',
    packages=find_packages(exclude=[]),
    package_data={'': ['LICENSE', 'NOTICE']},
    package_dir={'cloudroast': 'cloudroast'},
    include_package_data=True,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    #https://the-hitchhikers-guide-to-packaging.readthedocs.org/en/latest/specification.html
    classifiers=(
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    )
)

''' @todo: need to clean this up or do it with puppet/chef '''
# Default Config Options
root_dir = "{0}/.cloudcafe".format(os.path.expanduser("~"))
config_dir = "{0}/configs".format(root_dir)

# Build Default directories
if(os.path.exists("{0}/engine.config".format(config_dir)) == False):
    raise Exception("Core CAFE Engine configuration not found")
else:
    # Copy over the default configurations
    if(os.path.exists("~install")):
        os.remove("~install")
        # Report
        print('\n'.join(["\t\t   (----) (----)--)",
                         "\t\t    (--(----)  (----) --)",
                         "\t\t  (----) (--(----) (----)",
                         "\t\t  -----------------------",
                         "\t\t  \                     /",
                         "\t\t   \                   /",
                         "\t\t    \_________________/",
                         "\t\t     === CloudRoast ===",
                         "\t\t= A CloudCAFE Test Repository ="]))
    else:
        # State file
        temp = open("~install", "w")
        temp.close()
