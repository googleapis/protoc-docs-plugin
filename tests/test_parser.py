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

import pytest

from protoc_docs import models
from protoc_docs import parser


curdir = os.path.realpath(os.path.dirname(__file__))


class TestCodeGeneratorParser(unittest.TestCase):
    def test_from_input_file(self):
        with io.open('%s/data/input_buffer' % curdir, 'rb') as file_:
            cgp = parser.CodeGeneratorParser.from_input_file(file_)
        assert isinstance(cgp._request, models.CodeGeneratorRequest)

    def test_constructor_bad_argument(self):
        with pytest.raises(TypeError):
            parser.CodeGeneratorParser(request='foo')

    def test_find_docs(self):
        # Read in a valid request from disk.
        with io.open('%s/data/input_buffer' % curdir, 'rb') as file_:
            cgp = parser.CodeGeneratorParser.from_input_file(file_)

        # Parse the request.
        answer = {}
        for filename, message_structure in cgp.find_docs():
            answer.setdefault(filename, set())
            answer[filename].add(message_structure)

        # Make incredibly basic assertions about the collected data.
        assert len(answer) == 1
        assert len(answer['protos/descriptor.proto']) == 22

    def test_find_docs_no_output_files(self):
        # Read the file, but this time wipe out the list of target output
        # files; this should make no files be written.
        with io.open('%s/data/input_buffer' % curdir, 'rb') as file_:
            cgp = parser.CodeGeneratorParser.from_input_file(file_)
        cgp._request.ClearField('file_to_generate')

        # There should be no data this time.
        answer = {}
        for filename, message_structure in cgp.find_docs():
            answer.setdefault(filename, set())
            answer[filename].add(message_structure)
        assert len(answer) == 0

    def test_find_docs_no_source_info(self):
        # Read the file, but this time wipe out the source code info;
        # the proto specification says this is optional.
        with io.open('%s/data/input_buffer' % curdir, 'rb') as file_:
            cgp = parser.CodeGeneratorParser.from_input_file(file_)
        cgp._request.proto_file[0].ClearField('source_code_info')

        # There should be no data this time.
        answer = {}
        for filename, message_structure in cgp.find_docs():
            answer.setdefault(filename, set())
            answer[filename].add(message_structure)
        assert len(answer) == 0

    def test_is_mixed_case(self):
        cgp = parser.CodeGeneratorParser(models.CodeGeneratorRequest())
        assert cgp._is_mixed_case('foo') is False
        assert cgp._is_mixed_case('FOO') is False
        assert cgp._is_mixed_case('Foo') is True
