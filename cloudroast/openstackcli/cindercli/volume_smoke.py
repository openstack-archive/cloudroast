from cafe.drivers.unittest.decorators import \
    DataDrivenFixture, data_driven_test

from cloudroast.openstackcli.cindercli.fixtures import \
    CinderCLI_Datasets, CinderTestFixture


@DataDrivenFixture
class CinderCLI_VolumeSmoke(CinderTestFixture):

    @data_driven_test(CinderCLI_Datasets.volume_types())
    def ddtest_create_volume(self, volume_type_name, volume_type_id):
        name = self.random_volume_name()
        size = self.cinder.api.config.min_volume_size
        resp = self.cinder.cli.client.create_volume(
            size=size, volume_type=volume_type_id,display_name=name)

        self.assertIsNotNone(
            resp.entity, 'Could not parse cinder create response')

        self.assertEquals(
            resp.return_code, 0, "Cinder command returned an error code.")

        volume = resp.entity

        self.addCleanup(self.cinder.cli.client.delete_volume, volume.id_)

        self.assertEqual(size, volume.size, "Volume size reported incorrectly")
        self.assertEqual(
            name, volume.display_name,
            "Volume display name reported incorrectly")

    @data_driven_test(CinderCLI_Datasets.volume_types())
    def ddtest_delete_volume_by_id(self, volume_type_name, volume_type_id):
        # setup
        volume = self.cinder.cli.behaviors.create_available_volume(
            type_=volume_type_id)
        resp = self.cinder.cli.client.delete_volume(volume.id_)

        self.assertEquals(
            len(resp.standard_out), 0,
            "Volume delete returned output on standard error")
        self.addCleanup(self.cinder.cli.client.delete_volume, volume.id_)

        self.assertTrue(
            self.cinder.cli.behaviors.wait_for_volume_delete(volume.id_),
            "Could not confirm that volume {0} was deleted".format(volume.id_))
