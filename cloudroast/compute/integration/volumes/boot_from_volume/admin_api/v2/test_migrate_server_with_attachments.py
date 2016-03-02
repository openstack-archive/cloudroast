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
import time

from cloudcafe.blockstorage.volumes_api.v1.models import statuses \
    as volume_statuses
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.composites import ComputeAdminComposite
from cloudcafe.compute.common.types import NovaServerStatusTypes

from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture
from cloudroast.compute.integration.volumes.boot_from_volume.admin_api \
    .test_server_attachments import ServerAttachmentsTests


class ServerFromVolumeWithAttachmentsMigrateTests(
        ServerFromVolumeV2Fixture, ServerAttachmentsTests):

    @classmethod
    def setUpClass(cls):
        """ Create and migrate a server from volume with multiple attachments

        The following resources are created during this setup:
            - Create an active server.
        """
        super(ServerFromVolumeWithAttachmentsMigrateTests, cls).setUpClass()

        cls.create_server()

        num_volumes_to_attach = 2
        cls.attached_volumes = list()

        cls.volumes = cls.compute_integration.volumes

        for i in range(0, num_volumes_to_attach):
            # Create a volume
            volume = cls.volumes.behaviors.create_available_volume(
                cls.volumes.config.min_volume_size,
                cls.volumes.config.default_volume_type,
                rand_name('live_migrate_volume'))
            cls.resources.add(volume.id_, cls.volumes.client.delete_volume)
            cls.volume_attachments_client.attach_volume(
                cls.server.id, volume.id_)
            cls.volumes.behaviors.wait_for_volume_status(
                volume.id_, volume_statuses.Volume.IN_USE,
                cls.volumes.config.volume_create_max_timeout)
            cls.attached_volumes.append(volume)

        # Migrate and wait for ACTIVE status
        compute_admin = ComputeAdminComposite()

        compute_admin.servers.client.migrate_server(cls.server.id)
        compute_admin.servers.behaviors.wait_for_server_status(
            cls.server.id, NovaServerStatusTypes.VERIFY_RESIZE)
        compute_admin.servers.client.confirm_resize(cls.server.id)

        compute_admin.servers.behaviors.wait_for_server_status(
            cls.server.id, NovaServerStatusTypes.ACTIVE)
        time.sleep(30)
