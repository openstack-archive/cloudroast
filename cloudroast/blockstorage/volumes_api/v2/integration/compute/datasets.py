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

from random import shuffle

from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import memoized

from cloudroast.blockstorage.datasets import DatasetGeneratorError
from cloudroast.blockstorage.volumes_api.v2.datasets import VolumesDatasets
from cloudroast.blockstorage.volumes_api.v2.composites import VolumesComposite
from cloudroast.blockstorage.volumes_api.v2.integration.compute.composites \
    import ImagesComposite


class ComputeDatasets(VolumesDatasets):
    """Collection of dataset generators for blockstorage-images integration
    data driven tests
    """

    @classmethod
    @memoized
    def _images(cls):
        """Get images list"""

        images = ImagesComposite()
        resp = images.client.list_images_with_detail()
        if not resp.ok:
            raise DatasetGeneratorError(
                "Unable to retrieve list of images during data-driven-test "
                "setup")

        if resp.entity is None:
            raise DatasetGeneratorError(
                "Unable to retrieve list of images during data-driven-test "
                "setup: response did not deserialize")

        return resp.entity

    @classmethod
    def images_by_volume_type(
            cls, max_datasets=None, randomize=False, image_filter=None,
            volume_type_filter=None):
        """Returns a DatasetList of permuations of Volume Types and Images.
        Requests all available images and volume types from API, and applies
        image_filter and volume_type_filter if provided.
        Filters should be dictionaries with model attributes as keys and
        lists of attributes as key values
        """

        image_list = cls._filter_model_list(cls._images(), image_filter)
        volume_type_list = cls._filter_model_list(
            cls._volume_types(), volume_type_filter)

        # Create dataset from all combinations of all images and volume types
        dataset_list = DatasetList()
        for vol_type in volume_type_list:
            for img in image_list:
                data = {'volume_type': vol_type,
                        'image': img}
                testname = "{0}_volume_from_{1}_image".format(
                    vol_type.name,
                    str(img.name).replace(" ", "_"))
                dataset_list.append_new_dataset(testname, data)

        # Apply modifiers
        if randomize:
            shuffle(dataset_list)

        if max_datasets:
            dataset_list = dataset_list[:max_datasets]

        return dataset_list

    @classmethod
    def configured_images_by_volume_type(
            cls, max_datasets=None, randomize=None):
        """Returns a DatasetList of permuations of Volume Types and Images.
        Requests all available images and volume types from API, and applies
        pre-configured image and volume_type filters.
        """

        volumes = VolumesComposite()
        image_filter = volumes.config.image_filter
        volume_type_filter = volumes.config.volume_type_filter
        ret = cls.images_by_volume_type(
            max_datasets, randomize, image_filter, volume_type_filter)
        return ret
