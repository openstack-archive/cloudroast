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
import json

from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudcafe.common.tools import randomstring as randstring

BASE_NAME = "extract_archive"
HTTP_OK = 200


class ExtractInvalidArchiveTest(ObjectStorageFixture):
    """
    Tests Swfit expand archive operations:
    """
    @classmethod
    def setUpClass(cls):
        super(ExtractInvalidArchiveTest, cls).setUpClass()
        cls.default_obj_name = cls.behaviors.VALID_OBJECT_NAME
        cls.storage_url = cls.client.storage_url
        cls.bad_data = "X" * 1000

    def get_members(self, keys, response_content):
        members = []
        content = None

        try:
            content = json.loads(response_content)
        except ValueError, error:
            self.fixture_log.exception(error)

        for current in content:
            for key in keys:
                if key in current.keys():
                    members.append(current[key])
                else:
                    continue

        return members

    def test_failure_reported_with_invalid_tar_archive(self):
        """
        Scenario: Verify behavior when an invalid archive file is uploaded

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(self.client.force_delete_containers, [container_name])

        url = "{0}/{1}".format(
            self.storage_url,
            container_name)
        params = {'extract-archive': 'tar'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            url,
            data=self.bad_data,
            params=params,
            headers=headers)

        expected = HTTP_OK
        recieved = response.status_code
        self.assertEqual(
            expected,
            recieved,
            "upload corrupted tar.gz expected"
            " successful status code: {0} recieved: {1}".format(
                expected,
                recieved))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = 0
        recieved = int(content.get('Number Files Created'))
        self.assertEqual(
            expected,
            recieved,
            msg="response body 'Number Files Created' expected: {0} recieved"
            "{1}".format(expected, recieved))

        expected = '400 Bad Request'
        recieved = content.get('Response Status')
        self.assertEqual(
            expected,
            recieved,
            msg="response body 'Response Status' expected: {0}"
            " recieved {1}".format(expected, recieved))

        expected = 0
        recieved = len(content.get('Errors'))
        self.assertEqual(
            expected,
            recieved,
            msg="response body 'Errors' expected None recieved {0}".format(
                content.get('Errors')))

        expected = 'Invalid Tar File: invalid header'
        recieved = content.get('Response Body')
        self.assertIn(
            expected,
            recieved,
            msg="response body 'Response Body' expected None recieved"
            " {0}".format(content.get('Response Body')))

        params = {'format': 'json'}
        response = self.client.list_objects(container_name, params=params)

        resp_obj_names = self.get_members(["name"], response.content)

        expected = 0
        recieved = len(resp_obj_names)
        self.assertEqual(
            expected,
            recieved,
            msg="container list expected: {0} objects."
            " recieved: {1} objects".format(expected, recieved))

    def test_failure_reported_with_invalid_tar_gz_archive(self):
        """
        Scenario: Verify behavior when an invalid archive file is uploaded

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(self.client.force_delete_containers, [container_name])

        url = "{0}/{1}".format(
            self.storage_url,
            container_name)
        params = {'extract-archive': 'tar.gz'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            url,
            data=self.bad_data,
            params=params,
            headers=headers)

        expected = HTTP_OK
        recieved = response.status_code
        self.assertEqual(
            expected,
            recieved,
            "upload corrupted tar.gz expected"
            " successful status code: {0} recieved: {1}".format(
                expected,
                recieved))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = 0
        recieved = int(content.get('Number Files Created'))
        self.assertEqual(
            expected,
            recieved,
            msg="response body 'Number Files Created' expected: {0} recieved"
            "{1}".format(expected, recieved))

        expected = '400 Bad Request'
        recieved = content.get('Response Status')
        self.assertEqual(
            expected,
            recieved,
            msg="response body 'Response Status' expected: {0}"
            " recieved {1}".format(expected, recieved))

        expected = 0
        recieved = len(content.get('Errors'))
        self.assertEqual(
            expected,
            recieved,
            msg="response body 'Errors' expected None recieved {0}".format(
                content.get('Errors')))

        expected = 'Invalid Tar File: not a gzip file'
        recieved = content.get('Response Body')
        self.assertIn(
            expected,
            recieved,
            msg="response body 'Response Body' expected None recieved"
            " {0}".format(content.get('Response Body')))

        params = {'format': 'json'}
        response = self.client.list_objects(container_name, params=params)

        resp_obj_names = self.get_members(["name"], response.content)

        expected = 0
        recieved = len(resp_obj_names)
        self.assertEqual(
            expected,
            recieved,
            msg="container list expected: {0} objects."
            " recieved: {1} objects".format(expected, recieved))

    def test_failure_reported_with_invalid_tar_bz2_archive(self):
        """
        Scenario: Verify behavior when an invalid archive file is uploaded

        Expected Results: Errors are reported. Objects are not created
        """
        container_name = '{0}_container_{1}'.format(
            BASE_NAME,
            randstring.get_random_string())

        self.behaviors.create_container(container_name)

        self.addCleanup(self.client.force_delete_containers, [container_name])

        url = "{0}/{1}".format(
            self.storage_url,
            container_name)
        params = {'extract-archive': 'tar.bz2'}
        headers = {'Accept': 'application/json'}
        response = self.client.put(
            url,
            data=self.bad_data,
            params=params,
            headers=headers)

        expected = HTTP_OK
        recieved = response.status_code
        self.assertEqual(
            expected,
            recieved,
            "upload corrupted tar.bz2 expected"
            " successful status code: {0} recieved: {1}".format(
                expected,
                recieved))

        # inspect the body of the response
        content = None

        try:
            content = json.loads(response.content)
        except ValueError, error:
            self.fixture_log.exception(error)

        expected = 0
        recieved = int(content.get('Number Files Created'))
        self.assertEqual(
            expected,
            recieved,
            msg="response body 'Number Files Created' expected: {0} recieved"
            " {1}".format(expected, recieved))

        expected = '400 Bad Request'
        recieved = content.get('Response Status')
        self.assertEqual(
            expected,
            recieved,
            msg="response body 'Response Status' expected: {0}"
            " recieved {1}".format(expected, recieved))

        expected = 0
        recieved = len(content.get('Errors'))
        self.assertEqual(
            expected,
            recieved,
            msg="response body 'Errors' expected None recieved {0}".format(
                content.get('Errors')))

        expected = 'Invalid Tar File: invalid compressed data'
        recieved = content.get('Response Body')
        self.assertIn(
            expected,
            recieved,
            msg="response body 'Response Body' expected None recieved"
            " {0}".format(content.get('Response Body')))

        params = {'format': 'json'}
        response = self.client.list_objects(container_name, params=params)

        resp_obj_names = self.get_members(["name"], response.content)

        expected = 0
        recieved = len(resp_obj_names)
        self.assertEqual(
            expected,
            recieved,
            msg="container list expected: {0} objects."
            " recieved: {1} objects".format(expected, recieved))
