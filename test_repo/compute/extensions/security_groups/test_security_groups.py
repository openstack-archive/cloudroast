from test_repo.compute.fixtures import ComputeFixture


class SecurityGroupTest(ComputeFixture):

    def test_create_delete_security_group(self):
        resp = self.sec_groups_client.create_security_group(name='test',
                                                            description='test group')
        group = resp.entity
        self.sec_groups_client.delete_security_group(group.id)