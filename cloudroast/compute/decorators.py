"""
Copyright 2015 Rackspace

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

import unittest

from cloudcafe.compute.composites import ComputeComposite


def requires_extension(*extensions):
    """
    @summary: Requires decorator main purpose skips execution of test if the
    extension is not found in list extensions call
    @param extensions: List of Extensions that the test requires
    @type extensions: List
    """
    def decorator(func):
        compute = ComputeComposite()
        rescue_client = compute.extension.client
        list_extensions_response = rescue_client.list_extensions()
        name_list = set()
        if list_extensions_response.entity:
            for element in list_extensions_response.entity:
                name_list.add(element.name)
            if set(extensions).issubset(name_list) is False:
                return unittest.skip("Required extensions are not present for "
                                     "running this test")(func)
            else:
                return func
        else:
            raise Exception('List Exceptions API call malfunctioned. '
                            'Please see logs for details.')
    return decorator
