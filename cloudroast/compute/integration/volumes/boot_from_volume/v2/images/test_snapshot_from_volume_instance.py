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

from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.types import NovaImageStatusTypes

from cloudroast.compute.instance_actions.api.test_create_image \
    import CreateImageTest
from cloudroast.compute.fixtures import ServerFromVolumeV2Fixture


class ServerFromVolumeV2CreateImageTests(ServerFromVolumeV2Fixture,
                                         CreateImageTest):

    @classmethod
    def setUpClass(cls):
        super(ServerFromVolumeV2CreateImageTests, cls).setUpClass()
        cls.create_server()
        cls.image_name = rand_name('image')
        cls.metadata = {'user_key1': 'value1',
                        'user_key2': 'value2'}
        server_id = cls.server.id
        cls.image_response = cls.servers_client.create_image(
            server_id, cls.image_name, metadata=cls.metadata)
        cls.image_id = cls.parse_image_id(cls.image_response)
        cls.resources.add(cls.image_id, cls.images_client.delete_image)
        cls.image_behaviors.wait_for_image_status(
            cls.image_id, NovaImageStatusTypes.ACTIVE)
        cls.image = cls.images_client.get_image(cls.image_id).entity
