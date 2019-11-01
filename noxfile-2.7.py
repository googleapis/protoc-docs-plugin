# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import nox


@nox.session
def unit(session):
    """Run the unit tests."""

    session.interpreter = 'python2.7'
    session.install('mock', 'pytest', 'pytest-cov', 'restructuredtext_lint')
    session.install('-e', '.')
    session.run('pytest', '--cov=protoc_docs')
