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
from cafe.drivers.unittest.decorators import tags
from cloudcafe.cloudkeep.common.states import VerificationsStates
from cloudroast.cloudkeep.barbican.fixtures import VerificationsFixture


class VerificationsAPI(VerificationsFixture):

    @tags(type='positive')
    def test_create_verification(self):
        """Covers creating a verification."""
        resp = self.behaviors.create_verification_overriding_cfg(
            resource_type="image",
            resource_ref="http://www.smoke_testing_create_verification.com",
            resource_action="vm_attach",
            impersonation_allowed=False)
        self.assertEqual(resp.status_code, 202)

    @tags(type='positive')
    def test_get_verification(self):
        """Covers getting a verification."""
        # Create a verification to get
        resp = self.behaviors.create_verification_overriding_cfg(
            resource_type="image",
            resource_ref="http://www.smoke_testing_get_verification.com",
            resource_action="vm_attach",
            impersonation_allowed=False)
        self.assertEqual(resp.status_code, 202)

        # Verify Creation
        get_resp = self.verifications_client.get_verification(resp.id)
        verification = get_resp.entity
        verification_status = (
            verification.status == VerificationsStates.ACTIVE or
            verification.status == VerificationsStates.PENDING)

        self.assertEqual(get_resp.status_code, 200)
        self.assertIsNotNone(verification.verification_ref)
        self.assertTrue(verification_status,
                        "verification not active nor pending")

    @tags(type='positive')
    def test_delete_verification(self):
        """Covers deleting a verification."""
        # Create a verification to delete
        resp = self.behaviors.create_verification_overriding_cfg(
            resource_type="image",
            resource_ref="http://www.smoke_testing_delete_verification.com",
            resource_action="vm_attach",
            impersonation_allowed=False)
        self.assertEqual(resp.status_code, 202)

        del_resp = self.behaviors.delete_verification(resp.id)
        self.assertEqual(del_resp.status_code, 200)

    @tags(type='positive')
    def test_get_verifications(self):
        """Covers getting a list of verifications."""
        # Create 10 verifications
        for i in range(0, 10):
            testURL = \
                "http://www.smoke_testing_get_verifications.com/{0}".format(i)
            self.behaviors.create_verification_overriding_cfg(
                resource_type="image",
                resource_ref=testURL,
                resource_action="vm_attach",
                impersonation_allowed=False)

        resp = self.verifications_client.get_verifications()
        self._check_list_of_verifications(resp=resp, limit=10)
