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

import textwrap

from protoc_docs.code import MessageStructure
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
        return cls(CodeGeneratorRequest.FromString(input_file.read()))

    def find_docs(self):
        """Find valid documentation in the proto and iterate over them.

        Yields:
            tuple(str, :class:`protoc_docs.code.MessageStructure`): A tuple,
                of length 2, of filenames and ``MessageStructure`` objects.
                Within the same filename, the same ``MessageStructure`` may
                be yielded more than once (augmented each time). Store a
                set for each filename to handle de-duplication (they are
                hashed appropriately).
        """
        # Iterate over each proto file.
        for proto_file in self._request.proto_file:
            # Ignore any intermediate proto files.
            if proto_file.name not in self._request.file_to_generate:
                continue

            # Sanity check: If this proto file has no source code
            # information, skip it.
            #
            # Descriptor objects lack a meaningful `__nonzero__` method
            # (never stop being awesome, protoc), so we must explicitly
            # check `.ByteSize()`. Which is a method, not a property,
            # because reasons.
            if not proto_file.source_code_info.ByteSize():
                continue
            src = proto_file.source_code_info

            # Iterate over each location in the source info.
            for loc in src.location:
                # Sanity check: If there are no comments, then we do not
                # actually care about this location.
                if not loc.leading_comments and not loc.trailing_comments:
                    continue

                # Sanity check: For now, we are only able to do anything
                # useful with comments for message types (path: 4)
                #
                # Eventually it would be nice to be able to add enum
                # types (path: 5), and services (path: 6).
                #
                # For now, ignore anything else.
                if loc.path[0] != 4:
                    continue

                # We have comments. We need to determine what the thing is
                # that they are attached to.
                filename = proto_file.name
                comment = textwrap.dedent('{leading}\n{trailing}'.format(
                    leading=loc.leading_comments,
                    trailing=loc.trailing_comments,
                ))
                message_structure = self.parse_path(
                    docstring=comment,
                    path=list(loc.path),
                    struct=proto_file,
                )

                # Sanity check: If we got None back for the message_structure,
                # skip. This happens (right now) for enums because there is
                # no insertion point for them and no way to gracefully move
                # on within that method.
                if message_structure is None:
                    continue

                # Yield back what we need.
                yield (filename, message_structure)

    def parse_path(self, struct, path, docstring, message_structure=None):
        """Return the correct thing for a full path.

        Args:
            struct (:class:`google.protobuf.Message`): The structure being
                parsed.
            path (list): The path; a list of numbers. See descriptor.proto
                for complete documentation.
            docstring (str): The comment.
            message_structure (:class:`protoc_docs.code.MessageStructure`):
                Optional. A structure about what is known about the message
                so far. This argument should be considered private and is
                used for recursive calls.

        Returns:
            :class:`protoc_docs.code.MessageStructure`: A ``MessageStructure``
                object. The same object may be returned over multiple
                iterations (for example, if the loop calling this function
                does so for a class and its members); however, these return
                objects are hashable and therefore may safely be added
                to a set to handle de-duplication.
        """
        # The first two ints in the path represent what kind of thing
        # the comment is attached to (message, enum, or service) and the
        # order of declaration in the file.
        #
        # e.g. [4, 0, ...] would refer to the *first* message, [4, 1, ...] to
        # the second, etc.
        field_name = ''
        for field in [i[0] for i in struct.ListFields()]:
            if field.number == path[0]:
                field_name = field.name
        child = getattr(struct, field_name)[path[1]]
        path = path[2:]

        # Ignore enums.
        #
        # We ignore enums because there is no valid insertion point for them,
        # and protoc will not write anything if we offer any invalid
        # insertion point, and there does not seem to be any graceful
        # fallback available (nor is there a way to get a list of insertion
        # points to check against).
        if child.DESCRIPTOR.name == 'EnumDescriptorProto':
            return

        # If applicable, create the MessageStructure object for this.
        if not message_structure:
            message_structure = MessageStructure.get_or_create(
                name='{pkg}.{name}'.format(
                    name=child.name,
                    pkg=struct.package,
                ),
            )

        # If the length of the path is 2 or greater, call this method
        # recursively.
        if len(path) >= 2:
            return self.parse_path(child, path, docstring, message_structure)

        # Write the documentation to the appropriate spot.
        # This entails figuring out what the Message (basically the "class")
        # is, and then whether this is class-level or property-level
        # documentation.
        if message_structure.name.endswith(child.name):
            message_structure.docstring = docstring
        elif self._is_mixed_case(child.name):
            message_structure = MessageStructure.get_or_create(
                name='{parent}.{name}'.format(
                    name=child.name,
                    parent=message_structure.name,
                )
            )
            message_structure.docstring = docstring
        else:
            message_structure.members[child.name] = docstring

        # If the length of the path is now 1...
        #
        # This seems to be a corner case situation. I am not sure what
        # to do for these, and the documentation for odd-numbered paths
        # does not match my observations.
        #
        # Punting. Most of the docs are better than none of them, which was
        # the status quo ante before I wrote this.
        if len(path) == 1:
            return message_structure

        # Done! Return the message structure.
        return message_structure

    def _is_mixed_case(self, string):
        """Return True if the string has mixed case, False otherwise.

        Args:
            string (str): A string. It is assumed to be alpha or alphanumeric,
                but this is not checked.

        Returns:
            bool: Whether the string is mixed case or not.
        """
        if string == string.lower():
            return False
        if string == string.upper():
            return False
        return True
