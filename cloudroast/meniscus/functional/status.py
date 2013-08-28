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
from json import dumps as dict_to_str
from cloudroast.meniscus.fixtures import StatusFixture
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import (tags, data_driven_test,
                                              DataDrivenFixture)
from cafe.drivers.unittest.decorators import skip_open_issue


class LoadAveragePositiveDatasetList(DatasetList):
    def __init__(self):
        super(LoadAveragePositiveDatasetList, self).__init__()
        self.append_new_dataset('zeroed', {'one': 0, 'five': 0, 'fifteen': 0})
        self.append_new_dataset('floats',
                                {'one': 0.1, 'five': 0.1, 'fifteen': 0.1})


class LoadAverageNegativeDatasetList(DatasetList):
    def __init__(self):
        super(LoadAverageNegativeDatasetList, self).__init__()
        self.append_new_dataset('empty_strings',
                                {'one': '', 'five': '', 'fifteen': ''})
        self.append_new_dataset('nones',
                                {'one': None, 'five': None, 'fifteen': None})
        self.append_new_dataset('arrays',
                                {'one': [], 'five': [], 'fifteen': []})
        self.append_new_dataset('dictionaries',
                                {'one': {}, 'five': {}, 'fifteen': {}})


class DiskUsagePositiveDatasetList(DatasetList):
    def __init__(self):
        super(DiskUsagePositiveDatasetList, self).__init__()
        self.append_new_dataset('values_ints', {'device': '/dev/sda1',
                                                'total': 1000, 'used': 500})
        self.append_new_dataset('sysdev_path', {'device': '/sys/devices/blk1',
                                                'total': 1000, 'used': 500})


class DiskUsageNegativeDatasetList(DatasetList):
    def __init__(self):
        super(DiskUsageNegativeDatasetList, self).__init__()
        self.append_new_dataset('number_strings', {'device': '/dev/sda1',
                                                   'total': '1000',
                                                   'used': '500'})
        self.append_new_dataset('invalid_strings', {'device': 'boom',
                                                    'total': 'trace',
                                                    'used': 'boom'})
        self.append_new_dataset('device_to_array',
                                {'device': [], 'total': 1000, 'used': 500})
        self.append_new_dataset('device_to_dictionary',
                                {'device': {}, 'total': 1000, 'used': 500})


@DataDrivenFixture
class TestStatus(StatusFixture):

    def setUp(self):
        super(TestStatus, self).setUp()
        self.pairing_resp = self.pairing_behaviors.pair_worker_from_config()
        self.assertEqual(self.pairing_resp.status_code, 202)
        self.pairing_info = self.pairing_resp.entity
        self.worker_id = self.pairing_info.worker_id
        self.worker_token = self.pairing_info.worker_token

    @tags(type='positive')
    @data_driven_test(LoadAveragePositiveDatasetList())
    def ddtest_set_load_to_positive(self, one=None, five=None, fifteen=None):
        resp = self.status_behaviors.update_load_average(
            worker_id=self.worker_id,
            worker_token=self.worker_token,
            one=one,
            five=five,
            fifteen=fifteen)
        self.assertEqual(resp.status_code, 200)

        resp = self.status_client.get_worker_status(self.worker_id)
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.entity)
        self.assertIsNotNone(resp.entity.system_info)

        load_average = resp.entity.system_info.load_average
        self.assertEqual(load_average.one_average, one)
        self.assertEqual(load_average.five_average, five)
        self.assertEqual(load_average.fifteen_average, fifteen)

    @tags(type='negative')
    @data_driven_test(LoadAverageNegativeDatasetList())
    def ddtest_set_load_to_negative(self, one=None, five=None, fifteen=None):
        resp = self.status_behaviors.update_load_average(
            worker_id=self.worker_id,
            worker_token=self.worker_token,
            one=one,
            five=five,
            fifteen=fifteen)
        self.assertEqual(resp.status_code, 400)

    @tags(type='positive')
    @data_driven_test(DiskUsagePositiveDatasetList())
    def ddtest_positive_set_usage_to(self, device, total, used):
        disks = [{'device': device, 'total': total, 'used': used}]
        resp = self.status_behaviors.update_status_from_config(
            worker_id=self.worker_id,
            worker_token=self.worker_token,
            disks=disks)
        self.assertEqual(resp.status_code, 200)
        # TODO: Add additional verification when available.

    @tags(type='negative')
    @data_driven_test(DiskUsageNegativeDatasetList())
    def ddtest_negative_set_usage_to(self, device, total, used):
        disks = [{'device': device, 'total': total, 'used': used}]
        resp = self.status_behaviors.update_status_from_config(
            worker_id=self.worker_id,
            worker_token=self.worker_token,
            disks=disks)
        self.assertEqual(resp.status_code, 400)

    @tags(type='negative')
    @skip_open_issue('GitHub', '327')
    def test_set_load_to_neg_numbers(self):
        """ This should be added to the dataset when completed. """
        self.ddtest_set_load_to_negative(one=-2, five=-2, fifteen=-2)

    @tags(type='negative')
    def test_set_load_with_invalid_body(self):
        data = dict_to_str({"load_average": "didn't validate me"})
        resp = self.status_client.direct_update(
            worker_id=self.worker_id,
            worker_token=self.worker_token,
            body=data)
        self.assertEqual(resp.status_code, 400)

    @tags(type='negative')
    def test_set_usage_with_invalid_body(self):
        worker_id = self.pairing_info.worker_id
        worker_token = self.pairing_info.worker_token
        data = dict_to_str({'disk_usage': 'random_str'})

        resp = self.status_client.direct_update(worker_id=worker_id,
                                                worker_token=worker_token,
                                                body=data)
        self.assertEqual(resp.status_code, 400)
