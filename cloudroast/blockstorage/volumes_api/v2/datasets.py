from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import memoized

from cloudroast.blockstorage.datasets import BaseDataset, DatasetGeneratorError
from cloudroast.blockstorage.volumes_api.v2.composites import VolumesComposite


class VolumesDatasets(BaseDataset):
    """Collection of dataset generators for blockstorage data driven tests"""

    @classmethod
    @memoized
    def _volume_types(cls):
        """Get volume type list"""

        volumes = VolumesComposite()
        resp = volumes.client.list_all_volume_types()
        if not resp.ok:
            raise DatasetGeneratorError(
                "Unable to retrieve list of volume types during "
                "data-driven-test setup.")

        if resp.entity is None:
            raise DatasetGeneratorError(
                "Unable to retrieve list of volume types during "
                "data-driven-test setup: response did not deserialize")

        return resp.entity

    @classmethod
    @memoized
    def volume_type(
            cls, max_datasets=None, randomize=False, volume_type_filter=None):
        """Returns a DatasetList of Volume Type names and id's"""

        volume_type_list = cls._filter_model_list(
            cls._volume_types(), volume_type_filter)
        dataset_list = DatasetList()
        for vol_type in volume_type_list:
            data = {'volume_type_name': vol_type.name,
                    'volume_type_id': vol_type.id_}
            dataset_list.append_new_dataset(vol_type.name, data)
        return dataset_list
