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
from datetime import datetime

from cloudroast.meniscus.fixtures import (PublishingFixture,
                                          RSyslogPublishingFixture)


class TestPublishToCorrelatorHTTP(PublishingFixture):

    def test_publishing_message(self):
        resp = self.publish_behaviors.publish_from_config()
        self.assertEqual(resp.status_code, 204)


class TestPublishToCorrelatorRSyslog(RSyslogPublishingFixture):

    def test_rsyslog_message(self):
        """Verifying that the syslog endpoint accepts a message"""
        now = datetime.now().isoformat()
        result = self.rsyslog_client.send(priority='46', version='1',
                                          timestamp=now, app_name='cloudcafe',
                                          host_name='test')

        # A socket returns None if it was successful
        self.assertIsNone(result)

        # Make sure the index exists before we continue
        if not self.es_client.wait_for_index(self.tenant_id):
            self.fail('ES index couldn\'t be found after 30 secs')