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

import io
import os
import unittest

import mock

from protoc_docs.bin import py_docstring


class PyDocstringTests(unittest.TestCase):
    def test_input_file(self):
        # Set up mocks.
        input_file = mock.Mock(spec=io.BytesIO)
        input_file.read.return_value = b''
        output_file = mock.Mock(spec=io.BytesIO)

        # Read the empty file; we should get empty output.
        py_docstring.main(input_file=input_file, output_file=output_file)
        output_file.write.assert_called_once_with(b'')

    def test_input_file_buffer(self):
        # Ensure that the .buffer attribute is used if present.
        # This makes sys.stdin and sys.stdout be valid things to use
        # in Python 3.
        input_file = mock.Mock(spec=['buffer'])
        input_file.buffer = mock.Mock(spec=io.BytesIO)
        input_file.buffer.read.return_value = b''
        output_file = mock.Mock(spec=['buffer'])
        output_file.buffer = mock.Mock(spec=io.BytesIO)

        # Read the empty file; we should get empty output.
        py_docstring.main(input_file=input_file, output_file=output_file)
        output_file.buffer.write.assert_called_once_with(b'')

    def test_real_input_file(self):
        output_file = io.BytesIO()

        # Use the input file for descriptor.proto.
        curdir = os.path.realpath(os.path.dirname(__file__))
        with io.open('%s/data/input_buffer' % curdir, 'rb') as file_:
            py_docstring.main(input_file=file_, output_file=output_file)

        # Just ensure that the bytestream is the appropriate length.
        # This is a terrible test. :-/
        assert len(output_file.getvalue()) == 25294
