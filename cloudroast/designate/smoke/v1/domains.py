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

import json

from cafe.drivers.unittest.decorators import tags
from cloudcafe.common.tools.datagen import rand_name

from cloudroast.designate.fixtures import DomainsFixture


class DomainTest(DomainsFixture):

    @tags('smoke', 'positive')
    def test_list_domains(self):
        self.create_domain()
        list_resp = self.domain_client.list_domains()
        self.assertEquals(list_resp.status_code, 200)
        self.assertGreater(len(list_resp.entity), 0)

        domains = list_resp.entity
        for domain in domains:
            get_resp = self.domain_client.get_domain(domain.id)
            self.assertEquals(get_resp.status_code, 200)

    @tags('smoke', 'positive')
    def test_create_domain(self):
        create_resp = self.create_domain()
        self.assertEquals(create_resp.status_code, 200)

        get_resp = self.domain_client.get_domain(create_resp.entity.id)
        self.assertEquals(get_resp.status_code, 200)

    @tags('smoke', 'positive')
    def test_update_domain(self):
        name, email = self.domain_behaviors._prepare_domain_and_email()
        create_resp = self.create_domain(name=name, email=email)
        domain_id = create_resp.entity.id

        # the updated email address must have the same domain
        new_email = "new_" + email
        update_resp = self.domain_behaviors.update_domain(domain_id=domain_id,
                                                          email=new_email,
                                                          name=name)
        self.assertEquals(update_resp.status_code, 200)

    @tags('smoke', 'positive')
    def test_delete_domain(self):
        create_resp = self.create_domain()
        domain_id = create_resp.entity.id

        del_resp = self.domain_client.delete_domain(domain_id)
        self.assertEquals(del_resp.status_code, 200)

    @tags('smoke', 'positive')
    def test_list_domain_servers(self):
        create_resp = self.create_domain()
        domain_id = create_resp.entity.id

        list_resp = self.domain_client.list_domain_servers(domain_id)
        self.assertEquals(list_resp.status_code, 200)

        servers = list_resp.entity
        self.assertGreater(len(servers), 0)
