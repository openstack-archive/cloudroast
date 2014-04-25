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
import re
import unittest
#from cafe.drivers.unittest.datasets import DatasetList
#from cafe.drivers.unittest.decorators import (
#    DataDrivenFixture, data_driven_test)
#from cafe.engine.config import EngineConfig
#from cloudcafe.common.tools.md5hash import get_md5_hash
from cloudcafe.common.tools.check_dict import get_value
from cloudroast.objectstorage.fixtures import ObjectStorageFixture

BASE_NAME = "extract_archive"
HTTP_OK = 200


class BulkDeleteTest(ObjectStorageFixture):
    """
    Will delete multiple objects or containers from their account with a
    single response.
    """

    def test_bulk_deletion_of_multiple_objects(self):
        """
        Scenario:
            Create objects in a container.
            Bulk delete some of the objects.

        Expected Results:
            Only the objects bulk deleted should be removed.
        """
        container_name = self.create_temp_container('bulk_delete')
        base_name = self.behaviors.VALID_OBJECT_NAME

        objects_to_remain = [
            '{0}10'.format(base_name),
            '{0}20'.format(base_name),
            '{0}30'.format(base_name),
            '{0}40'.format(base_name)]

        objects_to_delete = [
            '{0}1'.format(base_name),
            '{0}2'.format(base_name),
            '{0}3'.format(base_name),
            '{0}4'.format(base_name)]

        objects_to_create = objects_to_remain + objects_to_delete

        for name in objects_to_create:
            self.behaviors.create_object(
                container_name=container_name, object_name=name, data='')

        targets = ['/{0}/{1}'.format(
            container_name, name) for name in objects_to_delete]
        response = self.client.bulk_delete(targets)
        self.assertTrue(response.ok, 'should return report.')
        self.assertEqual(200, response.status_code, 'should 200.')

        self.assertTrue(
            re.search('Number Deleted:', response.content),
            'should contain "Number Deleted" in the report returned.')

        number_deleted = \
            int(re.findall('Number Deleted: (\d+)', response.content)[0])
        self.assertEqual(
            number_deleted, len(objects_to_delete),
            'should delete objects in the deletion list.')

        self.assertTrue(
            re.search('Number Not Found:', response.content),
            'should contain "Number Not Found" in the report returned.')

        not_found_count = \
            int(re.findall('Number Not Found: (\d+)', response.content)[0])
        self.assertEqual(
            not_found_count, 0,
            'should have found all objects to be removed.')

        c = self.client.get_object_count(container_name)
        self.assertEqual(
            c, len(objects_to_remain),
            'should not remove objects with similar names.')

    def test_bulk_deletion_of_all_objects(self):
        """
        Scenario:
            Create objects in a container.
            Bulk delete all of the objects.

        Expected Results:
            The created objects and the container should be deleted
        """
        container_name = self.create_temp_container('bulk_delete')
        base_name = self.behaviors.VALID_OBJECT_NAME

        objects_list = ['{0}{1}'.format(base_name, x) for x in range(1, 10)]

        for name in objects_list:
            self.behaviors.create_object(
                container_name=container_name, object_name=name, data='')

        targets = ['/{0}/{1}'.format(
            container_name, name) for name in objects_list]
        targets.append('/{0}'.format(container_name))

        response = self.client.bulk_delete(targets)
        self.assertTrue(response.ok, 'should return report.')

        self.assertTrue(
            re.search('Number Deleted:', response.content),
            'should contain "Number Deleted" in the report returned.')

        number_deleted = \
            int(re.findall('Number Deleted: (\d+)', response.content)[0])
        self.assertEqual(
            number_deleted, len(targets),
            'should delete objects in the deletion list.')

        self.assertTrue(
            re.search('Number Not Found:', response.content),
            'should contain "Number Not Found" in the report returned.')

        not_found_count = \
            int(re.findall('Number Not Found: (\d+)', response.content)[0])
        self.assertEqual(
            not_found_count, 0,
            'should have found all objects to be removed.')

        r = self.client.list_objects(container_name)
        self.assertEqual(
            r.status_code, 404,
            'container and all objects should have been deleted.')

    @unittest.skipUnless(get_value('slow') == 'true', 'test is too slow')
    def test_bulk_delete_max_count(self):
        """
        Scenario:
            Create a number of objects to equal the max number allowed for
            bulk delete.
            Bulk delete all of the objects.

        Expected Results:
            The all objects should be deleted.
        """
        container_name = self.create_temp_container('bulk_delete')
        base_name = self.behaviors.VALID_OBJECT_NAME

        objects_list = ['{0}{1}'.format(base_name, x + 1) for x in xrange(
            0, self.objectstorage_api_config.bulk_delete_max_count)]

        for name in objects_list:
            self.behaviors.create_object(
                container_name=container_name, object_name=name, data='')

        targets = ['/{0}/{1}'.format(
            container_name, name) for name in objects_list]

        response = self.client.bulk_delete(targets)
        self.assertTrue(response.ok, 'should return report.')

        self.assertTrue(
            re.search('Number Deleted:', response.content),
            'should contain "Number Deleted" in the report returned.')

        number_deleted = \
            int(re.findall('Number Deleted: (\d+)', response.content)[0])
        self.assertEqual(
            number_deleted, len(targets),
            'should delete objects in the deletion list.')

        self.assertTrue(
            re.search('Number Not Found:', response.content),
            'should contain "Number Not Found" in the report returned.')

        not_found_count = \
            int(re.findall('Number Not Found: (\d+)', response.content)[0])
        self.assertEqual(
            not_found_count, 0,
            'should have found all objects to be removed.')

    @unittest.skipUnless(get_value('slow') == 'true', 'test is too slow')
    def test_cant_bulk_delete_above_max_count(self):
        """
        Scenario:
            Create a number of objects to equal the max number + 1 allowed for
            bulk delete.
            Bulk delete all of the objects.

        Expected Results:
            An error should be returned informing the user that it could not
            delete the objects.
        """
        container_name = self.create_temp_container('bulk_delete')
        base_name = self.behaviors.VALID_OBJECT_NAME

        objects_list = ['{0}{1}'.format(base_name, x + 1) for x in xrange(
            0, self.objectstorage_api_config.bulk_delete_max_count + 1)]

        for name in objects_list:
            self.behaviors.create_object(
                container_name=container_name, object_name=name, data='')

        targets = ['/{0}/{1}'.format(
            container_name, name) for name in objects_list]

        response = self.client.bulk_delete(targets)

        self.assertEqual(response.status_code, 200, 'should return ok.')

        number_deleted = \
            int(re.findall('Number Deleted: (\d+)', response.content)[0])
        self.assertEqual(
            number_deleted, 0, 'should not delete over max objects count.')

        response_status = \
            re.findall('Response Status: (.+)', response.content)[0]
        self.assertEqual(
            response_status, '413 Request Entity Too Large',
            'should not bulk delete objects.')

    def test_bulk_deletion_empty_list(self):
        """
        Verify recieve an error when an empty list is sent.
        """
        container_name = self.create_temp_container('bulk_delete')
        object_name = self.behaviors.VALID_OBJECT_NAME

        self.behaviors.create_object(
            container_name=container_name, object_name=object_name, data='')

        targets = []
        response = self.client.bulk_delete(targets)
        self.assertEqual(response.status_code, 200, 'should return ok.')

        number_deleted = \
            int(re.findall('Number Deleted: (\d+)', response.content)[0])
        self.assertEqual(
            number_deleted, 0, 'should delete objects in the deletion list.')

        response_status = \
            re.findall('Response Status: (.+)', response.content)[0]
        self.assertEqual(
            response_status, '400 Bad Request',
            'should not bulk delete objects.')
