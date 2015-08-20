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
    suite.addTest(ServerIntegration(
        "test_deactivated_image"))
    suite.addTest(ServerIntegration(
        "test_can_create_server_from_deactivated_image"))
    suite.addTest(ServerIntegration(
        "test_reactivate_image"))
    suite.addTest(ServerIntegration(
        "test_can_create_server_from_reactivated_image"))
    return suite


class ServerIntegration(ImagesIntegrationFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing.

        The following resources are created during this setup:
            - A server with defaults defined in server behaviors
            - An image from the newly created server
        """
        super(ServerIntegration, cls).setUpClass()
        cls.server = (
            cls.compute.servers.behaviors.create_active_server().entity)
        cls.image = cls.compute.images.behaviors.create_active_image(
            cls.server.id).entity
        cls.resources.add(
            cls.server.id, cls.compute.servers.client.delete_server)
        cls.resources.add(cls.image.id, cls.images_client.delete_image)

    def test_deactivated_image(self):
        """
        Verify that a V1 image can be deactivated

        Execute deactivate API call on pre-created snapshot from cloud server

        This test will be successful if:
            - Received response code is valid 204
            """
        self.resp = self.images_admin.client.deactivate_image(self.image.id)
        self.assertEqual(204, self.resp.status_code)

    def test_create_server_from_deactivated_image(self):
        """
        Verify that a instance can not be build from deactivated image

        Execute create_server client call with deactivated image

        This test will be successful if:
            - Received response code is 400 Bad Request
        """
        resp = self.compute.servers.client.create_server(
            name=rand_name("server"),
            flavor_ref=self.flavor_ref,
            image_ref=self.image.id)
        self.assertEqual(400, resp.status_code)

    def test_reactivate_image(self):
        """
        Verify that a V1 image can be reactivated

        Execute reactivate API call on pre-created and deactivated
        snapshot from cloud server

        This test will be successful if:
            - Received response code is valid 204
        """
        self.resp = self.images_admin.client.reactivate_image(self.image.id)
        self.assertEqual(204, self.resp.status_code)

    def test_create_server_from_reactivated_image(self):
        """
        Verify that a instance can be build from reactivated image

        Execute create_active_server behavior call with reactivated image

        This test will be successful if:
            - The Active Server had same image id as reactivated one
        """
        server = self.compute.servers.behaviors.create_active_server(
            image_ref=self.image.id).entity
        self.resources.add(
            server.id, self.servers_client.delete_server)
        self.assertEqual(server.image.id, self.image.id)
