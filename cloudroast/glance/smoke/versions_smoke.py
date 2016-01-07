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

from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cloudcafe.glance.common.constants import Messages

from cloudroast.glance.fixtures import ImagesFixture
from cloudroast.glance.generators import ImagesDatasetListGenerator


@DataDrivenFixture
class VersionsSmoke(ImagesFixture):

    @data_driven_test(ImagesDatasetListGenerator.Versions())
    def ddtest_list_versions(self, url_addition):
        """
        @summary: List all versions

        @param url_addition: Paremter being passed to the list versions request
        @type url_addition: Dictonary

        1) List all versions passing in each url addition
        2) If versions is in the url, verify that the response code is 200
        3) If versions is not in the url, verify that the response code is 300
        """

        resp = self.images.client.list_versions(url_addition)
        if 'versions' in url_addition:
            self.assertEqual(
                resp.status_code, 200,
                Messages.STATUS_CODE_MSG.format(200, resp.status_code))
        else:
            self.assertEqual(
                resp.status_code, 300,
                Messages.STATUS_CODE_MSG.format(300, resp.status_code))
