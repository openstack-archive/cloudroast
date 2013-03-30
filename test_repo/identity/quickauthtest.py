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

from cloudcafe.identity.v2_0.tokens_api.provider import TokenAPI_Provider

tokens_api = TokenAPI_Provider()
auth_token = tokens_api.behaviors.get_token_by_password()

assert auth_token is not None, 'Auth token returned as None'
assert auth_token != '', 'Auth token returned empty'
