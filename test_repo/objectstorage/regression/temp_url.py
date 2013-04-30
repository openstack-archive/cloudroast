import time

from urllib import quote
from datetime import datetime
from cloudcafe.common.tools import md5hash
from cloudcafe.common.tools import randomstring
from test_repo.objectstorage.fixtures import ObjectStorageFixture

CONTENT_TYPE_TEXT = 'text/plain; charset=UTF-8'


class TempUrl(ObjectStorageFixture):

    def test_tempurl_object_upload(self):
        time.sleep(61)

        container_name = '{0}_{1}'.format(
                self.base_container_name,
                randomstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
                self.client.force_delete_containers,
                [container_name])

        object_name = '{0}_{1}'.format(
                self.base_object_name,
                randomstring.get_random_string())

        headers = {'Content-Length': '0'}

        self.client.create_object(
                container_name,
                object_name,
                headers=headers)

        temp_key = '{0}_{1}'.format(
                'temp_url_dl_test_key',
                randomstring.get_random_string())
        key = md5hash.get_md5_hash(temp_key)
        headers = {'X-Account-Meta-Temp-URL-Key': key}

        resp = self.client.set_temp_url_key(headers=headers)

        self.assertEqual(resp.status_code, 204)

        tempurl_data = self.client.create_temp_url(
                'PUT',
                container_name,
                object_name,
                '86400',
                key)

        ul_tempurl = '{0}?temp_url_sig={1}&temp_url_expires={2}'.format(
                tempurl_data['target_url'],
                tempurl_data['signature'],
                tempurl_data['expires'])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        etag = md5hash.get_md5_hash(object_data)

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Etag': etag}

        resp = self.client.put(ul_tempurl, data=object_data, headers=headers)
        self.assertEqual(resp.status_code, 201)

        resp = self.client.get_object(container_name, object_name)
        self.assertEqual(resp.content, object_data)

    def test_tempurl_object_download(self):
        time.sleep(61)

        container_name = '{0}_{1}'.format(
                self.base_container_name,
                randomstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
                self.client.force_delete_containers,
                [container_name])

        object_name = '{0}_{1}'.format(
                self.base_object_name,
                randomstring.get_random_string())
        object_data = 'Test file data'
        content_length = str(len(object_data))
        etag = md5hash.get_md5_hash(object_data)

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT,
                   'Etag': etag}

        self.client.create_object(
                container_name,
                object_name,
                headers=headers,
                data=object_data)

        temp_key = '{0}_{1}'.format(
                'temp_url_dl_test_key',
                randomstring.get_random_string())
        key = md5hash.get_md5_hash(temp_key)
        headers = {'X-Account-Meta-Temp-URL-Key': key}

        resp = self.client.set_temp_url_key(headers=headers)

        self.assertEqual(resp.status_code, 204)

        tempurl_data = self.client.create_temp_url(
                'GET',
                container_name,
                object_name,
                '86400',
                key)

        dl_tempurl = '{0}?temp_url_sig={1}&temp_url_expires={2}'.format(
                tempurl_data['target_url'],
                tempurl_data['signature'],
                tempurl_data['expires'])

        resp = self.client.get(dl_tempurl)

        if resp.headers['content-disposition'] is not None:
            expected = 'attachment; filename="{0}"'.format(object_name)
            recieved = resp.headers['content-disposition']
            self.assertEqual(expected, recieved)
        else:
            self.assertIsNotNone(resp.headers['content-disposition'])
