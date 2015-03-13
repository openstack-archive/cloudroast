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
from cloudcafe.compute.common.exceptions import BadRequest, ItemNotFound
from cloudroast.compute.fixtures import ComputeFixture


class FlavorsTest(ComputeFixture):

    @classmethod
    def setUpClass(cls):
        """
        Perform actions that setup the neccesary resources for testing

        The following resources are created during this setup:
            - a list of flavors

        The following data is generated during this setup:
            - The flavor with the most RAM
            - The flavor with the most Disk
        """
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
        """
        A list of all flavors contains an expected flavor

        Request a list of available flavors and ensure that the list is
        populated. Get the flavor reference for the flavor set during test
        configuration. Validate that the flavor reference is found in
        the list of flavors.

        The following assertions occur:
            - The flavor list for the test user is not empty
            - The flavor set during test configuration is found in the list
              of available flavors
        """
        response = self.flavors_client.list_flavors()
        flavors = response.entity
        self.assertTrue(len(flavors) > 0)
        response = self.flavors_client.get_flavor_details(self.flavor_ref)
        flavor = response.entity
        flavor_ids = [x.id for x in flavors]
        self.assertIn(flavor.id, flavor_ids,
                      "The expected flavor: %s was not found in "
                      "the flavor list" % flavor.id)

    @tags(type='smoke', net='no')
    def test_list_flavors_with_detail(self):
        """
        A detailed list of all flavors should contain the expected flavor

        Request a list of available flavors and their details. Ensure
        that the list is populated. Get the flavor reference for the
        flavor set during test configuration. Validate that the flavor
        reference is found in the list of flavors.

        The following assertions occur:
            - The detailed flavor list for the test user is not empty
            - The flavor set during test configuration is found in the list
              of available flavors
        """
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity
        self.assertTrue(len(flavors) > 0)
        response = self.flavors_client.get_flavor_details(self.flavor_ref)
        flavor = response.entity
        self.assertIn(flavor, flavors)

    @tags(type='smoke', net='no')
    def test_get_flavor(self):
        """
        A test user should be able to get details for a flavor

        Get detailed information about the flavor set during test
        configuration. Ensure that that the flavor ref returned in the
        details matches the flavor ref set during test configuration.

        The following assertions occur:
            - The flavor ref returned in the flavor details using the configured
              flavor ref matches the flavor ref set during test configuration.
        """
        response = self.flavors_client.get_flavor_details(self.flavor_ref)
        flavor = response.entity
        self.assertEqual(self.flavor_ref, flavor.id)

    @tags(type='negative', net='no')
    def test_get_non_existent_flavor(self):
        """
        A test user should not be able to get details for a nonexistent flavor

        Request detailed flavor information about a nonexistent image with an id
        value of "999". Ensure that the flavor is not found.
        """
        try:
            self.flavors_client.get_flavor_details(999)
            self.fail('No exception thrown for a non-existent flavor id')
        except ItemNotFound:
            pass

    @tags(type='positive', net='no')
    def test_list_flavors_limit_results(self):
        """
        A request for a list of flavors should respect the page size requested

        Get a list of flavors with a page size of 1. Validate that
        the flavor list returned contains only one flavor.

        The following assertions occur:
            - The flavor list requested by the test user with a page size of 1
              contains only one flavor
        """
        response = self.flavors_client.list_flavors(limit=1)
        flavors = response.entity
        self.assertEqual(1, len(flavors))

    @tags(type='positive', net='no')
    def test_list_flavors_detailed_limit_results(self):
        """
        A detailed list of flavors should respect the page size requested

        Get a detailed list of flavors with a page size of 1. Validate that
        the flavor list returned contains only one flavor.

        The following assertions occur:
            - The detailed flavor list requested by the test user with a page
              size of 1 contains only one flavor
        """
        response = self.flavors_client.list_flavors_with_detail(limit=1)
        flavors = response.entity
        self.assertEqual(1, len(flavors))

    @tags(type='positive', net='no')
    def test_list_flavors_using_marker(self):
        """
        A list of flavors should respect the marker parameter

        Get a list of flavors and ensure it is not empty. Get
        the first flavor in the list. Use the selected flavor as the
        marker parameter to request a list of flavors. The returned
        list should not contain the selected flavor.

        The following assertions occur:
            - The list of flavors the test user requests is populated
            - A list of flavors does not contain the selected flavor used as a
              marker
        """
        response = self.flavors_client.list_flavors()
        flavors = response.entity
        self.assertGreater(len(flavors), 0, 'Flavors list is empty')
        flavor_marker = flavors[0]

        response = self.flavors_client.list_flavors(marker=flavor_marker.id)
        filtered_flavors = response.entity
        self.assertNotIn(flavor_marker, filtered_flavors,
                         msg='Filtered flavor was incorrectly '
                             'included in the list of returned flavors')

    @tags(type='positive', net='no')
    def test_list_flavors_detailed_using_marker(self):
        """
        A detailed list of flavors should respect the marker parameter

        Get a detailed list of flavors and ensure it is not empty. Get
        the first flavor in the list. Use the selected flavor as the
        marker parameter to request a detailed list of flavors. The returned
        list should not contain the selected flavor.

        The following assertions occur:
            - The list of flavors the test user requests is populated
            - A detailed list of flavors does not contain the selected flavor
              used as a marker
        """
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity
        self.assertGreater(len(flavors), 0, 'Flavors list is empty')
        flavor_marker = flavors[0]

        response = self.flavors_client.list_flavors_with_detail(
            marker=flavor_marker.id)
        filtered_flavors = response.entity
        self.assertNotIn(flavor_marker, filtered_flavors,
                         msg='Filtered flavor was incorrectly '
                             'included in the list of returned flavors')

    @tags(type='positive', net='no')
    def test_list_flavors_detailed_filter_by_min_disk(self):
        """
        A detailed list of flavors should respect the minimum disk value

        Get a detailed list of flavors. Sort the list in ascending size
        based on disk size. Get the second flavor in the list. Use the
        selected flavor as the minimum disk value to request a detailed
        list of flavors. The returned list should contain only flavors
        with equal or greater disk size than the selected flavor.

        The following assertions occur:
            - A detailed list of flavors only contains flavors with equal or
              greater disk size than the value used as the minimum disk value
        """
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity

        # Sort the flavors by disk size in ascending order
        flavors.sort(key=lambda k: int(k.disk))

        # Remove any flavors from the list that are smaller than the
        # flavor with the second smallest disk size
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
        """
        A detailed list of flavors should respect the minimum RAM value

        Get a detailed list of flavors. Sort the list in ascending size
        based on RAM. Get the second flavor in the list. Use the selected
        flavor as the minimum RAM value to request a detailed list of
        flavors. The returned list should contain only flavors with equal
        or greater RAM value than the selected flavor.

        The following assertions occur:
            - A detailed list of flavors only contains flavors with equal or
              greater RAM value than the value used as the minimum RAM value
        """
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity

        # Sort the flavors by RAM in ascending order
        flavors.sort(key=lambda k: int(k.ram))

        # Remove any flavors from the list that are smaller than the
        # flavor with the second smallest RAM size
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
        """
        A list of flavors should respect the minimum disk value

        Get a list of flavors. Sort the list in ascending size based on
        disk size. Get the second flavor in the list. Use the selected
        flavor as the minimum disk value to request a list of flavors.
        The returned list should contain only flavors with equal or
        greater disk size than the selected flavor.

        The following assertions occur:
            - A list of flavors only contains flavors with equal or greater
              disk size than the value used as the minimum disk value
        """
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity

        # Sort the flavors by disk size in ascending order
        flavors.sort(key=lambda k: int(k.disk))

        # Remove any flavors from the list that are smaller than the
        # flavor with the second smallest disk size
        filter_criteria = lambda x: int(x.disk) >= int(flavors[1].disk)
        expected_flavors = filter(filter_criteria, flavors)
        response = self.flavors_client.list_flavors(min_disk=flavors[1].disk)
        actual_flavors = response.entity

        actual_flavor_ids = set([flavor.id for flavor in actual_flavors])
        expected_flavor_ids = set([flavor.id for flavor in expected_flavors])
        self.assertEqual(actual_flavor_ids, expected_flavor_ids)

    @tags(type='positive', net='no')
    def test_list_flavors_filter_by_min_ram(self):
        """
        A list of flavors should respect the minimum RAM value

        Get a list of flavors. Sort the list in ascending size based on
        RAM. Get the second flavor in the list. Use the selected flavor
        as the minimum RAM value to request a detailed list of flavors.
        The returned list should contain only flavors with equal or
        greater RAM size than the selected flavor.

        The following assertions occur:
            - A list of flavors only contains flavors with equal or greater
              RAM value than the value used as the minimum RAM value
        """
        response = self.flavors_client.list_flavors_with_detail()
        flavors = response.entity

        # Sort the flavors by RAM in ascending order
        flavors.sort(key=lambda k: int(k.ram))

        # Remove any flavors from the list that are smaller than the
        # flavor with the second smallest RAM value
        filter_criteria = lambda x: int(x.ram) >= int(flavors[1].ram)
        expected_flavors = filter(filter_criteria, flavors)
        response = self.flavors_client.list_flavors(min_ram=flavors[1].ram)
        actual_flavors = response.entity

        actual_flavor_ids = set([flavor.id for flavor in actual_flavors])
        expected_flavor_ids = set([flavor.id for flavor in expected_flavors])
        self.assertEqual(actual_flavor_ids, expected_flavor_ids)

    @tags(type='negative', net='no')
    def test_list_flavors_detailed_filter_by_invalid_min_disk(self):
        """
        A detailed list of flavors cannot be gotten with invalid min disk size

        Validate that if the value "invalid_disk" is used as the minimum disk
        size when requesting a detailed list of flavors a 'Bad Request' error
        is returned.

        The following assertions occur:
            - The list flavors with detail request raises a 'Bad Request'
              error when given an invalid value for the minimum disk size.
        """
        with self.assertRaises(BadRequest):
            response = self.flavors_client.list_flavors_with_detail(
                min_disk='invalid_disk')
            flavors = response.entity
            self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_detailed_filter_by_invalid_min_ram(self):
        """
        A detailed list of flavors cannot be gotten with invalid min RAM value

        Validate that if the value "invalid_ram" is used as the minimum RAM
        value when requesting a detailed list of flavors a 'Bad Request' error
        is returned.

        The following assertions occur:
            - The list flavors with detail request raises a 'Bad Request'
              error when given an invalid value for the minimum ram value.
        """
        with self.assertRaises(BadRequest):
            response = self.flavors_client.list_flavors_with_detail(
                min_ram='invalid_ram')
            flavors = response.entity
            self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_filter_by_invalid_min_disk(self):
        """
        A list of flavors cannot be gotten with invalid min disk size

        Validate that if the value "invalid_disk" is used as the minimum disk
        size when requesting a list of flavors a 'Bad Request' error is
        returned.

        The following assertions occur:
            - The list flavors with detail request raises a 'Bad Request'
              error when given an invalid value for the minimum disk size.
        """
        with self.assertRaises(BadRequest):
            response = self.flavors_client.list_flavors(
                min_disk='invalid_disk')
            flavors = response.entity
            self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_filter_by_invalid_min_ram(self):
        """
        A list of flavors cannot be gotten with invalid min RAM value

        Validate that if the value "invalid_ram" is used as the minimum RAM
        value when requesting a detailed list of flavors a 'Bad Request' error
        is returned.

        The following assertions occur:
            - The list flavors request raises a 'Bad Request' error when
              given an invalid value for the minimum RAM value.
        """
        with self.assertRaises(BadRequest):
            response = self.flavors_client.list_flavors(min_ram='invalid_ram')
            flavors = response.entity
            self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_detailed_min_disk_larger_than_max_flavor_disk(self):
        """
        A detailed list of flavors should respect the minimum disk value

        Use the flavor with the largest disk size selected during setup
        to generate a disk size greater than the disk sizes of any available
        flavor. Use this value as the minimum disk size to request a list
        of flavors. The returned list should contain no flavors.

        The following assertions occur:
            - A detailed list of flavors using a minimum disk size value greater
              than any of the available flavor disk sizes should be empty
        """
        response = self.flavors_client.list_flavors_with_detail(
            min_disk='99999')
        flavors = response.entity
        self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_detailed_min_ram_larger_than_max_flavor_ram(self):
        """
        A detailed list of flavors should respect the minimum RAM value

        Use the flavor with the largest RAM value selected during setup
        to generate a RAM value greater than the RAM value of any available
        flavor. Use this value as the minimum RAM value to request a detailed
        list of flavors. The returned list should contain no flavors.

        The following assertions occur:
            - A detailed list of flavors using a minimum RAM value greater
              than any of the available flavor RAM values should be empty
        """
        response = self.flavors_client.list_flavors_with_detail(
            min_ram=self.max_ram+1)
        flavors = response.entity
        self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_min_disk_greater_than_max_flavor_disk(self):
        """
        A list of flavors should respect the minimum disk value

        Use the flavor with the largest disk size selected during setup
        to generate a disk size greater than the disk sizes of any available
        flavor. Use this value as the minimum disk size to request a list
        of flavors. The returned list should contain no flavors.

        The following assertions occur:
            - A list of flavors using a minimum disk size value greater
              than any of the available flavor disk sizes should be empty
        """
        response = self.flavors_client.list_flavors(min_disk=self.max_disk+1)
        flavors = response.entity
        self.assertEqual(len(flavors), 0)

    @tags(type='negative', net='no')
    def test_list_flavors_min_disk_greater_than_max_flavor_ram(self):
        """
        A list of flavors should respect the minimum RAM value

        Use the flavor with the largest RAM value selected during setup
        to generate a RAM value greater than the RAM value of any available
        flavor. Use this value as the minimum RAM value to request a list
        of flavors. The returned list should contain no flavors.

        The following assertions occur:
            - A list of flavors using a minimum RAM value greater
              than any of the available flavor RAM values should be empty
        """
        response = self.flavors_client.list_flavors(min_ram=self.max_ram+1)
        flavors = response.entity
        self.assertEqual(len(flavors), 0)
