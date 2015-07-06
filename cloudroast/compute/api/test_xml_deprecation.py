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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name
from cloudcafe.compute.common.exceptions import BadRequest
from cloudcafe.compute.common.types import NovaServerStatusTypes

from cloudroast.compute.fixtures import ComputeFixture


class XMLDeprecationTest(ComputeFixture):

    @classmethod
    def tearDownClass(cls):
        """
        Perform actions that allow for the reset of the clients

        The following clients' headers reset during this tear down:
            - The flavors client
            - The servers client
        """

        super(XMLDeprecationTest, cls).tearDownClass()
        cls.flavors_client.default_headers['Accept'] = 'application/json'
        cls.flavors_client.default_headers['Content-Type'] = 'application/json'
        cls.servers_client.default_headers['Accept'] = 'application/json'
        cls.servers_client.default_headers['Content-Type'] = 'application/json'

    @tags(type='smoke', net='no')
    def test_get_request_accept_xml_ignored(self):
        """
        A GET request passing only the accept header as xml is ignored

        Request a list of available flavors passing only the accept header as
        xml and ensure that the header is ignored returning a valid json
        response.

        The following assertions occur:
            - The response content does not contain xml content
        """

        response_content = self._get_xml_response(accept='xml')
        self.assertNotIn('xml version', response_content,
                         'Unexpected xml content was found in the response')

    @tags(type='smoke', net='no')
    def test_get_request_content_type_xml_ignored(self):
        """
        A GET request passing only the content-type header as xml is ignored

        Request a list of available flavors passing only the content-type
        header as xml and ensure that the header is ignored returning a valid
        json response.

        The following assertions occur:
            - The response content does not contain xml content
        """

        response_content = self._get_xml_response(content_type='xml')
        self.assertNotIn('xml version', response_content,
                         'Unexpected xml content was found in the response')

    @tags(type='smoke', net='no')
    def test_get_request_accept_and_content_type_xml_ignored(self):
        """
        A GET request passing accept and content-type headers as xml is ignored

        Request a list of available flavors passing both the accept and
        content-type headers as xml and ensure that the headers are ignored
        returning a valid json response.

        The following assertions occur:
            - The response code is 200
            - The response content does not contain xml content
        """

        response_content = self._get_xml_response(
            accept='xml', content_type='xml')
        self.assertNotIn('xml version', response_content,
                         'Unexpected xml content was found in the response')

    @tags(type='smoke', net='no')
    def test_post_request_accept_xml_ignored(self):
        """
        A POST request passing only the accept header as xml is ignored

        Request a new server creation passing only the accept header as
        xml and ensure that the header is ignored returning a valid json
        response.

        The following assertions occur:
            - The response code is 202
            - The response content does not contain xml content
            - The server status is active
        """

        name = rand_name('testserver')
        self.servers_client.default_headers['Accept'] = 'application/xml'
        self.servers_client.default_headers['Content-Type'] = (
            'application/json')
        response = self.servers_client.create_server(
            name, self.image_ref, self.flavor_ref)
        self.assertEqual(response.status_code, 202,
                         'Unexpected status code returned. '
                         'Expected: {0} Received: '
                         '{1}'.format(202, response.status_code))
        content = response.content
        self.assertNotIn('xml version', content,
                         'Unexpected xml content was found in the response')
        server = response.entity
        self.resources.add(server.id, self.servers_client.delete_server)
        get_server = self.server_behaviors.wait_for_server_creation(server.id)
        self.assertEqual(get_server.status, NovaServerStatusTypes.ACTIVE,
                         'Unexpected server status returned. '
                         'Expected: {0} Received: '
                         '{1}'.format(NovaServerStatusTypes.ACTIVE,
                                      get_server.status))

    @tags(type='smoke', net='no')
    def test_post_request_content_type_xml_negative(self):
        """
        A POST request passing only the content-type header as xml returns 400

        Request a new server creation passing only the content-type header as
        xml and ensure that a bad request exception is returned.

        The following assertions occur:
            - The response code is 400
        """

        name = rand_name('testserver')
        self.servers_client.default_headers['Accept'] = 'application/json'
        self.servers_client.default_headers['Content-Type'] = 'application/xml'
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                name, self.image_ref, self.flavor_ref)

    @tags(type='smoke', net='no')
    def test_post_request_accept_and_content_type_xml_negative(self):
        """
        A POST passing accept and content-type headers as xml returns 400

        Request a new server creation passing both the accept and content-type
        headers as xml and ensure that a bad request exception is returned.

        The following assertions occur:
            - The response code is 400
        """

        name = rand_name('testserver')
        self.servers_client.default_headers['Accept'] = 'application/xml'
        self.servers_client.default_headers['Content-Type'] = 'application/xml'
        with self.assertRaises(BadRequest):
            self.servers_client.create_server(
                name, self.image_ref, self.flavor_ref)

    def _get_xml_response(self, accept='json', content_type='json'):
        """
        A GET request passing accept and content-type headers in given formats

        Request a list of available flavors passing the accept and content-type
        headers in the given formats and ensure that a response code of 200 is
        returned.

        The following assertions occur:
            - The response code is 200
        """

        if accept == 'xml':
            self.flavors_client.default_headers['Accept'] = 'application/xml'
        else:
            self.flavors_client.default_headers['Accept'] = 'application/json'
        if content_type == 'xml':
            self.flavors_client.default_headers['Content-Type'] = (
                'application/xml')
        else:
            self.flavors_client.default_headers['Content-Type'] = (
                'application/json')

        response = self.flavors_client.list_flavors()
        self.assertEqual(response.status_code, 200,
                         'Unexpected status code returned. '
                         'Expected: {0} Received: '
                         '{1}'.format(200, response.status_code))

        return response.content
