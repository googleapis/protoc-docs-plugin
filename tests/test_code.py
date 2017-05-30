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

import unittest

from protoc_docs import code


class MessageStructureTests(unittest.TestCase):
    def setUp(self):
        code.MessageStructure._registry.clear()

    def test_get_or_create_same_name(self):
        a = code.MessageStructure.get_or_create('foo')
        b = code.MessageStructure.get_or_create('foo')
        assert isinstance(a, code.MessageStructure)
        assert isinstance(b, code.MessageStructure)
        assert a is b

    def test_get_or_create_different_names(self):
        a = code.MessageStructure.get_or_create('foo')
        c = code.MessageStructure.get_or_create('bar')
        assert a is not c

    def test_hash_method(self):
        foo = code.MessageStructure.get_or_create('foo')
        assert hash(foo) == hash('foo')

    def test_get_python_docstring(self):
        foo = code.MessageStructure.get_or_create('foo')
        foo.docstring = 'Make a foo.'
        foo.members['bar'] = 'The spam of the eggs.'
        docstring = foo.get_python_docstring()
        assert 'Make a foo.' in docstring
        assert 'Properties:' in docstring
        assert 'bar:' in docstring
        assert 'The spam of the eggs.' in docstring

    def test_get_python_docstring_no_overall_docstring(self):
        foo = code.MessageStructure.get_or_create('foo')
        foo.members['bar'] = 'The spam of the eggs.'
        docstring = foo.get_python_docstring()
        assert 'foo' not in docstring
        assert 'Properties:' in docstring
        assert 'bar:' in docstring
        assert 'The spam of the eggs.' in docstring

    def test_get_python_docstring_no_properties(self):
        foo = code.MessageStructure.get_or_create('foo')
        foo.docstring = 'Make a foo.'
        docstring = foo.get_python_docstring()
        assert 'Make a foo.' in docstring
        assert 'Properties:' not in docstring
