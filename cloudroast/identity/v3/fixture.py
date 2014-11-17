from cafe.drivers.unittest.fixtures import BaseTestFixture

from cloudcafe.identity.v3.composites import IdentityV3Composite


class IdentityV3Fixture(BaseTestFixture):

    @classmethod
    def setUpClass(cls):
        """
        Function to create test bed fixture for all the v3 tests. Execute once
        at the beginning of class
        @param cls: instance of class
        """
        super(IdentityV3Fixture, cls).setUpClass()
        cls.v3_composite = IdentityV3Composite(cls.user_config)
        cls.v3_composite.load_clients_and_behaviors()

    def _verify_catalog_response(self, catalog_response):
        """
        Verify the response received for the catalog. Verifying the assertions
        are not none  as the catalog information may change depending on the
        user
        """
        for catalog in catalog_response.entity.catalog:
            self.assertIsNotNone(
                catalog.type, msg='Catalog expected type received {0}'.format(
                    catalog.type))
            for service in catalog.endpoints:
                self.assertIsNotNone(
                    service.interface,
                    msg='Service interface expected received {0}'.format(
                        service.interface))
                self.assertIsNotNone(
                    service.url,
                    msg='Service url expected received {0}'.format(
                        service.url))
                self.assertIsNotNone(
                    service.id,
                    msg='Service id expected received {0}'.format(
                        service.id))
