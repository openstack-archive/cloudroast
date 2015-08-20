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

from unittest.suite import TestSuite

from cloudcafe.common.tools.datagen import rand_name

from cloudroast.glance.fixtures import ImagesIntegrationFixture


def load_tests(loader, standard_tests, pattern):
    suite = TestSuite()
    suite.addTest(DeactivateReactivateServers(
        'test_deactivate_snapshot_image'))
    suite.addTest(DeactivateReactivateServers(
        'test_create_server_from_deactivated_image_invalid'))
    suite.addTest(DeactivateReactivateServers(
        'test_reactivate_snapshot_image'))
    suite.addTest(DeactivateReactivateServers(
        'test_create_server_from_reactivated_image'))
    return suite


class DeactivateReactivateServers(ImagesIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following resources are created during this setup:
            - A server with defaults defined in server behaviors
            - An image from the newly created server
        """

        super(DeactivateReactivateServers, cls).setUpClass()
        cls.server = (
            cls.compute.servers.behaviors.create_active_server().entity)
        cls.image = cls.compute.images.behaviors.create_active_image(
            cls.server.id).entity
        cls.resources.add(
            cls.server.id, cls.compute.servers.client.delete_server)
        cls.resources.add(cls.image.id, cls.images_client.delete_image)

    def test_deactivate_snapshot_image(self):
        """
        Verify that a snapshot image can be deactivated

        Deactivate a snapshot image

        This test will be successful if:
            - The response code received for deactivate image is a 204
        """

        self.resp = self.images_admin.client.deactivate_image(self.image.id)
        self.assertEqual(204, self.resp.status_code)

    def test_create_server_from_deactivated_image_invalid(self):
        """
        Verify that a server cannot be created from a deactivated image

        Attempt to create a server using a deactivated image

        This test will be successful if:
            - The response code received for deactivate image is a 400
        """

        resp = self.compute.servers.client.create_server(
            name=rand_name("server"),
            flavor_ref=self.flavor_ref,
            image_ref=self.image.id)
        self.assertEqual(400, resp.status_code)

    def test_reactivate_snapshot_image(self):
        """
        Verify that a snapshot image can be reactivated

        Reactivate a snapshot image

        This test will be successful if:
            - The response code received for deactivate image is a 204
        """

        self.resp = self.images_admin.client.reactivate_image(self.image.id)
        self.assertEqual(204, self.resp.status_code)

    def test_create_server_from_reactivated_image(self):
        """
        Verify that a server can be created from a reactivated image

        Create a server using a reactivated image

        This test will be successful if:
            - The server status is active
        """

        server = self.compute.servers.behaviors.create_active_server(
            image_ref=self.image.id).entity
        self.resources.add(
            server.id, self.servers_client.delete_server)
        self.assertEqual(server.image.id, self.image.id)
