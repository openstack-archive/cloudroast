from cafe.drivers.unittest.decorators import \
    data_driven_test, DataDrivenFixture, tags
from cloudcafe.blockstorage.datasets import BlockstorageDatasets

from cloudroast.blockstorage.volumes_api.integration.oscli.fixtures \
    import NovaCLI_IntegrationFixture

volume_type_complete_dataset = BlockstorageDatasets.volume_types()


@DataDrivenFixture
class NovaCLI_IntegrationSmoke(NovaCLI_IntegrationFixture):

    @classmethod
    def setUpClass(cls):
        super(NovaCLI_IntegrationSmoke, cls).setUpClass()

        # Create test server
        cls.test_server = cls.new_server()

    @tags('nova-integration')
    @data_driven_test(volume_type_complete_dataset)
    def ddtest_auto_attach(self, volume_type_name, volume_type_id):

        # Create volume and attach it to the test server
        volume = self.new_volume(
            volume_type=volume_type_id, add_cleanup=False)
        self.addCleanup(
            self.nova.client.volume_delete, volume.id_)
        self.verified_volume_attach(self.test_server.id_, volume.id_)

    @tags('nova-integration')
    @data_driven_test(volume_type_complete_dataset)
    def ddtest_detach(self, volume_type_name, volume_type_id):

        # Create volume and attach it to the test server
        volume = self.new_volume(volume_type=volume_type_id)
        self.verified_volume_attach(
            self.test_server.id_, volume.id_, add_cleanup=True)

        # Detach Volume
        resp = self.nova.client.volume_detach(self.test_server.id_, volume.id_)
        assert resp.return_code == 0, (
            'Unable to detach volume, return code was {0}'.format(
                resp.return_code))
