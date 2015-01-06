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

from cafe.drivers.unittest.datasets import DatasetList

from cloudcafe.common.tools.datagen import rand_name, random_int
from cloudcafe.glance.common.types import (
    ImageMemberStatus, ImageStatus, ImageVisibility, SortDirection)


class ImagesDatasetListGenerator(object):
    """@summary: Generator for Images API"""

    @staticmethod
    def ListImagesDatasetList():
        """@summary: Generates a dataset list for the list images request"""

        dataset_list = DatasetList()

        limit = 2
        # TODO: Add marker when able to add image creation, after composite
        member_status = ImageMemberStatus.ACCEPTED
        name = rand_name("name")
        owner = random_int(0, 999999)
        size_max = random_int(900000, 999999)
        size_min = random_int(0, 899999)
        sort_dir = SortDirection.DESCENDING
        sort_key = 'name'
        status = ImageStatus.ACTIVE
        tag = rand_name('tag')
        visibility = ImageVisibility.PUBLIC

        dataset_list.append_new_dataset('passing_no_parameters',
                                        {'params': {}})
        dataset_list.append_new_dataset('passing_limit',
                                        {'params': {'limit': limit}})
        dataset_list.append_new_dataset(
            'passing_member_status',
            {'params': {'member_status': member_status}})
        dataset_list.append_new_dataset('passing_name',
                                        {'params': {'name': name}})
        dataset_list.append_new_dataset('passing_owner',
                                        {'params': {'owner': owner}})
        dataset_list.append_new_dataset('passing_size_max',
                                        {'params': {'size_max': size_max}})
        dataset_list.append_new_dataset('passing_size_min',
                                        {'params': {'size_min': size_min}})
        dataset_list.append_new_dataset('passing_sort_dir',
                                        {'params': {'sort_dir': sort_dir}})
        dataset_list.append_new_dataset('passing_sort_key',
                                        {'params': {'sort_key': sort_key}})
        dataset_list.append_new_dataset('passing_status',
                                        {'params': {'status': status}})
        dataset_list.append_new_dataset('passing_tag',
                                        {'params': {'tag': tag}})
        dataset_list.append_new_dataset('passing_visibility',
                                        {'params': {'visibility': visibility}})

        return dataset_list

    @staticmethod
    def ListImageMembersDatasetList():
        """
        @summary: Generates a dataset list for the list image members
        request
        """

        dataset_list = DatasetList()

        member_status = ImageMemberStatus.ACCEPTED
        owner = random_int(0, 999999)
        visibility = ImageVisibility.PUBLIC

        dataset_list.append_new_dataset('passing_no_parameters',
                                        {'params': {}})
        dataset_list.append_new_dataset(
            'passing_member_status',
            {'params': {'member_status': member_status}})
        dataset_list.append_new_dataset('passing_owner',
                                        {'params': {'owner': owner}})
        dataset_list.append_new_dataset('passing_visibility',
                                        {'params': {'visibility': visibility}})

        return dataset_list
