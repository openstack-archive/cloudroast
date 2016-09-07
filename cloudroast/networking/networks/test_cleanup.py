"""
Copyright 2016 Rackspace

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

from prettytable import PrettyTable

from cafe.drivers.unittest.fixtures import BaseTestFixture
from cloudcafe.networking.networks.common.composites import CustomComposite
from cloudcafe.networking.networks.common.tools.resources import Resources


class NetworkingCleanUp(BaseTestFixture):
    """Clean up test for networking related resources.

    Uses the delete_networking method from the Resources class at:
        networking.networks.common.tools.resources
    By default it will try to delete all user resources that start with
    the name "test". Still, the delete resource dict can be set by
        export CAFE_networking_delete_resources='{"all": "*"}'
        or delete_resources={"all": "*"} under the networking section
        in the config file. The {"all": "*"} resource dict is an
        example to delete all user resources.
    """

    @classmethod
    def setUpClass(cls):
        super(NetworkingCleanUp, cls).setUpClass()
        cls.cc = CustomComposite()
        cls.res = Resources()
        cls.config = cls.cc.net.config

        # User data (getting from custom composite object)
        net_auth = cls.cc.networking_auth_composite
        net_url = net_auth.public_url
        net_region = net_auth.region

        comp_auth = cls.cc.compute_auth_composite
        comp_url = comp_auth.public_url
        comp_region = comp_auth.region

        user = net_auth.user_config
        username = user.username
        tenant_id = user.tenant_id
        user_id = user.user_id

        # Generating user data display table
        user_data = PrettyTable()
        user_data.field_names = ['User name', 'Tenant ID', 'User ID', ]
        user_data.add_row([username, tenant_id, user_id])

        env_data = PrettyTable()
        env_data.field_names = ['Product', 'Region', 'API URL']
        env_data.add_row(['Networks', net_region, net_url])
        env_data.add_row(['Compute', comp_region, comp_url])
        env_data.align = "l"

        # Displaying user data
        print user_data
        print env_data

        # Displaying initial user resources
        print '\n'
        print '*'*50
        print 'Resources before DELETE calls'
        cls.display_resources()

        # Getting resource dict from config file if given
        cls.resource_dict = cls.config.delete_resources

        # If resource dict not given, in the config file,
        # only resources starting with the name test will be deleted
        if not cls.resource_dict:
            cls.resource_dict = {'all': 'test*'}

    @classmethod
    def tearDownClass(cls):
        super(NetworkingCleanUp, cls).tearDownClass()

        # Displaying final user resources
        print '*'*50
        print 'Resources after DELETE calls'
        cls.display_resources()

    @classmethod
    def display_resources(self):
        """ Displaying resources """
        print '*'*50
        print 'User Resources'
        self.res.list_networking()
        print '*'*50
        print '\n\n'

    def test_delete_networking(self):
        """Deleting networking resources"""

        print '\nResources to delete dict:'
        print self.resource_dict
        print ('Note: to delete all resources export or set in config:'
               '\nCAFE_networking_delete_resources={\"all\": \"*\"}')
        self.res.delete_networking(resource_dict=self.resource_dict)
