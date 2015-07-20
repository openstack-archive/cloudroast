from cafe.drivers.unittest.decorators import (
    DataDrivenFixture, data_driven_test)
from cloudcafe.blockstorage.datasets import BlockstorageDatasets

from cloudroast.blockstorage.volumes_api.integration.oscli.fixtures import (
    CinderCLI_IntegrationFixture)


@DataDrivenFixture
class CinderCLI_VolumeSmoke(CinderCLI_IntegrationFixture):

    @data_driven_test(BlockstorageDatasets.volume_types())
    def ddtest_create_minimum_sized_volume(
            self, volume_type_name, volume_type_id):
        size = self.volumes.behaviors.get_configured_volume_type_property(
            "min_size", id_=volume_type_id, name=volume_type_name)
        name = self.random_volume_name()
        resp = self.cinder.client.create(
            size=size, volume_type=volume_type_id, display_name=name)

        self.assertIsNotNone(
            resp.entity, 'Could not parse cinder create response')

        self.assertEquals(
            resp.return_code, 0, "Cinder command returned an error code.")

        volume = resp.entity

        self.addCleanup(self.cinder.client.delete, volume.id_)

        self.assertEqual(
            int(size), int(volume.size), "Volume size reported incorrectly")
        self.assertEqual(
            name, volume.display_name,
            "Volume display name reported incorrectly")

    @data_driven_test(BlockstorageDatasets.volume_types())
    def ddtest_delete_volume_by_id(self, volume_type_name, volume_type_id):
        # setup
        size = self.volumes.behaviors.get_configured_volume_type_property(
            "min_size", id_=volume_type_id, name=volume_type_name)
        volume = self.volumes.behaviors.create_available_volume(
            size=size, volume_type=volume_type_id)

        resp = self.cinder.client.delete(volume.id_)
        self.assertEquals(
            len(resp.standard_out), 0,
            "Volume delete returned output on standard error")
        self.addCleanup(self.cinder.client.delete, volume.id_)

        self.assertTrue(
            self.volumes.behaviors.delete_volume_confirmed(
                volume.id_, size, ),
            "Could not confirm that volume {0} was deleted".format(volume.id_))

    @data_driven_test(BlockstorageDatasets.volume_types())
    def ddtest_delete_volume_by_name(self, volume_type_name, volume_type_id):
        # setup
        size = self.volumes.behaviors.get_configured_volume_type_property(
            "min_size", id_=volume_type_id, name=volume_type_name)

        volume = self.volumes.behaviors.create_available_volume(
            size=size, volume_type=volume_type_id,
            name=self.random_volume_name())

        resp = self.cinder.client.delete(volume.name)
        self.assertEquals(
            len(resp.standard_out), 0,
            "Volume delete returned output on standard error")
        self.addCleanup(self.cinder.client.delete, volume.id_)

        self.assertTrue(
            self.volumes.behaviors.delete_volume_confirmed(volume.name, size),
            "Could not confirm that volume {0} was deleted".format(volume.id_))
