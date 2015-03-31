"""
Copyright 2015 Rackspace

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

from cafe.drivers.unittest.decorators import tags

from cloudcafe.common.tools.datagen import rand_name
from cloudroast.compute.fixtures import ServerFromImageFixture


class ServerRHELActivationTests(object):

    @tags(type='smoke', net='yes')
    def test_check_rhel_activation(self):
        """
        Every 'Red Hat' server should have completed RHEL activation

        For every server in the list of servers created during test set up, get
        a remote instance client and validate that the instance has completed
        Red Hat Linux activation.

        The following assertions occur:
            - Each server has completed Red Hat Linux activation
        """
        # Get an instance of the remote client
        if not self.server_list:
            self.fail("No Servers created for the activation test")
        for server in self.server_list:
            remote_instance = self.server_behaviors.get_remote_instance_client(
                server, config=self.servers_config, key=self.key.private_key)

            self.assertTrue(
                remote_instance.check_rhel_activation(),
                "Red Hat activation on server with uuid: {server_id} "
                "failed".format(server_id=server.id))


class ServerFromImageRHELActivationTests(ServerFromImageFixture,
                                         ServerRHELActivationTests):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following data is generated during this setup:
            - A list of images with 'Red Hat' in the name

        The following resources are created during this setup:
            - A keypair with a random name starting with 'key'
            - A list of servers created with the following values:
                - An image id from the list of 'Red Hat' image ids previously
                  generated
                - Remaining values required for creating a server will come
                  from test configuration.
        """
        super(ServerFromImageRHELActivationTests, cls).setUpClass()
        key_response = cls.keypairs_client.create_keypair(rand_name("key"))

        if key_response.entity is None:
                raise Exception(
                    "Response entity of create key was not set. "
                    "Response was: {0}".format(key_response.content))

        cls.key = key_response.entity
        cls.resources.add(cls.key.name,
                          cls.keypairs_client.delete_keypair)
        cls.image_ids = cls.image_behaviors.get_image_ids_by_name(
            search_name='Red Hat')
        if not cls.image_ids:
            cls.assertClassSetupFailure("Unable to find any Red Hat Enterprise"
                                        " Linux images to test.")
        cls.server_list = []
        for image_id in cls.image_ids:
            server = cls.create_server(key_name=cls.key.name,
                                       image_ref=image_id)
            cls.server_list.append(server)
