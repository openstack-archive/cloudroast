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
from cafe.engine.http.client import BaseHTTPClient
from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cloudroast.objectstorage.generators import ObjectDatasetList

CONTAINER_DESCRIPTOR = 'cors'


@DataDrivenFixture
class CORSTest(ObjectStorageFixture):

    @data_driven_test(ObjectDatasetList())
    #@ObjectStorageFixture.required_features('tempurl')
    def ddtest_container_cors_with_tempurl(self, object_type, generate_object):
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
        # Temp fix till required_features decorator can be used with data
        # driven tests.
        features = self.behaviors.get_configured_features()
        if 'tempurl' not in features and features != '__ALL__':
            self.skipTest('tempurl not configured')

        expose_headers = ['Content-Length', 'Etag', 'X-Timestamp',
                          'X-Trans-Id']
        container_headers = {
            'X-Container-Meta-Access-Control-Allow-Origin':
            'http://example.com',
            'X-Container-Meta-Access-Control-Max-Age': '5',
            'X-Container-Meta-Access-Control-Expose-Headers':
            ','.join(expose_headers)}

        container_name = self.create_temp_container(
            descriptor='container-smoke', headers=container_headers)
        object_name = 'object'
        object_headers = {'Content-Type': 'text/plain'}
        generate_object(container_name, object_name, headers=object_headers)
        tempurl_key = self.behaviors.get_tempurl_key()
        tempurl_info = self.client.create_temp_url(
            'GET', container_name, object_name, 900, tempurl_key)

        dumb_client = BaseHTTPClient()

        # Requests with no Origin should not return CORS headers.
        response = dumb_client.request(
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
        response = dumb_client.request(
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
            response = dumb_client.request(
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
            response = dumb_client.request(
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
            descriptor='container-smoke', headers=container_headers)

        tempurl_key = self.behaviors.get_tempurl_key()
        files = [{'name': 'foo1'}]

        # Requests with no Origin should not return CORS headers.
        formpost_info = self.client.create_formpost(
            container_name, files, key=tempurl_key)
        dumb_client = BaseHTTPClient()
        headers = formpost_info.get('headers')
        response = dumb_client.post(formpost_info.get('target_url'),
                                    headers=headers,
                                    data=formpost_info.get('body'),
                                    allow_redirects=False)
        self.assertTrue(303, response.status_code)
        self.assertTrue('location' in response.headers)
        self.assertTrue('access-control-expose-headers' not in
                        response.headers)
        self.assertTrue('access-control-allow-origin' not in response.headers)

        # Requests with Origin which does match, should return CORS headers.
        formpost_info = self.client.create_formpost(
            container_name, files, key=tempurl_key)
        dumb_client = BaseHTTPClient()
        headers = formpost_info.get('headers')
        headers['Origin'] = 'http://example.com'
        response = dumb_client.post(formpost_info.get('target_url'),
                                    headers=headers,
                                    data=formpost_info.get('body'),
                                    allow_redirects=False)
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
            dumb_client = BaseHTTPClient()
            headers = formpost_info.get('headers')
            headers['Origin'] = 'http://foo.com'
            response = dumb_client.post(formpost_info.get('target_url'),
                                        headers=headers,
                                        data=formpost_info.get('body'),
                                        allow_redirects=False)
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
            dumb_client = BaseHTTPClient()
            headers = formpost_info.get('headers')
            headers['Origin'] = 'http://foo.com'
            response = dumb_client.post(formpost_info.get('target_url'),
                                        headers=headers,
                                        data=formpost_info.get('body'),
                                        allow_redirects=False)
            self.assertTrue(303, response.status_code)
            self.assertTrue('access-control-expose-headers' in
                            response.headers)
            self.assertTrue('location' in response.headers)
            self.assertTrue('access-control-allow-origin' in response.headers)

    @data_driven_test(ObjectDatasetList())
    #@ObjectStorageFixture.required_features('tempurl')
    def ddtest_object_cors_with_tempurl(self, object_type, generate_object):
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
        # Temp fix till required_features decorator can be used with data
        # driven tests.
        features = self.behaviors.get_configured_features()
        if 'tempurl' not in features and features != '__ALL__':
            self.skipTest('tempurl not configured')

        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)
        object_name = 'object'
        expose_headers = ['Content-Length', 'Etag', 'X-Timestamp',
                          'X-Trans-Id']
        object_headers = {
            'Content-Type': 'text/plain',
            'X-Object-Meta-Access-Control-Allow-Origin':
            'http://example.com',
            'X-Object-Meta-Access-Control-Max-Age': '5',
            'X-Object-Meta-Access-Control-Expose-Headers':
            ','.join(expose_headers)}
        generate_object(container_name, object_name, headers=object_headers)
        tempurl_key = self.behaviors.get_tempurl_key()
        tempurl_info = self.client.create_temp_url(
            'GET', container_name, object_name, 900, tempurl_key)

        dumb_client = BaseHTTPClient()

        # Requests with no Origin should not return CORS headers.
        response = dumb_client.request(
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
        response = dumb_client.request(
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
            response = dumb_client.request(
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
            response = dumb_client.request(
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
    #@ObjectStorageFixture.required_features('tempurl')
    def ddtest_object_override_container_cors_with_tempurl(
            self, object_type, generate_object):
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
        # Temp fix till required_features decorator can be used with data
        # driven tests.
        features = self.behaviors.get_configured_features()
        if 'tempurl' not in features and features != '__ALL__':
            self.skipTest('tempurl not configured')

        container_expose_headers = ['Content-Length', 'Etag']
        container_headers = {
            'X-Container-Meta-Access-Control-Allow-Origin':
            'http://foo.com',
            'X-Container-Meta-Access-Control-Expose-Headers':
            ','.join(container_expose_headers)}
        container_name = self.create_temp_container(
            descriptor='container-smoke', headers=container_headers)

        object_expose_headers = ['X-Timestamp', 'X-Trans-Id']
        object_headers = {
            'Content-Type': 'text/plain',
            'X-Object-Meta-Access-Control-Allow-Origin':
            'http://bar.com',
            'X-Object-Meta-Access-Control-Expose-Headers':
            ','.join(object_expose_headers)}
        object_name = 'object'
        object_headers = {'Content-Type': 'text/plain'}
        generate_object(container_name, object_name, headers=object_headers)
        tempurl_key = self.behaviors.get_tempurl_key()
        tempurl_info = self.client.create_temp_url(
            'GET', container_name, object_name, 900, tempurl_key)

        dumb_client = BaseHTTPClient()

        # Requests with no Origin should not return CORS headers.
        response = dumb_client.request(
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
        response = dumb_client.request(
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
            response = dumb_client.request(
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
            response = dumb_client.request(
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
            response = dumb_client.request(
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
            response = dumb_client.request(
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
