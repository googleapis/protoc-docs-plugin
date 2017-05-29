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

from __future__ import absolute_import

import sys

from protoc_docs.parser import CodeGeneratorParser


def main(*args, input_file=sys.stdin):
    """Parse a CodeGeneratorRequest and return a CodeGeneratorResponse."""

    # Sanity check: If no arguments were sent, we are using the entrypoint;
    # use sys.argv.
    if not args:
        args = sys.argv[1:]

    # Instantiate a parser.
    parser = CodeGeneratorParser.from_input_file(input_file)

    import io
    with io.open('./out', 'w+') as f:
        f.write(repr(parser._request))
