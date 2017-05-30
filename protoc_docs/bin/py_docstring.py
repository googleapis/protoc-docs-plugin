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
from protoc_docs.models import CodeGeneratorResponse


def main(input_file=sys.stdin, output_file=sys.stdout):
    """Parse a CodeGeneratorRequest and return a CodeGeneratorResponse."""

    # Ensure we are getting a bytestream, and writing to a bytestream.
    if hasattr(input_file, 'buffer'):
        input_file = input_file.buffer
    if hasattr(output_file, 'buffer'):
        output_file = output_file.buffer

    # Instantiate a parser.
    parser = CodeGeneratorParser.from_input_file(input_file)

    # Find all the docs and amalgamate them together.
    comment_data = {}
    for filename, message_structure in parser.find_docs():
        comment_data.setdefault(filename, set())
        comment_data[filename].add(message_structure)

    # Iterate over the data that came back and parse it into a single,
    # coherent CodeGeneratorResponse.
    answer = []
    for fn, structs in comment_data.items():
        for struct in structs:
            answer.append(CodeGeneratorResponse.File(
                name=fn.replace('.proto', '_pb2.py'),
                insertion_point='class_scope:%s' % struct.name,

                # Seriously, protoc, an insertion point but no trailing
                # comma before it?
                content=',\n__doc__ = """{docstring}""",'.format(
                    docstring=struct.get_python_docstring(),
                ),
            ))
    cgr = CodeGeneratorResponse(file=answer)
    output_file.write(cgr.SerializeToString())
