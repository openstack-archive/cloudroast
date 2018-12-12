from qe_coverage.opencafe_decorators import tags, unless_coverage

from cafe.drivers.unittest.decorators import \
    data_driven_test, DataDrivenFixture
from cloudcafe.blockstorage.datasets import BlockstorageDatasets
from cloudroast.blockstorage.volumes_api.integration.oscli.fixtures \
    import NovaCLI_IntegrationFixture

volume_type_complete_dataset = BlockstorageDatasets.volume_types()


@DataDrivenFixture
class NovaCLI_IntegrationSmoke(NovaCLI_IntegrationFixture):

    _class_cleanup_tasks = []

    @unless_coverage
    @classmethod
    def setUpClass(cls):
        super(NovaCLI_IntegrationSmoke, cls).setUpClass()

        # Create test server
        cls.test_server = cls.new_server()

    @unless_coverage
    def setUp(self):
        super(NovaCLI_IntegrationSmoke, self).setUp()

    @tags('positive')
    @data_driven_test(volume_type_complete_dataset)
    def ddtest_create_minimum_sized_volume(
            self, volume_type_name, volume_type_id):
        size = self.volumes.behaviors.get_configured_volume_type_property(
            "min_size", id_=volume_type_id, name=volume_type_name)
        volume = self.new_volume(size=size, volume_type=volume_type_id)
        assert int(volume.size) == int(size), "Volume was the wrong size"

    @tags('positive')
    @data_driven_test(volume_type_complete_dataset)
    def ddtest_create_maximum_sized_volume(
            self, volume_type_name, volume_type_id):
        size = self.volumes.behaviors.get_configured_volume_type_property(
            "max_size", id_=volume_type_id, name=volume_type_name)
        volume = self.new_volume(size=size, volume_type=volume_type_id)
        assert int(volume.size) == int(size), "Volume was the wrong size"

    @tags('nova-integration', 'positive')
    @data_driven_test(volume_type_complete_dataset)
    def ddtest_auto_attach(self, volume_type_name, volume_type_id):
        volume = self.new_volume(volume_type=volume_type_id)
        self.verified_volume_attach(self.test_server.id_, volume.id_)

    @tags('nova-integration', 'positive')
    @data_driven_test(volume_type_complete_dataset)
    def ddtest_detach(self, volume_type_name, volume_type_id):
        # Create volume and attach it to the test server
        volume = self.new_volume(volume_type=volume_type_id)
        self.verified_volume_attach(
            self.test_server.id_, volume.id_, add_cleanup=True)

        # Issue detach
        resp = self.nova.client.volume_detach(self.test_server.id_, volume.id_)
        assert resp.return_code == 0, (
            'Unable to detach volume, return code was {0}'.format(
                resp.return_code))

    @tags('positive')
    @data_driven_test(volume_type_complete_dataset)
    def ddtest_delete(self, volume_type_name, volume_type_id):
        volume = self.new_volume(volume_type=volume_type_id)
        resp = self.nova.client.volume_delete(volume.id_)
        assert resp.return_code == 0, 'Unable to delete volume'

    @unless_coverage
    def tearDown(self):
        super(NovaCLI_IntegrationSmoke, self).tearDown()

    @unless_coverage
    @classmethod
    def tearDownClass(cls):
        super(NovaCLI_IntegrationSmoke, cls).tearDownClass()
