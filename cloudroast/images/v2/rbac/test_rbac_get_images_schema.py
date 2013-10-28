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


class RbacGetImagesSchemaTest(ImagesV2Fixture):

    @tags(type='positive')
    def test_get_images_schema_observer(self):
        """Get images schema as observer.

        1) Get images schema as a user with the observer role
        2) Verify the response status code is 200
        """

        self.assertTrue(False, 'Not Implemented')
