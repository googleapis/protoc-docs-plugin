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

from __future__ import absolute_import, unicode_literals

import os
import sys

from pypandoc import convert_text
from protoc_docs.parser import CodeGeneratorParser
from google.protobuf.compiler.plugin_pb2 import CodeGeneratorResponse


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
    _BATCH_TOKEN = "CD985272F78311"

    meta_docstrings = []
    meta_structs = []
    for fn, structs in comment_data.items():
        for struct in structs:
            if meta_docstrings:
                meta_docstrings.append("\n%s" % _BATCH_TOKEN)
            meta_docstrings.append(struct.get_meta_docstring())
            meta_structs.append((fn, struct))

    meta_docstring = convert_text("".join(meta_docstrings), 'rst', format='md')
    meta_docstrings = meta_docstring.split("%s" % _BATCH_TOKEN)

    index = 0
    while index < len(meta_structs) and index < len(meta_docstrings):
        fn = meta_structs[index][0]
        struct = meta_structs[index][1]
        answer.append(CodeGeneratorResponse.File(
            name=fn.replace('.proto', '_pb2.py'),
            insertion_point='class_scope:%s' % struct.name,
            content=',\n\'__doc__\': """{docstring}""",'.format(
                docstring=struct.get_python_docstring(meta_docstrings[index]),
            ),
        ))
        index += 1

    for fn in _init_files(comment_data.keys()):
        answer.append(CodeGeneratorResponse.File(
            name=fn,
            content='',
        ))
    cgr = CodeGeneratorResponse(file=answer)
    output_file.write(cgr.SerializeToString())


def _init_files(fns=()):
    """Add init files to every directory generated."""
    files = set()
    for filename in fns:
        if filename.rfind('/') >= 0:
            files.add(
                os.path.join(filename[:filename.rfind('/')], "__init__.py"))
        else:
            files.add("__init__.py")
    return files


if __name__ == '__main__':
    main()
