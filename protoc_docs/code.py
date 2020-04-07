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

import collections
import textwrap
import sys

class MessageStructure(object):
    """A class representing the structure for a proto message.

    This class is its own registry; calling the with the same message name
    will return the same object.
    """
    _registry = {}

    # A random sequence of alphanumerical characters used as a token to
    # concatenate different docstrings together, then make a single pypandoc
    # call and split the returned result again using the same token. This allows
    # us to reduce an average number of calls to a child process (pypandoc
    # starts a pandoc subprocess) from several hundreds to a single call per
    # API. This execution reduces time by several orders of magnitude
    # (from ~10 secs to fractions of a second per API).
    _BATCH_TOKEN = "D55406F6B511E8"

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

    def get_meta_docstring(self):
        meta_docstring = ''

        if self.docstring:
            meta_docstring += self.docstring

        # Concatenate members adding new line and a _BATCH_TOKEN between each
        # member, such that the members list can be restored later (after
        # formatting) by simply splitting the big string by the same
        # _BATCH_TOKEN.
        for k, v in self.members.items():
            if meta_docstring:
                meta_docstring += "\n%s" % MessageStructure._BATCH_TOKEN
            meta_docstring += v

        return meta_docstring

    def get_python_docstring(self, docstring = None):
        tw8 = textwrap.TextWrapper(
            initial_indent=' ' * 8,
            subsequent_indent=' ' * 8,
        )

        tw0 = textwrap.TextWrapper()

        meta_docstring = docstring if docstring else self.get_meta_docstring()

        answer = ''

        # Reconstruct the docstrings list by splitting the meta_docstring
        # by same _BATCH_TOKEN which was used to concatenate them
        meta_vals = meta_docstring.split(MessageStructure._BATCH_TOKEN)
        meta_index = 0
        if self.docstring:
            answer += '\n'.join(tw0.wrap(meta_vals[meta_index]))
            meta_index += 1
            if len(self.members):
                answer += '\n'
        if len(self.members):
            answer += 'Attributes:\n'

        keys = list(self.members.keys())
        keys_index = 0
        while meta_index < len(meta_vals) and keys_index < len(keys):
            v = meta_vals[meta_index]
            k = keys[keys_index]
            answer += '    %s:\n%s\n' %  (k, '\n'.join(tw8.wrap(v)))
            meta_index += 1
            keys_index += 1

        # Done.
        return answer
