from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import memoized
from cloudroast.blockstorage.datasets import \
    BaseDataset, DatasetGeneratorError
from cloudcafe.blockstorage.composites import VolumesAutoComposite


class VolumesDatasets(BaseDataset):
    """Collection of dataset generators for blockstorage data driven tests"""
    volumes = VolumesAutoComposite()

    @classmethod
    @memoized
    def _volume_types(cls):
        """Get volume type list"""
        try:
            return cls.volumes.behaviors.get_volume_types()
        except:
            raise DatasetGeneratorError(
                "Unable to retrieve list of volume types during "
                "data-driven-test setup.")

    @classmethod
    @memoized
    def volume_types(
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
