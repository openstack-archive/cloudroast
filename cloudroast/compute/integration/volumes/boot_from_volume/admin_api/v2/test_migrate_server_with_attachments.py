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
import logging

from cafe.drivers.unittest.decorators import tags

from cloudcafe.blockstorage.volumes_api.common.models import statuses as \
    volume_statuses
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import NovaServerStatusTypes
from cloudcafe.compute.composites import ComputeAdminComposite

from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture


class ServerFromVolumeWithAttachmentsMigrateTests(ServerFromVolumeV2Fixture):

    @classmethod
    def setUpClass(cls):
        """ Create and migrate a server from volume with multiple attachments

        The following resources are created during this setup:
            - Create an active server.
        """
        super(ServerFromVolumeWithAttachmentsMigrateTests, cls).setUpClass()

        cls.create_server()

        # The base class create_server method adds the server resource to the
        # resources pool by default which will provide attempt to delete the
        # server during class tear down. This resource pool check will attempt
        # to confirm that the server is deleted prior to the resource pool
        # attempting deleting the other resources created below.
        cls.resources.add(cls.server.id, cls.confirm_server_deleted)

        num_volumes_to_attach = 2
        cls.attached_volumes = list()

        for i in range(num_volumes_to_attach):
            # Create a volume
            volume = cls.compute_integration.volumes.behaviors.\
                create_available_volume(
                    cls.compute_integration.volumes.config.
                    default_volume_type_min_size,
                    cls.compute_integration.volumes.config.default_volume_type,
                    rand_name('live_migrate_volume'))
            cls.resources.add(volume.id_, cls.delete_volume)
            cls.compute_integration.volume_attachments.behaviors.\
                attach_volume_to_server(cls.server.id, volume.id_)
            cls.attached_volumes.append(volume)

        # Migrate and wait for ACTIVE status
        compute_admin = ComputeAdminComposite()
        compute_admin.servers.client.migrate_server(cls.server.id)
        compute_admin.servers.behaviors.wait_for_server_status(
            cls.server.id, NovaServerStatusTypes.VERIFY_RESIZE)
        compute_admin.servers.client.confirm_resize(cls.server.id)
        compute_admin.servers.behaviors.wait_for_server_status(
            cls.server.id, NovaServerStatusTypes.ACTIVE)
        # Allow the server additional time to complete the migration processes
        # prior to performing tests
        time.sleep(30)

    @classmethod
    def confirm_server_deleted(cls, server_id):
        """ Confirm the server resource has been deleted

            This method will attempt to confirm the server resource created
            during setup has been deleted. If confirmation fails or times out,
            the id of the server will be logged.

        Args:
           server_id: The id of the server that would have been deleted.

        Returns:
            None
        """
        try:
            cls.compute.servers.behaviors.\
                confirm_server_deletion(server_id=server_id,
                                        response_code=404)
        except Exception as e:
            cls.fixture_log.log(logging.WARNING, str(e))

    @classmethod
    def delete_volume(cls, volume_id):
        """ Delete the volumes created during setup

            This method will attempt to detach and delete all volumes created
            and attached during setup.  If a either detaching or deleting fails
            or times out without being confirmed, the id of the volume will be
            logged.

        Args:
            volume_id: The id of the volume being deleted

        Returns:
            None
        """

        if volume_id in [volume.id_ for volume in cls.attached_volumes]:
            try:
                cls.compute_integration.volume_attachments.behaviors.\
                    delete_volume_attachment(volume_id, cls.server.id)
            except Exception as e:
                cls.fixture_log.log(logging.WARNING, str(e))

        if not cls.compute_integration.volumes.behaviors.\
                delete_volume_confirmed(volume_id):
            cls.fixture_log.log(logging.WARNING,
                                "Volume {0} either was not deleted during "
                                "clean up procedures or the confirm "
                                "deletion operation timed out.".
                                format(volume_id))

    @tags(type='smoke', net='yes')
    def test_server_volumes_attached(self):
        """ Test that a servers attached volumes have the status of "in-use"

            Get the details of the volumes created and attached during the
            setup. Validate that the status of the volume is 'in-use'.

            The following assertions occur:
                - The status of all of the volumes created and attached
                  during setup have a status of 'in-use'
        """
        volumes_not_attached = list()
        for volume in self.attached_volumes:
            volume_after_migration = self.compute_integration.volumes.\
                behaviors.get_volume_info(volume.id_)
            if volume_after_migration.status != volume_statuses.Volume.IN_USE:
                volumes_not_attached.append(volume_after_migration)

        self.assertEqual(len(volumes_not_attached), 0,
                         msg="One or more volume attachments were not "
                             "attached to the server with id {0}. Unattached "
                             "Volumes: {1}".format(
                             self.server.id, volumes_not_attached))
