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
from cafe.drivers.unittest.decorators import (
    DataDrivenFixture, data_driven_test)
from cafe.engine.http.client import HTTPClient
from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudroast.objectstorage.generators import ObjectDatasetList

CONTAINER_DESCRIPTOR = 'cors_container'


@DataDrivenFixture
class CORSTest(ObjectStorageFixture):

    @classmethod
    def setUpClass(cls):
        super(CORSTest, cls).setUpClass()

        cls.dumb_client = HTTPClient()
        cls.object_name = cls.behaviors.VALID_OBJECT_NAME

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('tempurl')
    def ddtest_container_cors_with_tempurl(self, generate_object):
        """
        Scenario:
            Create a container with CORS headers.
            Create a object.
            Retrieve the object via TempURL.

        Expected Results:
            If no Origin is set:
                The object should be returned with no CORS headers.
            If the Origin matches the Allow-Origin set:
                The object should be returned with the CORS headers.
            If strict_cors_mode == True and the Origin does not match:
                The object should be returned with no CORS headers.
            If strict_cors_mode == False and the Origin does not match:
                The object should be returned with the CORS headers.
        """
        expose_headers = ['Content-Length', 'Etag', 'X-Timestamp',
                          'X-Trans-Id']
        container_headers = {
            'X-Container-Meta-Access-Control-Allow-Origin':
            'http://example.com',
            'X-Container-Meta-Access-Control-Max-Age': '5',
            'X-Container-Meta-Access-Control-Expose-Headers':
            ','.join(expose_headers)}

        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR, headers=container_headers)

        object_headers = {'Content-Type': 'text/plain'}
        generate_object(container_name,
                        self.object_name,
                        headers=object_headers)

        tempurl_key = self.behaviors.get_tempurl_key()
        tempurl_info = self.client.create_temp_url(
            'GET', container_name, self.object_name, 900, tempurl_key)

        # Requests with no Origin should not return CORS headers.
        response = self.dumb_client.request(
            'GET', tempurl_info.get('target_url'), params={
                'temp_url_sig': tempurl_info.get('signature'),
                'temp_url_expires': tempurl_info.get('expires')})
        self.assertTrue(
            'Access-Control-Allow-Origin' not in response.headers,
            'Allow-Origin header should not be returned.')
        self.assertTrue('Access-Control-Max-Age' not in response.headers,
                        'Max-Age should not be returned.')
        self.assertTrue(
            'Access-Control-Expose-Headers' not in response.headers,
            'Expose-Headers should not be returned.')

        # Requests with Origin which matches, should return CORS headers.
        response = self.dumb_client.request(
            'GET', tempurl_info.get('target_url'), params={
                'temp_url_sig': tempurl_info.get('signature'),
                'temp_url_expires': tempurl_info.get('expires')},
            headers={'Origin': 'http://example.com'})
        self.assertTrue(
            'Access-Control-Allow-Origin' in response.headers,
            'Allow-Origin header should be returned.')
        self.assertTrue(
            'Access-Control-Expose-Headers' in response.headers,
            'Expose-Headers should be returned.')
        self.assertTrue('Access-Control-Max-Age' not in response.headers,
                        'Max-Age should not be returned.')

        if self.objectstorage_api_config.strict_cors_mode:
            # CORS should work according to the spec.
            # Requests with Origin which does not match, should not return
            # CORS headers.
            response = self.dumb_client.request(
                'GET', tempurl_info.get('target_url'), params={
                    'temp_url_sig': tempurl_info.get('signature'),
                    'temp_url_expires': tempurl_info.get('expires')},
                headers={'Origin': 'http://foo.com'})
            self.assertTrue(
                'Access-Control-Allow-Origin' not in response.headers,
                'Allow-Origin header should not be returned.')
            self.assertTrue(
                'Access-Control-Expose-Headers' not in response.headers,
                'Expose-Headers should not be returned.')
            self.assertTrue('Access-Control-Max-Age' not in response.headers,
                            'Max-Age should not be returned.')
        else:
            # Early implementation of CORS.
            # Requests with Origin which does not match, should not return
            # CORS headers.
            response = self.dumb_client.request(
                'GET', tempurl_info.get('target_url'), params={
                    'temp_url_sig': tempurl_info.get('signature'),
                    'temp_url_expires': tempurl_info.get('expires')},
                headers={'Origin': 'http://foo.com'})
            self.assertTrue(
                'Access-Control-Allow-Origin' in response.headers,
                'Allow-Origin header should be returned with '
                'differing origin.')
            self.assertTrue(
                'Access-Control-Expose-Headers' in response.headers,
                'Expose-Headers should be returned with '
                'differing origin.')
            self.assertTrue('Access-Control-Max-Age' not in response.headers,
                            'Max-Age should not be returned with '
                            'differing origin.')

    @ObjectStorageFixture.required_features('formpost')
    def test_container_cors_with_formpost(self):
        """
        Scenario:
            Create a container with CORS headers.
            POST an object to the container via FormPOST.

        Expected Results:
            If no Origin is set:
                The response should be returned with no CORS headers.
            If the Origin matches the Allow-Origin set:
                The response should be returned with the CORS headers.
            If strict_cors_mode == True and the Origin does not match:
                The response should be returned with no CORS headers.
            If strict_cors_mode == False and the Origin does not match:
                The response should be returned with the CORS headers.
        """
        expose_headers = ['Content-Length', 'Etag', 'X-Timestamp',
                          'X-Trans-Id']
        container_headers = {
            'X-Container-Meta-Access-Control-Allow-Origin':
            'http://example.com',
            'X-Container-Meta-Access-Control-Max-Age': '5',
            'X-Container-Meta-Access-Control-Expose-Headers':
            ','.join(expose_headers)}
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR, headers=container_headers)

        tempurl_key = self.behaviors.get_tempurl_key()
        files = [{'name': 'foo1'}]

        # Requests with no Origin should not return CORS headers.
        formpost_info = self.client.create_formpost(
            container_name, files, key=tempurl_key)

        headers = formpost_info.get('headers')
        response = self.dumb_client.post(
            formpost_info.get('target_url'),
            headers=headers,
            data=formpost_info.get('body'),
            requestslib_kwargs={'allow_redirects': False})
        self.assertTrue(303, response.status_code)
        self.assertTrue('location' in response.headers)
        self.assertTrue('access-control-expose-headers' not in
                        response.headers)
        self.assertTrue('access-control-allow-origin' not in response.headers)

        # Requests with Origin which does match, should return CORS headers.
        formpost_info = self.client.create_formpost(
            container_name, files, key=tempurl_key)

        headers = formpost_info.get('headers')
        headers['Origin'] = 'http://example.com'
        response = self.dumb_client.post(
            formpost_info.get('target_url'),
            headers=headers,
            data=formpost_info.get('body'),
            requestslib_kwargs={'allow_redirects': False})
        self.assertTrue(303, response.status_code)
        self.assertTrue('access-control-expose-headers' in response.headers)
        self.assertTrue('location' in response.headers)
        self.assertTrue('access-control-allow-origin' in response.headers)

        if self.objectstorage_api_config.strict_cors_mode:
            # CORS should work according to the spec.
            # Requests with Origin which does not match, should not return
            # CORS headers.
            formpost_info = self.client.create_formpost(
                container_name, files, key=tempurl_key)

            headers = formpost_info.get('headers')
            headers['Origin'] = 'http://foo.com'
            response = self.dumb_client.post(
                formpost_info.get('target_url'),
                headers=headers,
                data=formpost_info.get('body'),
                requestslib_kwargs={'allow_redirects': False})
            self.assertTrue(303, response.status_code)
            self.assertTrue('access-control-expose-headers' not in
                            response.headers)
            self.assertTrue('location' not in response.headers)
            self.assertTrue('access-control-allow-origin' not in
                            response.headers)
        else:
            # Early implementation of CORS.
            # Requests with Origin which does not match, should not return
            # CORS headers.
            formpost_info = self.client.create_formpost(
                container_name, files, key=tempurl_key)

            headers = formpost_info.get('headers')
            headers['Origin'] = 'http://foo.com'
            response = self.dumb_client.post(
                formpost_info.get('target_url'),
                headers=headers,
                data=formpost_info.get('body'),
                requestslib_kwargs={'allow_redirects': False})
            self.assertTrue(303, response.status_code)
            self.assertTrue('access-control-expose-headers' in
                            response.headers)
            self.assertTrue('location' in response.headers)
            self.assertTrue('access-control-allow-origin' in response.headers)

    def test_container_cors_preflight_request(self):
        """
        Scenario:
            Create a container with CORS headers:
               X-Container-Meta-Access-Control-Allow-Origin
               X-Container-Meta-Access-Control-Max-Age
               X-Container-Meta-Access-Control-Expose-Headers
            Make a preflight request using the OPTIONS call with an Origin
            that matches the container header.
            Make a preflight request using the OPTIONS call with an Origin
            that does not match the container header.

        Expected Results:
            If the Origin matches the Allow-Origin set:
                CF should return a 200.
            If the Origin does not match the Allow-Origin set:
                CF should return a 401.
        """
        expose_headers = ['Content-Length', 'Etag', 'X-Timestamp',
                          'X-Trans-Id']
        container_headers = {
            'X-Container-Meta-Access-Control-Allow-Origin':
            'http://example.com',
            'X-Container-Meta-Access-Control-Max-Age': '5',
            'X-Container-Meta-Access-Control-Expose-Headers':
            ','.join(expose_headers)}

        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR, headers=container_headers)

        container_url = '{0}/{1}'.format(
            self.client.storage_url, container_name)

        # OPTIONS Preflight request with matching Origin should return 200
        headers = {'Origin': 'http://example.com',
                   'Access-Control-Request-Method': 'POST'}
        preflight_response = self.dumb_client.request('OPTIONS',
                                                      container_url,
                                                      headers=headers)

        self.assertEqual(preflight_response.status_code,
                         200,
                         msg="Preflight request with matching Origin should "
                             "return {0} status code, received a {1}".format(
                                 "200", preflight_response.status_code))

        # OPTIONS Preflight request with non-matching Origin should return 401
        headers = {'Origin': 'http://test.com',
                   'Access-Control-Request-Method': 'POST'}
        preflight_response = self.dumb_client.request(
            'OPTIONS', container_url, headers=headers)

        self.assertEqual(preflight_response.status_code,
                         401,
                         msg="Preflight request with non-matching Origin "
                             "should return {0} status code, received a "
                             "{1}".format("401",
                                          preflight_response.status_code))

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('tempurl')
    def ddtest_container_cors_with_wildcard_origin(self, generate_object):
        """
        Scenario:
            Create a container with CORS headers:
               X-Container-Meta-Access-Control-Allow-Origin
               X-Container-Meta-Access-Control-Max-Age
               X-Container-Meta-Access-Control-Expose-Headers
            The X-Container-Meta-Access-Control-Allow-Origin header will be
            set to '*'.
            Retrieve an object with no Origin.
            Retrieve an object from a 'test' Origin.

        Expected Results:
            Retrieving the object with no Origin should not return a CORS
            header of Access-Control-Allow-Origin.
            Retrieving the object from any Origin should return a CORS
            header of Access-Control-Allow-Origin and it should be set to '*'.
        """

        expose_headers = ['Content-Length', 'Etag', 'X-Timestamp',
                          'X-Trans-Id']
        container_headers = {
            'X-Container-Meta-Access-Control-Allow-Origin': '*',
            'X-Container-Meta-Access-Control-Max-Age': '5',
            'X-Container-Meta-Access-Control-Expose-Headers':
            ','.join(expose_headers)}

        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR, headers=container_headers)

        object_headers = {'Content-Type': 'text/plain'}
        generate_object(container_name,
                        self.object_name,
                        headers=object_headers)

        tempurl_key = self.behaviors.get_tempurl_key()
        tempurl_info = self.client.create_temp_url('GET',
                                                   container_name,
                                                   self.object_name,
                                                   900,
                                                   tempurl_key)

        # tempURL parameters
        parameters = {'temp_url_sig': tempurl_info.get('signature'),
                      'temp_url_expires': tempurl_info.get('expires')}

        # Requests with no Origin should not return CORS headers.
        cors_response = self.dumb_client.request('GET',
                                                 tempurl_info.get(
                                                     'target_url'),
                                                 params=parameters)
        self.assertNotIn('Access-Control-Allow-Origin',
                         cors_response.headers,
                         msg="Allow-Origin header should not be returned "
                             "when a request is made with no Origin")
        self.assertNotIn('Access-Control-Max-Age',
                         cors_response.headers,
                         msg="Max-Age header should not be returned when a "
                             "request is made with no Origin")
        self.assertNotIn('Access-Control-Expose-Headers',
                         cors_response.headers,
                         msg="Expose-Headers header should not be returned "
                             "when a request is made with no Origin")

        headers = {'Origin': 'http://example.com'}
        parameters = {'temp_url_sig': tempurl_info.get('signature'),
                      'temp_url_expires': tempurl_info.get('expires')}

        # Requests with any Origin will return * as the allowed origin
        cors_response = self.dumb_client.request('GET',
                                                 tempurl_info.get(
                                                     'target_url'),
                                                 params=parameters,
                                                 headers=headers)
        self.assertIn('Access-Control-Allow-Origin',
                      cors_response.headers,
                      msg="The header Access-Control-Allow-Origin should be "
                          "returned in the list of headers: {0}".format(
                              cors_response.headers))
        self.assertEqual(
            cors_response.headers.get('Access-Control-Allow-Origin'),
            '*',
            msg="Allow-Origin header set to {0}, should be set to '*'".format(
                cors_response.headers.get('Access-Control-Allow-Origin')))

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('tempurl', 'object-cors')
    def ddtest_object_cors_with_tempurl(self, generate_object):
        """
        Scenario:
            Create a container.
            Create a object with CORS headers.
            Retrieve the object via TempURL.

        Expected Results:
            If no Origin is set:
                The object should be returned with no CORS headers.
            If the Origin matches the Allow-Origin set:
                The object should be returned with the CORS headers.
            If strict_cors_mode == True and the Origin does not match:
                The object should be returned with no CORS headers.
            If strict_cors_mode == False and the Origin does not match:
                The object should be returned with the CORS headers.
        """
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        expose_headers = ['Content-Length', 'Etag', 'X-Timestamp',
                          'X-Trans-Id']
        object_headers = {
            'Content-Type': 'text/plain',
            'X-Object-Meta-Access-Control-Allow-Origin':
            'http://example.com',
            'X-Object-Meta-Access-Control-Max-Age': '5',
            'X-Object-Meta-Access-Control-Expose-Headers':
            ','.join(expose_headers)}
        generate_object(container_name,
                        self.object_name,
                        headers=object_headers)

        tempurl_key = self.behaviors.get_tempurl_key()
        tempurl_info = self.client.create_temp_url(
            'GET', container_name, self.object_name, 900, tempurl_key)

        # Requests with no Origin should not return CORS headers.
        response = self.dumb_client.request(
            'GET', tempurl_info.get('target_url'), params={
                'temp_url_sig': tempurl_info.get('signature'),
                'temp_url_expires': tempurl_info.get('expires')})
        self.assertTrue(
            'Access-Control-Allow-Origin' not in response.headers,
            'Allow-Origin header should not be returned.')
        self.assertTrue('Access-Control-Max-Age' not in response.headers,
                        'Max-Age should not be returned.')
        self.assertTrue(
            'Access-Control-Expose-Headers' not in response.headers,
            'Expose-Headers should not be returned.')

        # Requests with Origin which does match, should return CORS headers.
        response = self.dumb_client.request(
            'GET', tempurl_info.get('target_url'), params={
                'temp_url_sig': tempurl_info.get('signature'),
                'temp_url_expires': tempurl_info.get('expires')},
            headers={'Origin': 'http://example.com'})
        self.assertTrue(
            'Access-Control-Allow-Origin' in response.headers,
            'Allow-Origin header should be returned.')
        self.assertTrue(
            'Access-Control-Expose-Headers' in response.headers,
            'Expose-Headers should be returned.')
        self.assertTrue('Access-Control-Max-Age' not in response.headers,
                        'Max-Age should not be returned.')

        if self.objectstorage_api_config.strict_cors_mode:
            # CORS should work according to the spec.
            # Requests with Origin which does not match, should not return
            # CORS headers.
            response = self.dumb_client.request(
                'GET', tempurl_info.get('target_url'), params={
                    'temp_url_sig': tempurl_info.get('signature'),
                    'temp_url_expires': tempurl_info.get('expires')},
                headers={'Origin': 'http://foo.com'})
            self.assertTrue(
                'Access-Control-Allow-Origin' not in response.headers,
                'Allow-Origin header should not be returned.')
            self.assertTrue('Access-Control-Max-Age' not in response.headers,
                            'Max-Age should not be returned.')
            self.assertTrue(
                'Access-Control-Expose-Headers' not in response.headers,
                'Expose-Headers should not be returned.')
        else:
            # Early implementation of CORS.
            # Requests with Origin which does not match, should not return
            # CORS headers.
            response = self.dumb_client.request(
                'GET', tempurl_info.get('target_url'), params={
                    'temp_url_sig': tempurl_info.get('signature'),
                    'temp_url_expires': tempurl_info.get('expires')},
                headers={'Origin': 'http://foo.com'})
            self.assertTrue(
                'Access-Control-Allow-Origin' in response.headers,
                'Allow-Origin header should be returned with '
                'differing origin.')
            self.assertTrue(
                'Access-Control-Expose-Headers' in response.headers,
                'Expose-Headers should be returned with '
                'differing origin.')
            self.assertTrue('Access-Control-Max-Age' not in response.headers,
                            'Max-Age should not be returned with '
                            'differing origin.')

    @data_driven_test(ObjectDatasetList())
    @ObjectStorageFixture.required_features('tempurl', 'object-cors')
    def ddtest_object_override_container_cors_with_tempurl(
            self, generate_object):
        """
        Scenario:
            Create a container with CORS headers.
            Create a object with CORS headers.
            Retrieve the object via TempURL.

        Expected Results:
            If no Origin is set:
                The object should be returned with no CORS headers.
            If the Origin matches the object's Allow-Origin:
                The object should be returned with the CORS headers.
            If strict_cors_mode == True and the Origin does not match:
                The object should be returned with no CORS headers.
            If strict_cors_mode == False and the Origin does not match:
                The object should be returned with the CORS headers.
        """
        container_expose_headers = ['Content-Length', 'Etag']
        container_headers = {
            'X-Container-Meta-Access-Control-Allow-Origin':
            'http://foo.com',
            'X-Container-Meta-Access-Control-Expose-Headers':
            ','.join(container_expose_headers)}
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR, headers=container_headers)

        object_expose_headers = ['X-Timestamp', 'X-Trans-Id']
        object_headers = {
            'Content-Type': 'text/plain',
            'X-Object-Meta-Access-Control-Allow-Origin':
            'http://bar.com',
            'X-Object-Meta-Access-Control-Expose-Headers':
            ','.join(object_expose_headers)}

        # object_headers = {'Content-Type': 'text/plain'}
        generate_object(container_name,
                        self.object_name,
                        headers=object_headers)

        tempurl_key = self.behaviors.get_tempurl_key()
        tempurl_info = self.client.create_temp_url(
            'GET', container_name, self.object_name, 900, tempurl_key)

        # Requests with no Origin should not return CORS headers.
        response = self.dumb_client.request(
            'GET', tempurl_info.get('target_url'), params={
                'temp_url_sig': tempurl_info.get('signature'),
                'temp_url_expires': tempurl_info.get('expires')})
        self.assertTrue(
            'Access-Control-Allow-Origin' not in response.headers,
            'Allow-Origin header should not be returned.')
        self.assertTrue(
            'Access-Control-Expose-Headers' not in response.headers,
            'Expose-Headers should not be returned.')

        # Requests with Origin which matches object, should return CORS
        # headers.
        response = self.dumb_client.request(
            'GET', tempurl_info.get('target_url'), params={
                'temp_url_sig': tempurl_info.get('signature'),
                'temp_url_expires': tempurl_info.get('expires')},
            headers={'Origin': 'http://bar.com'})
        self.assertTrue(
            'Access-Control-Allow-Origin' in response.headers,
            'Allow-Origin header should be returned.')
        self.assertEqual(
            'http://bar.com', response.headers.get(
                'Access-Control-Allow-Origin', ''),
            'Allow-Origin header should be returned.')
        self.assertTrue(
            'Access-Control-Expose-Headers' in response.headers,
            'Expose-Headers should be returned.')

        if self.objectstorage_api_config.strict_cors_mode:
            # CORS should work according to the spec.

            # Requests with Origin which matches container, should not return
            # CORS headers.
            response = self.dumb_client.request(
                'GET', tempurl_info.get('target_url'), params={
                    'temp_url_sig': tempurl_info.get('signature'),
                    'temp_url_expires': tempurl_info.get('expires')},
                headers={'Origin': 'http://foo.com'})
            self.assertTrue(
                'Access-Control-Allow-Origin' not in response.headers,
                'Allow-Origin header should not be returned.')
            self.assertTrue(
                'Access-Control-Expose-Headers' not in response.headers,
                'Expose-Headers should not be returned.')

            # Requests with Origin which does not match, should not return
            # CORS headers.
            response = self.dumb_client.request(
                'GET', tempurl_info.get('target_url'), params={
                    'temp_url_sig': tempurl_info.get('signature'),
                    'temp_url_expires': tempurl_info.get('expires')},
                headers={'Origin': 'http://example.com'})
            self.assertTrue(
                'Access-Control-Allow-Origin' not in response.headers,
                'Allow-Origin header should not be returned.')
            self.assertTrue(
                'Access-Control-Expose-Headers' not in response.headers,
                'Expose-Headers should not be returned.')
        else:
            # Early implementation of CORS.

            # Requests with Origin which matches container, should not return
            # CORS headers.
            response = self.dumb_client.request(
                'GET', tempurl_info.get('target_url'), params={
                    'temp_url_sig': tempurl_info.get('signature'),
                    'temp_url_expires': tempurl_info.get('expires')},
                headers={'Origin': 'http://foo.com'})
            self.assertTrue(
                'Access-Control-Allow-Origin' in response.headers,
                'Allow-Origin header should be returned.')
            self.assertTrue(
                'Access-Control-Expose-Headers' in response.headers,
                'Expose-Headers should be returned.')

            # Requests with Origin which does not match, should not return
            # CORS headers.
            response = self.dumb_client.request(
                'GET', tempurl_info.get('target_url'), params={
                    'temp_url_sig': tempurl_info.get('signature'),
                    'temp_url_expires': tempurl_info.get('expires')},
                headers={'Origin': 'http://example.com'})
            self.assertTrue(
                'Access-Control-Allow-Origin' in response.headers,
                'Allow-Origin header should be returned with '
                'differing origin.')
            self.assertTrue(
                'Access-Control-Expose-Headers' in response.headers,
                'Expose-Headers should be returned with '
                'differing origin.')
