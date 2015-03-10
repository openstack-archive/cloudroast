"""
Copyright 2015 Rackspace

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

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)

from cloudroast.glance.fixtures import ImagesFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator


@DataDrivenFixture
class ListVersions(ImagesFixture):

    @data_driven_test(ImagesDatasetListGenerator.Versions())
    def ddtest_list_versions(self, url_addition):
        """
        @summary: List all versions

        @param url_addition: Paremter being passed to the list versions request
        @type url_addition: Dictonary

        1) Retrieve the versions data file
        2) List all versions passing in each url addition
        3) Verify that the response code is 300
        4) Verify that the number of versions received matches the number of
        versions in the versions data file
        5) For each version returned, verify that the data matches the
        versions data file
        """

        errors = []

        versions_data = self.images.behaviors.get_comparison_data(
            self.images.config.versions_data)

        resp = self.images.client.list_versions(url_addition)
        self.assertEqual(resp.status_code, 300,
                         self.status_code_msg.format(300, resp.status_code))
        listed_versions = resp.entity

        self.assertEqual(len(listed_versions), len(versions_data))

        for version in listed_versions:
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

        # Allows the full error list to be returned if it is larger than normal
        self.assertEqual.im_class.maxDiff = None

        self.assertListEqual(
            errors, [], msg=('Unexpected errors received. Expected: No errors '
                             'Received: {0}').format(errors))
