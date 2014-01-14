from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import memoized
from cloudroast.blockstorage.volumes_api.v2.composites import VolumesComposite


class VolumesDatasets(object):
    """Collection of dataset generators for blockstorage data driven tests"""

    @classmethod
    @memoized
    def volume_types(cls):
        """Returns a DatasetList of Volume Type names and id's"""

        volumes = VolumesComposite()
        resp = volumes.client.list_all_volume_types()
        assert resp.ok, (
            "Unable to retrieve list of volume types during data-driven-test "
            "setup")

        assert resp.entity is not None, (
            "Unable to retrieve list of volume types during data-driven-test "
            "setup: response did not deserialize")

        volume_type_list = resp.entity
        dataset_list = DatasetList()
        for vol_type in volume_type_list:
            data = {'volume_type_name': vol_type.name,
                    'volume_type_id': vol_type.id_}
            dataset_list.append_new_dataset(vol_type.name, data)
        return dataset_list
