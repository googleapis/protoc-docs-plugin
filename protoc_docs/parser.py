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

from protoc_docs.models import CodeGeneratorRequest


class CodeGeneratorParser(object):
    """Class to read the code generator request and parse comments.

    This class takes the CodeGeneratorRequest from protoc and
    provides a mapping of relevant comments and the insertion points
    where those comments belong.

    Args:
        request (:class:`protoc_docs_plugin.models.CodeGeneratorRequest`):
            The CodeGeneratorRequest, as an instantiated protobuf object.

    Raises
        TypeError: If the argument is not a CodeGeneratorRequest.
    """
    def __init__(self, request):
        if not isinstance(request, CodeGeneratorRequest):
            type_sent = type(request).__name__
            raise TypeError('Parser must be instantiated with a '
                            'CodeGeneratorRequest; got %s' % type_sent)
        self._request = request

    @classmethod
    def from_input_file(cls, input_file):
        """Return a CodeGeneratorRequest from this protobuf stream.

        Args:
            input_file (Any): A file-like object (requires a ``read`` method).

        Returns:
            CodeGeneratorParser: A parser.
        """
        if hasattr(input_file, 'buffer'):
            input_file = input_file.buffer
        return cls(CodeGeneratorRequest.FromString(input_file.read()))
