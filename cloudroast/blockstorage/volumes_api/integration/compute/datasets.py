from cloudcafe.blockstorage.datasets import ComputeIntegrationDatasets


class bfv_datasets(object):
    """ dataset lists tagged for use with boot-from-volume tests """
    # Create tagged Image dataset

    images = ComputeIntegrationDatasets.images()
    single = ComputeIntegrationDatasets.images(
        max_datasets=1, randomize=True)
    configured = ComputeIntegrationDatasets.configured_images()
    images.apply_test_tags("bfv-exhaustive")
    configured.apply_test_tags("bfv-configured")
    single.apply_test_tags("bfv-single-random")
    images.merge_dataset_tags(configured, single)

    # Create tagged Images by VolumeType dataset
    images_by_volume = \
        ComputeIntegrationDatasets.images_by_volume_type()
    single = ComputeIntegrationDatasets.images_by_volume_type(
        max_datasets=1, randomize=True)
    configured = ComputeIntegrationDatasets.configured_images_by_volume_type()
    images_by_volume.apply_test_tags("bfv-exhaustive")
    configured.apply_test_tags("bfv-configured")
    single.apply_test_tags("bfv-single-random")
    images_by_volume.merge_dataset_tags(configured, single)

    # Create tagged Images by Flavor dataset
    images_by_flavor = \
        ComputeIntegrationDatasets.images_by_flavor()
    single = ComputeIntegrationDatasets.images_by_flavor(
        max_datasets=1, randomize=True)
    configured = ComputeIntegrationDatasets.configured_images_by_flavor()
    images_by_flavor.apply_test_tags("bfv-exhaustive")
    configured.apply_test_tags("bfv-configured")
    single.apply_test_tags("bfv-single-random")
    images_by_flavor.merge_dataset_tags(configured, single)

    # Create tagged Images by Flavor by VolumeType dataset
    flavors_by_images_by_volume_type = \
        ComputeIntegrationDatasets.flavors_by_images_by_volume_type()
    single = ComputeIntegrationDatasets.flavors_by_images_by_volume_type(
        max_datasets=1, randomize=True)
    configured = \
        ComputeIntegrationDatasets.configured_images_by_flavor_by_volume_type()
    flavors_by_images_by_volume_type.apply_test_tags("bfv-exhaustive")
    configured.apply_test_tags("bfv-configured")
    single.apply_test_tags("bfv-single-random")
    flavors_by_images_by_volume_type.merge_dataset_tags(configured, single)
