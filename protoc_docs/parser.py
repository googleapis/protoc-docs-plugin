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

    def find_insertions(self):
        """Find valid insertions and iterate over them.

        Yields:
            tuple([str, str, str]): A tuple of length 3 with the filename,
                insertion point name, and content.
        """
        # Iterate over each proto file.
        for proto_file in self._request.proto_file:
            # Sanity check: If this proto file has no source code
            # information, skip it.
            if not proto_file.source_code_info:
                continue
            src = proto_file.source_code_info

            # Iterate over each location in the source info.
            for loc in src.location:
                # Sanity check: If there are no comments, then we do not
                # actually care about this location.
                if not loc.leading_comments and not loc.trailing_comments:
                    continue

                # Sanity check: For now, we are only able to do anything
                # useful with comments for message types (path: 4), enum
                # types (path: 5), and services (path: 6).
                #
                # Therefore, ignore anything else.
                if loc.path[0] not in (4, 5, 6):
                    continue

                # Never attempt to do anything with any path with 999 in it.
                if 999 in loc.path:
                    continue

                # We have comments. We need to determine what the thing is
                # that they are attached to.
                filename = proto_file.name.split('/')[-1].replace(
                    '.proto',
                    '_pb2.py',
                )
                import pdb ; pdb.set_trace()
                insertion_point = self.parse_path(proto_file, list(loc.path))

    def parse_path(self, cursor, path):
        """Return the correct thing for a full path.

        Args:
            message (:class:`google.protobuf.Message`): A Message.
            path (list): The path; a list of numbers. See descriptor.proto
                for complete documentation.

        Returns:
            str: The correct insertion point name.
        """
        # The first two ints in the path represent what kind of thing
        # the comment is attached to (message, enum, or service) and the
        # order of declaration in the file.
        #
        # e.g. [4, 0, ...] would refer to the *first* message, [4, 1, ...] to
        # the second, etc.
        for field in cursor._fields.keys():
            if field.number == path[0]:
                break
        cursor = getattr(cursor, field.name)[path[1]]
        path = path[2:]

        # If the length of the path is 2 or greater, call this method
        # recursively.
        if len(path) >= 2:
            return self.parse_path(cursor, path)

        # At this point we might be done.
        # If we are, return the appropriate name.
        if not path:
            return 'class_scope:%s.%s' % (proto_file.package, field.name)

        import pdb ; pdb.set_trace()
