from cafe.drivers.unittest.decorators import \
    data_driven_test, DataDrivenFixture, tags
from cloudcafe.blockstorage.datasets import BlockstorageDatasets

from cloudroast.blockstorage.volumes_api.integration.oscli.fixtures \
    import NovaCLI_IntegrationFixture

volume_type_complete_dataset = BlockstorageDatasets.volume_types()


@DataDrivenFixture
class NovaCLI_VolumesSmoke(NovaCLI_IntegrationFixture):

    @tags('cinder-only')
    @data_driven_test(volume_type_complete_dataset)
    def ddtest_create_minimum_sized_volume(
            self, volume_type_name, volume_type_id):

        size = self.volumes.behaviors.get_configured_volume_type_property(
            "min_size", id_=volume_type_id, name=volume_type_name)
        volume = self.new_volume(size=size, volume_type=volume_type_id)
        assert int(volume.size) == int(size), "Volume was the wrong size"

    @tags('cinder-only')
    @data_driven_test(volume_type_complete_dataset)
    def ddtest_delete(self, volume_type_name, volume_type_id):

        volume = self.new_volume(volume_type=volume_type_id)
        resp = self.nova.client.volume_delete(volume.id_)
        assert resp.return_code == 0, 'Unable to delete volume'
