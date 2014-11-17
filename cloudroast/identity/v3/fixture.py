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
