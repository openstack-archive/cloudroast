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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.types import BackupTypes
from cloudroast.compute.fixtures import ComputeAdminFixture


class CreateBackupTests(ComputeAdminFixture):

    @classmethod
    def setUpClass(cls):
        super(CreateBackupTests, cls).setUpClass()
        cls.server = cls.server_behaviors.create_active_server().entity
        cls.resources.add(cls.server.id, cls.servers_client.delete_server)

    @classmethod
    def tearDownClass(cls):
        super(CreateBackupTests, cls).tearDownClass()

    def test_create_backup_for_server(self):
        image_response = self.admin_images_behaviors.\
            create_active_backup(self.server.id,
                                 BackupTypes.DAILY, "1")
        image = image_response.entity
        self.resources.add(
            image.id, self.admin_images_client.delete_image(image.id))
