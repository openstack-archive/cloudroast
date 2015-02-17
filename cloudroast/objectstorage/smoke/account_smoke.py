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
from cafe.engine.http.client import HTTPClient
from cloudroast.objectstorage.fixtures import ObjectStorageFixture

STATUS_CODE_MSG = ("{method} expected status code {expected}"
                   " recieved status code {recieved}")
CONTAINER_NAME = 'account_smoke_test_container'
C_TYPE_TEXT = 'text/plain; charset=utf-8'
C_TYPE_JSON = 'application/json; charset=utf-8'
C_TYPE_XML = 'application/xml; charset=utf-8'
HTTP_OK = 200


class AccountSmokeTest(ObjectStorageFixture):
    @classmethod
    def setUpClass(cls):
        super(AccountSmokeTest, cls).setUpClass()

        cls.container_names = ['a_{0}'.format(CONTAINER_NAME),
                               'b_{0}'.format(CONTAINER_NAME),
                               'c_{0}'.format(CONTAINER_NAME)]

        for container_name in cls.container_names:
            cls.client.create_container(container_name)

    @classmethod
    def tearDownClass(cls):
        super(AccountSmokeTest, cls).setUpClass()
        for container_name in cls.container_names:
            cls.behaviors.force_delete_containers([container_name])

    def test_container_list(self):
        response = self.client.list_containers()

        method = "list containers"
        expected = HTTP_OK
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        expected = C_TYPE_TEXT
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'x-account-object-count' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_container_list_with_format_json_query_parameter(self):
        format_ = {"format": "json"}
        response = self.client.list_containers(params=format_)

        method = "list containers using content-type json"
        expected = HTTP_OK
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        expected = C_TYPE_JSON
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'x-account-object-count' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_container_list_with_format_xml_query_parameter(self):
        format_ = {"format": "xml"}
        response = self.client.list_containers(params=format_)

        method = "list containers using content-type xml"
        expected = HTTP_OK
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        expected = C_TYPE_XML
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'x-account-object-count' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_container_list_with_accept_header(self):
        headers = {"Accept": "*/*"}
        response = self.client.list_containers(headers=headers)

        method = "list containers using accept */*"
        expected = HTTP_OK
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        expected = C_TYPE_TEXT
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'x-account-object-count' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_container_list_with_text_accept_header(self):
        headers = {"Accept": "text/plain"}
        response = self.client.list_containers(headers=headers)

        method = "list containers using accept text/plain"
        expected = HTTP_OK
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        expected = C_TYPE_TEXT
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'x-account-object-count' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_container_list_with_json_accept_header(self):
        headers = {"Accept": "application/json"}
        response = self.client.list_containers(headers=headers)

        method = "list containers using accept application/json"
        expected = HTTP_OK
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        expected = C_TYPE_JSON
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'x-account-object-count' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_container_list_with_xml_accept_header(self):
        headers = {"Accept": "application/xml"}
        response = self.client.list_containers(headers=headers)

        method = "list containers using accept application/xml"
        expected = HTTP_OK
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        expected = C_TYPE_XML
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'x-account-object-count' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_container_list_with_limit_query_parameter(self):
        limit = {"limit": "10"}
        response = self.client.list_containers(params=limit)

        method = "list containers using limit query parameter"
        expected = HTTP_OK
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        expected = C_TYPE_TEXT
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'x-account-object-count' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_container_list_with_marker_query_parameter(self):
        marker = {"marker": "a"}
        response = self.client.list_containers(params=marker)

        method = "list containers using marker query parameter"
        expected = HTTP_OK
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        expected = C_TYPE_TEXT
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'x-account-object-count' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_container_list_with_limit_and_marker_query_parameters(self):
        limit_marker = {"limit": "3", "marker": "a"}
        response = self.client.list_containers(params=limit_marker)

        method = "list containers using limit and marker query parameters"
        expected = HTTP_OK
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        expected = C_TYPE_TEXT
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'x-account-object-count' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_container_list_with_limit_marker_format_json(self):
        limit_marker_format = {"limit": "3", "marker": "a", "format": "json"}
        response = self.client.list_containers(params=limit_marker_format)

        method = "list containers using limit, marker, and format json query" \
            " parameters"
        expected = HTTP_OK
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        expected = C_TYPE_JSON
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'x-account-object-count' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_container_list_with_limit_marker_format_xml(self):
        limit_marker_format = {"limit": "3", "marker": "a", "format": "xml"}
        response = self.client.list_containers(params=limit_marker_format)

        method = "list containers using limit, marker, and format xml query" \
            " parameters"
        expected = HTTP_OK
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        expected = C_TYPE_XML
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'x-account-object-count' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_metadata_retrieval_with_existing_account(self):
        response = self.client.retrieve_account_metadata()

        method = "account metadata retrieval"
        expected = 204
        recieved = response.status_code

        self.assertEqual(
            expected,
            recieved,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                recieved=str(recieved)))

        self.assertIn('x-account-bytes-used', response.headers)

        self.assertIn('date', response.headers)

        self.assertIn('x-timestamp', response.headers)

        self.assertIn('x-account-container-count', response.headers)

        self.assertIn('x-account-object-count', response.headers)

        expected = 'bytes'
        recieved = response.headers.get('accept-ranges')
        self.assertEqual(
            expected,
            recieved,
            msg="'accept-ranges' header value expected: {0} recieved"
            " {1}".format(expected, recieved))

        expected = 0
        recieved = int(response.headers.get('content-length'))
        self.assertEqual(
            expected,
            recieved,
            msg="'content-length' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

        expected = C_TYPE_TEXT
        recieved = response.headers.get('content-type')
        self.assertEqual(
            expected,
            recieved,
            msg="'content-type' header value expected: {0} recieved:"
            " {1}".format(expected, recieved))

    def test_list_containers_with_alt_url_version(self):
        """
        Scenario:
            Attempt to list containers on an account using 'v1.0' instead of
            the standard 'v1' in the storage url.
            Attempt to list containers on an account using 'v1.' instead of
            the standard 'v1' in the storage url.

        Expected Results:
            For both cases, should receive a response of 200.
        """
        dumb_client = HTTPClient()
        token = self.client.auth_token

        modified_url = self.storage_url.replace('/v1/', '/v1.0/')
        headers = {'X-AUTH-TOKEN': token}
        list_response = dumb_client.request('GET',
                                            modified_url,
                                            headers=headers)

        method = "Account List Containers with 'v1.0' in URL"
        expected = 200
        received = list_response.status_code

        self.assertEqual(expected,
                         received,
                         msg=STATUS_CODE_MSG.format(
                             method=method,
                             expected=expected,
                             recieved=str(received)))

        modified_url = self.storage_url.replace('/v1/', '/v1./')
        list_response = dumb_client.request('GET',
                                            modified_url,
                                            headers=headers)

        method = "Account List Containers with 'v1.' in URL"
        expected = 200
        received = list_response.status_code

        self.assertEqual(expected,
                         received,
                         msg=STATUS_CODE_MSG.format(
                             method=method,
                             expected=expected,
                             recieved=str(received)))
