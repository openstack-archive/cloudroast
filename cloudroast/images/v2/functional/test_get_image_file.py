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
import cStringIO as StringIO

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.constants import Messages

from cloudroast.images.v2.fixtures import ImagesV2Fixture

msg = Messages.ASSERT_MSG


class GetImageFileTest(ImagesV2Fixture):
    @tags(type='smoke')
    def test_download_image_data(self):
        """Downloads binary data for an image.

        1. Register new image
        2. Verify response code is 200
        3. Upload image with an image file
        4. Download binary image data
        5. Verify response code is 200
        6. Verify that the downloaded image data is same as uploaded binary
        image data
        """
        image_id = self.register_basic_image()
        image_data = StringIO.StringIO(('*' * 1024))
        response = self.api_client.store_raw_image_data(image_id,
                                                        image_data)
        self.assertEqual(response.status_code, 204,
                         msg.format('status_code', 204, response.status))

        response = self.api_client.get_image(image_id)
        self.assertEqual(response.status_code, 200,
                         msg.format('status_code', 200, response.status))
        self.assertEqual(response.entity.size, 1024)
        self.assertEqual(response.entity.file_,
                         "/v2/images/{0}/file".format(image_id))

    @tags(type='negative')
    def test_download_image_without_data(self):
        """Download binary data for an image that has none.

        1. Register new image
        2. Verify response code is 200
        4. Download binary image data
        5. Verify response code is 404
        """
        self.assertTrue(False, 'Not Implemented')

    @tags(type='negative')
    def test_download_image_data_with_invalid_id(self):
        """Download binary data using an invalid image id.

        1. Try download binary data using invalid image id
        2. Verify response code is 404
        """
        self.assertTrue(False, 'Not Implemented')

    @tags(type='negative')
    def test_download_image_data_with_blank_image_id(self):
        """Download binary data using a blank image id.

        1. Try download binary data using a blank image id
        2. Verify response code is 404
        """
        self.assertTrue(False, 'Not Implemented')
