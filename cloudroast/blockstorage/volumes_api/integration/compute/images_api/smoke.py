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
from cafe.drivers.unittest.decorators import \
    data_driven_test, DataDrivenFixture, tags

from cloudroast.blockstorage.volumes_api.integration.compute.fixtures \
    import VolumesImagesIntegrationFixture
from cloudroast.blockstorage.volumes_api.integration.compute.datasets \
    import ComputeDatasets


@DataDrivenFixture
class VolumesImagesIntegrationSmoke(VolumesImagesIntegrationFixture):

    # Creates a single test from a random volume type and image
    @data_driven_test(ComputeDatasets.images_by_volume_type(
        max_datasets=1, randomize=True))
    @tags('single-random-dataset')
    def ddtest_single_random_dataset_create(self, volume_type, image):
        """Create a single volume_type volume from image"""
        self.create_volume_from_image_test(volume_type, image)

    # Creates tests for every combination of volume type and image
    @data_driven_test(ComputeDatasets.images_by_volume_type())
    @tags('complete-dataset')
    def ddtest_complete_dataset_create(self, volume_type, image):
        """Create a single volume_type volume from image"""
        self.create_volume_from_image_test(volume_type, image)

    # Creates tests from a configuration-limited subset of all
    # possible combinations of volume types and images
    @data_driven_test(ComputeDatasets.configured_images_by_volume_type())
    @tags('configured-dataset')
    def ddtest_configured_dataset_create(self, volume_type, image):
        """Create a single volume_type volume from image"""
        self.create_volume_from_image_test(volume_type, image)
