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
from cloudroast.objectstorage.fixtures import ObjectStorageFixture


class AccountSmokeTest(ObjectStorageFixture):

    """4.1.1. List Containers"""
    def test_container_list_with_non_empty_account(self):
        response = self.client.list_containers()

        self.assertEqual(
            response.status_code,
            200,
            'should list containers')

    """4.1.1.1. Serialized List Output"""
    def test_container_list_with_format_json_query_parameter(self):
        format_ = {'format': 'json'}
        response = self.client.list_containers(params=format_)

        self.assertEqual(
            response.status_code,
            200,
            'should list containers using content-type json')

    def test_container_list_with_format_xml_query_parameter(self):
        format_ = {'format': 'xml'}
        response = self.client.list_containers(params=format_)

        self.assertEqual(
            response.status_code,
            200,
            'should list containers using content-type xml')

    def test_container_list_with_accept_header(self):
        headers = {'Accept': '*/*'}
        response = self.client.list_containers(headers=headers)

        self.assertEqual(
            response.status_code,
            200,
            'should list containers using content-type text/plain')

    def test_container_list_with_text_accept_header(self):
        headers = {'Accept': 'text/plain'}
        response = self.client.list_containers(headers=headers)

        self.assertEqual(
            response.status_code,
            200,
            'should list containers using content-type text/plain')

    def test_container_list_with_json_accept_header(self):
        headers = {'Accept': 'application/json'}
        response = self.client.list_containers(headers=headers)

        self.assertEqual(
            response.status_code,
            200,
            'should list containers using content-type application/json')

    def test_container_list_with_xml_accept_header(self):
        headers = {'Accept': 'application/xml'}
        response = self.client.list_containers(headers=headers)

        self.assertEqual(
            response.status_code,
            200,
            'should list containers using content-type application/xml')

        headers = {'Accept': 'text/xml'}
        response = self.client.list_containers(headers=headers)

        self.assertEqual(
            response.status_code,
            200,
            'should list containers using content-type text/xml')

    """4.1.1.2. Controlling a Large List of Containers"""
    def test_container_list_with_limit_query_parameter(self):
        limit = {'limit': '10'}
        response = self.client.list_containers(params=limit)

        self.assertEqual(
            response.status_code,
            200,
            'should list containers')

    def test_container_list_with_marker_query_parameter(self):
        marker = {'marker': 'a'}
        response = self.client.list_containers(params=marker)

        self.assertEqual(
            response.status_code,
            200,
            'should list containers')

    def test_container_list_with_limit_and_marker_query_parameters(self):
        limit_marker = {'limit': '3', 'marker': 'a'}
        response = self.client.list_containers(params=limit_marker)

        self.assertEqual(
            response.status_code,
            200,
            'should list containers')

    def test_container_list_with_limit_marker_format_json(self):
        limit_marker_format = {'limit': '3', 'marker': 'a', 'format': 'json'}
        response = self.client.list_containers(params=limit_marker_format)

        self.assertEqual(
            response.status_code,
            200,
            'should list containers')

    def test_container_list_with_limit_marker_format_xml(self):
        limit_marker_format = {'limit': '3', 'marker': 'a', 'format': 'xml'}
        response = self.client.list_containers(params=limit_marker_format)

        self.assertEqual(
            response.status_code,
            200,
            'should list containers')

    """4.1.2. Retrieve Account Metadata"""
    def test_metadata_retrieval_with_existing_account(self):
        response = self.client.retrieve_account_metadata()

        self.assertEqual(
            response.status_code,
            204,
            'should return metadata')
