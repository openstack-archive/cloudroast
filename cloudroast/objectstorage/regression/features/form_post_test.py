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
from calendar import timegm
from time import gmtime, sleep, time
from cafe.engine.http.client import HTTPClient
from cloudroast.objectstorage.fixtures import ObjectStorageFixture

CONTAINER_DESCRIPTOR = 'form_post_test'
STATUS_CODE_MSG = ('{method} expected status code {expected}'
                   ' received status code {received}')


class FormPostTest(ObjectStorageFixture):

    @classmethod
    def setUpClass(cls):
        super(FormPostTest, cls).setUpClass()
        cls.key_cache_time = (
            cls.objectstorage_api_config.tempurl_key_cache_time)
        cls.tempurl_key = cls.behaviors.VALID_TEMPURL_KEY
        cls.object_name = cls.behaviors.VALID_OBJECT_NAME
        cls.object_data = cls.behaviors.VALID_OBJECT_DATA
        cls.content_length = str(len(cls.behaviors.VALID_OBJECT_DATA))
        cls.http_client = HTTPClient()
        cls.redirect_url = "http://example.com/form_post_test"

    @ObjectStorageFixture.required_features('formpost')
    def test_object_formpost_redirect(self):
        """
        Scenario:
            Try to POST an object through FormPOST which has a redirect
            URL in the form.

        Expected Results:
            1.Should return a 303 and the redirect URL should be set as a
              location in the response header.
            2.Redirect should not occur over HTTPS
        """
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        files = [{'name': 'foo1'}]

        formpost_info = self.client.create_formpost(
            container_name,
            files,
            redirect=self.redirect_url,
            max_file_size=104857600,
            max_file_count=1,
            key=self.tempurl_key)

        formpost_response = self.http_client.post(
            formpost_info.get('target_url'),
            headers=formpost_info.get('headers'),
            data=formpost_info.get('body'),
            requestslib_kwargs={'allow_redirects': False})

        method = 'Object Creation via FormPOST with redirect'
        expected = 303
        received = formpost_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        self.assertTrue('location' in formpost_response.headers,
                        msg="Could not find a redirect location in the "
                            "headers: {0}".format(formpost_response.headers))

        self.assertFalse(formpost_response.headers.get('location').startswith(
                         'https'),
                         msg="FormPOST should have been redirected to {0} "
                             "but went to {1} over HTTPS".format(
                             self.redirect_url,
                             formpost_response.headers.get('location')))

    @ObjectStorageFixture.required_features('formpost')
    def test_object_formpost_no_redirect(self):
        """
        Scenario:
            Try to POST an object through FormPOST without a redirect
            URL in the form.

        Expected Results:
            Should return a 201 and no redirect should be set in the
            response header.
        """
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        files = [{'name': 'foo1'}]

        formpost_info = self.client.create_formpost(
            container_name,
            files,
            redirect="",
            max_file_size=104857600,
            max_file_count=1,
            key=self.tempurl_key)

        formpost_response = self.http_client.post(
            formpost_info.get('target_url'),
            headers=formpost_info.get('headers'),
            data=formpost_info.get('body'),
            requestslib_kwargs={'allow_redirects': False})

        method = 'Object Creation via FormPOST without redirect'
        expected = 201
        received = formpost_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        self.assertTrue('location' not in formpost_response.headers,
                        msg="Found a redirect location in the "
                            "headers: {0}".format(formpost_response.headers))

    @ObjectStorageFixture.required_features('formpost')
    def test_object_formpost_x_delete_at(self):
        """
        Scenario:
            Try to set X_DELETE_AT for an object through FormPOST

        Expected Results:
            The object should be accessible before the 'delete at' time.
            The object should not be accessible after the 'delete at' time.
            The object should not be listed after the object expirer has had
            time to run.
        """
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        files = [{'name': 'foo1'}]

        delete_at = int(timegm(gmtime()) + 60)

        formpost_info = self.client.create_formpost(
            container_name,
            files,
            redirect=self.redirect_url,
            max_file_size=104857600,
            max_file_count=1,
            x_delete_at=delete_at,
            key=self.tempurl_key)

        formpost_response = self.http_client.post(
            formpost_info.get('target_url'),
            headers=formpost_info.get('headers'),
            data=formpost_info.get('body'),
            requestslib_kwargs={'allow_redirects': False})

        method = 'Object Creation via FormPOST '
        expected = 303
        received = formpost_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        object_response = self.client.get_object(container_name,
                                                 files[0].get("name"))

        self.assertEqual(200,
                         object_response.status_code,
                         msg="Object {0} should exist until {1}".format(
                             files[0].get("name"), delete_at))

        # wait for the object to be deleted.
        sleep(self.objectstorage_api_config.object_deletion_wait_interval)

        delete_response = self.client.get_object(container_name,
                                                 files[0].get("name"))

        self.assertEqual(404,
                         delete_response.status_code,
                         msg="Object should be deleted after X-Delete-At.")

    @ObjectStorageFixture.required_features('formpost')
    def test_object_formpost_x_delete_after(self):
        """
        Scenario:
            Try to set X_DELETE_AFTER for an object through FormPOST

        Expected Results:
            The object should be accessible until the 'delete after' time.
            The object should not be accessible after the 'delete after' time.
            The object should not be listed after the object expirer has had
            time to run.
        """
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        files = [{'name': 'foo1'}]

        delete_after = 60

        formpost_info = self.client.create_formpost(
            container_name,
            files,
            redirect=self.redirect_url,
            max_file_size=104857600,
            max_file_count=1,
            x_delete_after=delete_after,
            key=self.tempurl_key)

        formpost_response = self.http_client.post(
            formpost_info.get('target_url'),
            headers=formpost_info.get('headers'),
            data=formpost_info.get('body'),
            requestslib_kwargs={'allow_redirects': False})

        method = 'Object Creation via FormPOST '
        expected = 303
        received = formpost_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        object_response = self.client.get_object(container_name,
                                                 files[0].get("name"))

        self.assertEqual(200,
                         object_response.status_code,
                         msg="Object {0} should exist for {1} "
                             "seconds.".format(files[0].get("name"),
                                               delete_after))

        # wait for the object to be deleted.
        sleep(delete_after)

        delete_response = self.client.get_object(container_name,
                                                 files[0].get("name"))

        self.assertEqual(404,
                         delete_response.status_code,
                         msg="Object {0} should be deleted after {1} "
                             "seconds.".format(files[0].get("name"),
                                               delete_after))

    @ObjectStorageFixture.required_features('formpost')
    def test_object_formpost_over_max_file_count(self):
        """
        Scenario:
            Try to POST an object through FormPOST, passing in more files
            than the max_file_count.

        Expected Results:
            The FormPOST will return a 400.
            Any files up to the max_count will create objects, while files
            over the max_count will not.
        """
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        files = [{'name': 'test_1'}, {'name': 'test_2'}]

        formpost_info = self.client.create_formpost(
            container_name,
            files,
            redirect="",
            max_file_size=104857600,
            max_file_count=1,
            key=self.tempurl_key)

        formpost_response = self.http_client.post(
            formpost_info.get('target_url'),
            headers=formpost_info.get('headers'),
            data=formpost_info.get('body'),
            requestslib_kwargs={'allow_redirects': False})

        method = 'Object FormPOST over max file count '
        expected = 400
        received = formpost_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        object_response = self.client.get_object(container_name,
                                                 files[0].get("name"))

        self.assertEqual(200,
                         object_response.status_code,
                         msg="GET on object {0} should return status code "
                             "{1} actually received status code {2}.".format(
                                 files[0].get("name"),
                                 200,
                                 object_response.status_code))

        object_response = self.client.get_object(container_name,
                                                 files[1].get("name"))

        self.assertEqual(404,
                         object_response.status_code,
                         msg="GET on object {0} should return status code "
                             "{1} actually received status code {2}.".format(
                                 files[0].get("name"),
                                 404,
                                 object_response.status_code))

    @ObjectStorageFixture.required_features('formpost')
    def test_object_formpost_over_max_file_size(self):
        """
        Scenario:
            Try to POST an object through FormPOST, passing in a file bigger
            than the max_file_size.

        Expected Results:
            Should return a 413 and no object should be created
        """
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        files = [{'name': 'foo1'}]

        formpost_info = self.client.create_formpost(
            container_name,
            files,
            redirect="",
            max_file_size=10,
            max_file_count=1,
            key=self.tempurl_key)

        formpost_response = self.http_client.post(
            formpost_info.get('target_url'),
            headers=formpost_info.get('headers'),
            data=formpost_info.get('body'),
            requestslib_kwargs={'allow_redirects': False})

        method = 'Object FormPOST over max file size '
        expected = 413
        received = formpost_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        object_response = self.client.get_object(container_name,
                                                 files[0].get("name"))

        self.assertEqual(404,
                         object_response.status_code,
                         msg="GET on object {0} should return status code "
                             "{1} actually received status code {2}.".format(
                                 files[0].get("name"),
                                 404,
                                 object_response.status_code))

    @ObjectStorageFixture.required_features('formpost')
    def test_object_formpost_after_expires(self):
        """
        Scenario:
            Create a form, then let it expire, then try to POST the form.

        Expected Results:
            Should return a 401 and no object should be created
        """
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        files = [{'name': 'foo1'}]
        expire_time = int(time() + 60)

        formpost_info = self.client.create_formpost(
            container_name,
            files,
            redirect="",
            expires=expire_time,
            max_file_size=10,
            max_file_count=1,
            key=self.tempurl_key)

        # Wait for form to expire
        sleep(65)

        formpost_response = self.http_client.post(
            formpost_info.get('target_url'),
            headers=formpost_info.get('headers'),
            data=formpost_info.get('body'),
            requestslib_kwargs={'allow_redirects': False})

        method = 'Object FormPOST with expired form '
        expected = 401
        received = formpost_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        object_response = self.client.get_object(container_name,
                                                 files[0].get("name"))

        self.assertEqual(404,
                         object_response.status_code,
                         msg="GET on object {0} should return status code "
                             "{1} actually received status code {2}.".format(
                                 files[0].get("name"),
                                 404,
                                 object_response.status_code))

    @ObjectStorageFixture.required_features('formpost')
    def test_object_formpost_with_bad_signature(self):
        """
        Scenario:
            Try to POST a form with a bad signature

        Expected Results:
            Should return a 4XX and no object should be created
        """
        container_name = self.create_temp_container(
            descriptor=CONTAINER_DESCRIPTOR)

        files = [{'name': 'foo1'}]

        formpost_info = self.client.create_formpost(
            container_name,
            files,
            redirect="",
            max_file_size=10,
            max_file_count=1,
            key=self.tempurl_key,
            signature="79d078b5f1de29")

        formpost_response = self.http_client.post(
            formpost_info.get('target_url'),
            headers=formpost_info.get('headers'),
            data=formpost_info.get('body'),
            requestslib_kwargs={'allow_redirects': False})

        method = 'Object FormPOST with bad signature '
        expected = 401
        received = formpost_response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received)))

        object_response = self.client.get_object(container_name,
                                                 files[0].get("name"))

        self.assertEqual(404,
                         object_response.status_code,
                         msg="GET on object {0} should return status code "
                             "{1} actually received status code {2}.".format(
                                 files[0].get("name"),
                                 404,
                                 object_response.status_code))
