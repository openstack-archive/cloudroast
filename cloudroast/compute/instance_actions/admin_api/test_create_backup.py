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

import unittest

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import BackupTypes

from cloudroast.compute.fixtures import ComputeAdminFixture


@unittest.skip("Feature not available.")
class CreateBackupTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the necessary resources for testing

        The following resources are accessed from a parent class:
            - An instance from ComputeAdminFixture

        The following resources are created during this setup:
            - A server with defaults defined in server behaviors
        """
        super(CreateBackupTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @tags(type='smoke', net='no')
    def test_create_backup_for_server(self):
        """
        Verify that a backup can be created from a server

        Creates an active backup of the server with parameters of Daily backup
        and keep 1 backup only.

        This test will be successful if:
            - The call to create the back returns an entity
        """

        image_response = self.admin_images_behaviors.create_active_backup(
            self.server.id, BackupTypes.DAILY, "1")
        image = image_response.entity
        self.resources.add(
            image.id, self.admin_images_client.delete_image(image.id))
