"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from cloudcafe.cloudkeep.config import CloudKeepRBACRoleConfig
from cloudroast.cloudkeep.barbican.fixtures import SecretsFixture
from cloudroast.cloudkeep.barbican.fixtures import OrdersFixture


class RBACSecretRoles(SecretsFixture):
    rbac_config = CloudKeepRBACRoleConfig()

    @classmethod
    def setUpClass(cls, username=None):
        config = cls._build_editable_keystone_config()
        if username:
            config.username = username

        super(RBACSecretRoles, cls).setUpClass(config)

        # This is very ugly, but I need to aggregate, but not run this fixture
        SecretsFixture.bypass_func = lambda: None
        cls.admin_fixture = SecretsFixture('bypass_func')
        cls.admin_fixture.setUpClass()

    def tearDown(self):
        super(RBACSecretRoles, self).tearDown()
        # Manually deleting admin created secrets as tearDown won't work
        self.admin_fixture.behaviors.delete_all_created_secrets()


class RBACOrderRoles(OrdersFixture):
    rbac_config = CloudKeepRBACRoleConfig()

    @classmethod
    def setUpClass(cls, username=None):
        config = cls._build_editable_keystone_config()
        if username:
            config.username = username

        super(RBACOrderRoles, cls).setUpClass(config)

        # This is very ugly, but I need to aggregate, but not run this fixture
        OrdersFixture.bypass_func = lambda: None
        cls.admin_fixture = OrdersFixture('bypass_func')
        cls.admin_fixture.setUpClass()

    def tearDown(self):
        super(RBACOrderRoles, self).tearDown()
        # Manually deleting admin created orders as tearDown won't work
        self.admin_fixture.behaviors.delete_all_created_orders_and_secrets()
