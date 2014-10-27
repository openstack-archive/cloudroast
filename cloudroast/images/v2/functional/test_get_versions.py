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

from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture, tags)
from cloudroast.images.fixtures import ImagesFixture


class VersionsDatasetList(DatasetList):
    def __init__(self):
        self.append_new_dataset('url_with_no_backslash', {'url_addition': ''})
        self.append_new_dataset('url_with_backslash', {'url_addition': '/'})
        self.append_new_dataset('url_with_versions_and_no_backslash',
                                {'url_addition': '/versions'})
        self.append_new_dataset('url_with_versions_and_backslash',
                                {'url_addition': '/versions/'})


@DataDrivenFixture
class TestGetVersions(ImagesFixture):

    @tags(type='smoke')
    @data_driven_test(VersionsDatasetList())
    def ddtest_get_versions(self, url_addition):
        """
        @summary: Get all versions of using each possible url

        1) Get versions of Cloud Images using each url
        2) Verify that the response code is 300
        3) Verify that the number of versions returned is as expected
        4) Verify that each version returned contains the correct parameters
        and values
        """

        versions_data = self.get_comparison_data(
            self.images_config.versions_data)
        errors = []

        response = self.images_client.get_versions(url_addition)
        self.assertEqual(response.status_code, 300)
        list_versions = response.entity

        self.assertEqual(len(list_versions), len(versions_data))

        for version in list_versions:
            version_data = versions_data[version.id_]

            if version.links[0].href != version_data.get('href'):
                errors.append(self.error_msg.format(
                    'href', version_data.get('href'), version.links[0].href))
            if version.links[0].rel != version_data.get('rel'):
                errors.append(self.error_msg.format(
                    'rel', version_data.get('rel'), version.links[0].rel))
            if version.status.lower() != version_data.get('status').lower():
                errors.append(self.error_msg.format(
                    'status', version_data.get('status').lower(),
                    version.status.lower()))

        self.assertListEqual(errors, [])
