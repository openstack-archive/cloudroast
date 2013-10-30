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
from cloudroast.images.v2.fixtures import ImagesV2Fixture


class GetSchemaRateLimitTest(ImagesV2Fixture):
    """Test the rate limits for retrieval of schema details for images."""

    @tags(type='positive')
    def test_get_image_schema_glance_default(self):
        """Perform GET on /schemas 1001 times in 1 minute as GlanceDefault user
        to hit rate limit.

        1) Get image schema as GlanceDefault user 1000 times in 1 minute
        2) Verify the response status code is 200
        3) Get image schema as GlanceDefault user 1 more time
        4) Verify the response status code is 429
        """

        count = self.config.get_schema_count

        for x in range(count):
            response = self.api_client.get_image_schema()
            self.assertEqual(response.status_code, 200)
            #TODO: Catch the exception if rate limit is it and pass test?

        response = self.api_client.get_image_schema()
        self.assertEqual(response.status_code, 429)
