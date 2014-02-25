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
from cloudcafe.common.tools import randomstring as randstring
from cafe.drivers.unittest.decorators import data_driven_test
from cafe.drivers.unittest.decorators import DataDrivenFixture
from cloudroast.objectstorage.fixtures import ObjectStorageFixture
from cafe.drivers.unittest.datasets import DatasetList

CONTENT_TYPE_TEXT = 'text/plain; charset=UTF-8'
STATUS_CODE_MSG = '{method} expected status code {expected}' \
    ' received status code {received} headers: {headers}'


class DataSetList(DatasetList):
    def append_new_dataset(self, descriptor, hdrs=None):
        """
        @type  client_roles: list of strings
        @param client_roles: list of role names
        """
        dataset = {"descriptor": descriptor,
                   "hdrs": hdrs}

        super(DataSetList, self).append_new_dataset(
            str(descriptor),
            dataset)


data_set_list = DataSetList()

data_set_list.append_new_dataset(
    "0", hdrs={'Accept': 'application/xml'})

data_set_list.append_new_dataset(
    "1", hdrs={'Accept': 'application/xml; charset=UTF-8'})

data_set_list.append_new_dataset(
    "2", hdrs={'Accept': 'application/xml; q=0.9'})

data_set_list.append_new_dataset(
    "3", hdrs={'Accept': 'application/xml; foo="bar"'})

data_set_list.append_new_dataset(
    "4", hdrs={'Accept': 'application/xml; q=0.9; foo="bar"'})

data_set_list.append_new_dataset(
    "5", hdrs={'Accept': 'application/xml; charset=UTF-8; q=0.9'})

data_set_list.append_new_dataset(
    "6", hdrs={'Accept': 'application/xml; charset=UTF-8; foo="bar"'})

data_set_list.append_new_dataset(
    "7", hdrs={'Accept': 'application/xml; charset=UTF-8; q=0.9; foo="bar"'})

data_set_list.append_new_dataset(
    "8", hdrs={'Accept': 'application/json'})

data_set_list.append_new_dataset(
    "9", hdrs={'Accept': 'application/json; charset=UTF-8'})

data_set_list.append_new_dataset(
    "10", hdrs={'Accept': 'application/json; q=0.9'})

data_set_list.append_new_dataset(
    "11", hdrs={'Accept': 'application/json; foo="bar"'})

data_set_list.append_new_dataset(
    "12", hdrs={'Accept': 'application/json; q=0.9; foo="bar"'})

data_set_list.append_new_dataset(
    "13", hdrs={'Accept': 'application/json; charset=UTF-8; q=0.9'})

data_set_list.append_new_dataset(
    "14", hdrs={'Accept': 'application/json; charset=UTF-8; foo="bar"'})

data_set_list.append_new_dataset(
    "15", hdrs={'Accept': 'application/json; charset=UTF-8; q=0.9; foo="bar"'})


@DataDrivenFixture
class ExtendedAcceptHeaderTest(ObjectStorageFixture):
    @data_driven_test(data_set_list)
    def ddtest_object_list_with_extended_accept_header(self, descriptor=None,
                                                       hdrs=None):
        """
        test for openstack bug #1202453 fix
        and expansion of accept to take 'q' and
        arbitrary extensions
        """
        container_name = '{0}_{1}'.format(
            self.base_container_name,
            randstring.get_random_string())
        self.client.create_container(container_name)
        self.addCleanup(
            self.behaviors.force_delete_containers,
            [container_name])

        object_data = 'Test file data'
        content_length = str(len(object_data))
        object_name = '{0}_{1}'.format(
            'extended_accept_header',
            randstring.get_random_string())

        headers = {'Content-Length': content_length,
                   'Content-Type': CONTENT_TYPE_TEXT}

        self.client.create_object(
            container_name,
            object_name,
            headers=headers,
            data=object_data)

        # headers from the data set
        headers = hdrs

        response = self.client.list_objects(
            container_name,
            headers=hdrs)

        method = 'list objects'
        expected = 200
        received = response.status_code

        self.assertEqual(
            expected,
            received,
            msg=STATUS_CODE_MSG.format(
                method=method,
                expected=expected,
                received=str(received),
                headers=str(hdrs)))
