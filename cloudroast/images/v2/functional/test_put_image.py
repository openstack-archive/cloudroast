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
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class PutImageTest(ImagesV2Fixture):

    @tags(type='smoke')
    def test_upload_image(self):
        """
        Register and upload new image.

        1. Register new image
        2. Update image with image file
        3. Verify response code is 204
        """

        self.assertTrue(False, "Not Yet Implemented")
