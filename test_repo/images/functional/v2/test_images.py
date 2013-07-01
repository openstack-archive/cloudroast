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
from test_repo.images.fixtures import ImageV2Fixture


class CreateRegisterImagesTest(ImageV2Fixture):
    """
        Test registration and creation of images.
    """

    @tags(type='negative', net='no')
    def test_register_with_invalid_container_format(self):
        response = self.api_client.create_image(
            name='test',
            container_format='wrong',
            disk_format='vhd')

        self.assertEqual(400, response.status_code)
