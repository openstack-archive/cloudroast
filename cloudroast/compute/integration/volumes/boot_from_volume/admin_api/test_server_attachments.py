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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.blockstorage.volumes_api.v1.models import statuses as \
    volume_statuses


class ServerAttachmentsTests(object):
    """ Test volume attachments for a server

        This class is not intended to be instantiated and expects sub-classes
        to provide the following objects:
            1. server:
                A cloud server object
            2. attached_volumes:
                A list of volumes that are expected to be attached to the
                server.
            3. volumes:
                A composite providing access to a volumes api client
    """

    @tags(type='smoke', net='yes')
    def test_server_volumes_attached(self):
        """ Test that a servers attached volumes have the status of "in-use"

            Get the details of the volumes created and attached during the
            setup. Validate that the status of the volume is 'in-use'.

            The following assertions occur:
                - The status of the volume created and attached during setup
                  shows as 'in-use'
        """
        volumes_not_attached = list()
        for volume in self.attached_volumes:
            volume_after_migration = self.volumes.client.get_volume_info(
                volume.id_).entity
            if volume_after_migration.status != volume_statuses.Volume.IN_USE:
                volumes_not_attached.append(volume_after_migration)

        self.assertEqual(len(volumes_not_attached), 0,
                         msg="One or more volume attachments were not "
                             "attached to the server with id {0}. Unattached "
                             "Volumes: {1}".format(
                             self.server.id, volumes_not_attached))
