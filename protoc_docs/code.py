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

from pypandoc import convert_text

import collections
import textwrap


class MessageStructure(object):
    """A class representing the structure for a proto message.

    This class is its own registry; calling the with the same message name
    will return the same object.
    """
    _registry = {}

    @classmethod
    def get_or_create(cls, name):
        """Return a Message object.

        Args:
            name (str): The fully qualified name of the message (for example:
                ``google.protobuf.SourceCodeInfo``)

        Returns:
            ``MessageStructure``: A ``MessageStructure`` object.
        """
        cls._registry.setdefault(name, cls(name=name))
        return cls._registry[name]

    def __init__(self, name):
        self.name = name
        self.docstring = ''
        self.members = collections.OrderedDict()

    def __hash__(self):
        """Return a hash for this object based on its name.

        This makes MessageStructure objects able to be placed into a set
        to handle de-duplication properly.
        """
        return hash(self.name)

    def __repr__(self):
        tw8 = textwrap.TextWrapper(
            initial_indent=' ' * 8,
            subsequent_indent=' ' * 8,
        )
        tw12 = textwrap.TextWrapper(
            initial_indent=' ' * 12,
            subsequent_indent=' ' * 12,
        )

        answer =  'MessageStructure {\n'
        answer += '    name: {0}\n'.format(self.name)
        answer += '    docstring:\n{0}\n'.format(
            '\n'.join(tw8.wrap(self.docstring)),
        )
        if len(self.members):
            answer += '    members:\n'
        for k, v in self.members.items():
            answer += '        {name}:\n{doc}\n'.format(
                name=k,
                doc='\n'.join(tw12.wrap(v)),
            )
        answer += '}\n'
        return answer

    def get_python_docstring(self):
        tw = textwrap.TextWrapper(
            initial_indent=' ' * 8,
            subsequent_indent=' ' * 8,
        )
        answer = ''

        # Build the beginning of the docstring.
        if self.docstring:
            answer += convert_text(self.docstring, 'rst', format='md')
            if len(self.members):
                answer += '\n\n'

        # Label the properties as such if there are any.
        if len(self.members):
            answer += 'Attributes:\n'

        # Build a note about each property of the message.
        for k, v in self.members.items():
            v = convert_text(v, 'rst', format='md')
            answer += '    %s:\n%s\n' %  (k, '\n'.join(tw.wrap(v)))

        # Done.
        return answer
