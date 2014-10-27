"""
Copyright 2014 Rackspace

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
from cloudroast.images.fixtures import ImagesFixture


class TestGetVersions(ImagesFixture):

    @tags(type='smoke')
    def test_get_versions(self):
        """
        @summary: Get all versions of using each possible url

        1) Get versions of Cloud Images using each url
        2) Verify that the response code is 300
        3) Verify that the number of versions returned is as expected
        4) Verify that each version returned contains the correct parameters
        and values
        """

        url_additions = ['', '/', '/versions', '/versions/']

        for url_addition in url_additions:

            response = self.images_client.get_versions(url_addition)
            self.assertEqual(response.status_code, 300)
            versions = response.entity

            self.assertEqual(len(versions), len(self.versions))

            for version in versions:
                version_data = self.versions[version.id_]

                self.assertEqual(version.links[0].href,
                                 version_data.get('href'))
                self.assertEqual(version.links[0].rel, version_data.get('rel'))
                self.assertEqual(version.status.lower(),
                                 version_data.get('status').lower())
