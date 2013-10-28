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

from cafe.drivers.unittest.decorators import tags
from cloudcafe.compute.common.exceptions import BadRequest, ItemNotFound
from cloudroast.compute.fixtures import ComputeFixture


class FlavorsTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        super(FlavorsTest, cls).setUpClass()
        flavors = cls.flavors_client.list_flavors_with_detail().entity

        # Find the flavor that provides the most RAM
        flavors.sort(key=lambda k: k.ram)
        cls.max_ram = flavors[-1].ram

        # Find the flavor that provides the most disk
        flavors.sort(key=lambda k: k.disk)
        cls.max_disk = flavors[-1].disk

    @tags(type='smoke', net='no')
    def test_list_flavors(self):
        """ List of all flavors should contain the expected flavor """
        response = self.flavors_client.list_flavors()
        flavors = response.entity
        self.assertTrue(len(flavors) > 0)
        response = self.flavors_client.get_flavor_details(self.flavor_ref)
        flavor = response.entity
        for each in flavors:
            if flavor.id == each.id:
                return
        self.fail("The expected flavor: %s was not found in the flavor list."
                  % flavor.id)

    @tags(type='smoke', net='no')
    def test_list_flavors_with_detail(self):
        """ Detailed list of all flavors should contain the expected flavor """
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity
        self.assertTrue(len(flavors) > 0)
        response = self.flavors_client.get_flavor_details(self.flavor_ref)
        flavor = response.entity
        self.assertIn(flavor, flavors)

    @tags(type='smoke', net='no')
    def test_get_flavor(self):
        """ The expected flavor details should be returned """
        response = self.flavors_client.get_flavor_details(self.flavor_ref)
        flavor = response.entity
        self.assertEqual(self.flavor_ref, flavor.id)

    @tags(type='negative', net='no')
    def test_get_non_existent_flavor(self):
        """flavor details are not returned for non existent flavors"""
        try:
            self.flavors_client.get_flavor_details(999)
            self.fail('No exception thrown for a non-existent flavor id')
        except ItemNotFound:
            pass

    @tags(type='positive', net='no')
    def test_list_flavors_limit_results(self):
        """Only the expected number of flavors should be returned"""
        response = self.flavors_client.list_flavors(limit=1)
        flavors = response.entity
        self.assertEqual(1, len(flavors))

    @tags(type='positive', net='no')
    def test_list_flavors_detailed_limit_results(self):
        """The expected number of flavors (detailed) should be returned"""
        response = self.flavors_client.list_flavors_with_detail(limit=1)
        flavors = response.entity
        self.assertEqual(1, len(flavors))

    @tags(type='positive', net='no')
    def test_list_flavors_using_marker(self):
        """The list of flavors should start after the provided marker"""
        response = self.flavors_client.list_flavors()
        flavors = response.entity
        flavor_marker = flavors[0]

        response = self.flavors_client.list_flavors(marker=flavor_marker.id)
        filtered_flavors = response.entity
        self.assertNotIn(flavor_marker, filtered_flavors,
                         msg='Filtered flavor was incorrectly '
                             'included in the list of returned flavors')

    @tags(type='positive', net='no')
    def test_list_flavors_detailed_using_marker(self):
        """The list of flavors should start from the provided marker"""
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity
        flavor_marker = flavors[0]

        response = self.flavors_client.list_flavors_with_detail(
            marker=flavor_marker.id)
        filtered_flavors = response.entity
        self.assertNotIn(flavor_marker, filtered_flavors,
                         msg='Filtered flavor was incorrectly '
                             'included in the list of returned flavors')

    @tags(type='positive', net='no')
    def test_list_flavors_detailed_filter_by_min_disk(self):
        """The detailed list of flavors should be filtered by disk space"""
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity
        flavors.sort(key=lambda k: int(k.disk))

        # Filter out any flavors of the same size
        filter_criteria = lambda x: int(x.disk) >= int(flavors[1].disk)
        expected_flavors = filter(filter_criteria, flavors)
        response = self.flavors_client.list_flavors_with_detail(
            min_disk=flavors[1].disk)
        actual_flavors = response.entity
        actual_flavors.sort(key=lambda k: k.id)
        expected_flavors.sort(key=lambda k: k.id)
        self.assertEqual(actual_flavors, expected_flavors)

    @tags(type='positive', net='no')
    def test_list_flavors_detailed_filter_by_min_ram(self):
        """The detailed list of flavors should be filtered by RAM"""
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity
        flavors.sort(key=lambda k: int(k.ram))
        # Filter out any flavors of the same size
        filter_criteria = lambda x: int(x.ram) >= int(flavors[1].ram)
        expected_flavors = filter(filter_criteria, flavors)
        response = self.flavors_client.list_flavors_with_detail(
            min_ram=flavors[1].ram)
        actual_flavors = response.entity
        actual_flavors.sort(key=lambda k: k.id)
        expected_flavors.sort(key=lambda k: k.id)
        self.assertEqual(actual_flavors, expected_flavors)

    @tags(type='positive', net='no')
    def test_list_flavors_filter_by_min_disk(self):
        """The list of flavors should be filtered by disk space"""
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity
        flavors.sort(key=lambda k: int(k.disk))

        # Filter out any flavors of the same size
        filter_criteria = lambda x: int(x.disk) >= int(flavors[1].disk)
        expected_flavors = filter(filter_criteria, flavors)
        response = self.flavors_client.list_flavors(min_disk=flavors[1].disk)
        actual_flavors = response.entity

        actual_flavor_ids = set([flavor.id for flavor in actual_flavors])
        expected_flavor_ids = set([flavor.id for flavor in expected_flavors])
        self.assertEqual(actual_flavor_ids, expected_flavor_ids)

    @tags(type='positive', net='no')
    def test_list_flavors_filter_by_min_ram(self):
        """The list of flavors should be filtered by RAM"""
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity
        flavors.sort(key=lambda k: int(k.ram))

        # Filter out any flavors of the same size
        filter_criteria = lambda x: int(x.ram) >= int(flavors[1].ram)
        expected_flavors = filter(filter_criteria, flavors)
        response = self.flavors_client.list_flavors(min_ram=flavors[1].ram)
        actual_flavors = response.entity

        actual_flavor_ids = set([flavor.id for flavor in actual_flavors])
        expected_flavor_ids = set([flavor.id for flavor in expected_flavors])
        self.assertEqual(actual_flavor_ids, expected_flavor_ids)

    @tags(type='negative', net='no')
    def test_list_flavors_detailed_filter_by_invalid_min_disk(self):
        """The detailed list of flavors should be filtered by disk space"""
        with self.assertRaises(BadRequest):
            response = self.flavors_client.list_flavors_with_detail(
                min_disk='invalid_disk')
            flavors = response.entity
            self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_detailed_filter_by_invalid_min_ram(self):
        """The detailed list of flavors should be filtered by RAM"""
        with self.assertRaises(BadRequest):
            response = self.flavors_client.list_flavors_with_detail(
                min_ram='invalid_ram')
            flavors = response.entity
            self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_filter_by_invalid_min_disk(self):
        """The detailed list of flavors should be filtered by disk space"""
        with self.assertRaises(BadRequest):
            response = self.flavors_client.list_flavors(
                min_disk='invalid_disk')
            flavors = response.entity
            self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_filter_by_invalid_min_ram(self):
        """The detailed list of flavors should be filtered by RAM"""
        with self.assertRaises(BadRequest):
            response = self.flavors_client.list_flavors(min_ram='invalid_ram')
            flavors = response.entity
            self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_detailed_min_disk_larger_than_max_flavor_disk(self):
        """The detailed list of flavors should be filtered by disk space"""
        response = self.flavors_client.list_flavors_with_detail(
            min_disk='99999')
        flavors = response.entity
        self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_detailed_min_ram_larger_than_max_flavor_ram(self):
        """The detailed list of flavors should be filtered by RAM"""
        response = self.flavors_client.list_flavors_with_detail(
            min_ram=self.max_ram+1)
        flavors = response.entity
        self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_min_disk_greater_than_max_flavor_disk(self):
        """The list of flavors should be filtered by disk space"""
        response = self.flavors_client.list_flavors(min_disk=self.max_disk+1)
        flavors = response.entity
        self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_min_disk_greater_than_max_flavor_ram(self):
        """The list of flavors should be filtered by RAM"""
        response = self.flavors_client.list_flavors(min_ram=self.max_ram+1)
        flavors = response.entity
        self.assertEqual(len(flavors), 0)
