# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import sys

import pypandoc

from google.protobuf import descriptor_pb2 as desc


class CommentsConverter(object):
    """Comments converter which converts comments in a batch by calling
    convert_text only once for the whole batch. The ``pypandoc.convert_text``
    call spawns a child ``pandoc`` subprocess, so it is an expensive operation
    and we want to minimize the number of such calls.

    Batching is performed by concatenating comments with special characters in
    them (and skipping the others) using the unique batch token. After that
    ``pandoc`` is called for the batch only once and then the result is split by
    same batch token back into individual comments.
    """

    _PROTO_LINK_RE = re.compile(
        r'(\[(?P<text>[^\]]+)\]\[(?P<uri>[A-Za-z_][A-Za-z_.0-9]*)?\])')
    _RELATIVE_LINK_RE = re.compile(
        r'(\[(?P<text>[^\]]+)\]\((?P<uri>/[^\)]+)\))')
    _NEW_LINES = re.compile(r'(?P<newlines>(\r?\n)+)(?P<followup>[^\r\n])')

    _BATCH_TOKEN = "$#!"

    def __init__(self):
        self.raw_comments = {}
        self.converted_comments = {}
        self._index = 0

    def put_comment(self, comment):
        """Put a comment in a batch for future processing by ``pypandoc``.

        This method must be called one or more times prior calling
        ``convert()``, if this method is called after ``convert()`` its behavior
        is undefined.

        Args:
            comment (str): The comment to convert.
        """

        comment = self._replace_proto_link(comment)
        comment = self._replace_relative_link(comment)

        token = comment

        # Try to avoid conversion for comments without special characters in the
        # markdown
        if any([i in token for i in '`[]*_']):
            if self.converted_comments:
                token = "\n%s%s" % (self._BATCH_TOKEN, token)
            self.converted_comments[self._index] = token
        else:
            self.raw_comments[self._index] = token

        self._index += 1

    def convert(self):
        """Converts the comments by calling `pypandoc` for a batch of comments and
        then splitting them back into individual comments.

        This method must be called only once after a last call to
        ``put_comment()`` and before a first call to ``get_next_comment()``.
        """

        converted_doc = pypandoc.convert_text(
            "".join(self.converted_comments.values()),
            'rst',
            format='commonmark'
        )
        converted = converted_doc.split(self._BATCH_TOKEN)

        c_index = 0
        index = 0
        while c_index < len(converted):
            while index in self.raw_comments:
                index += 1
            self.converted_comments[index] = self._insert_spaces(
                converted[c_index])
            index += 1
            c_index += 1

        self._index = 0

    def get_next_comment(self):
        """Iterates over individual comments after conversion has been done.
        This method returns converted comments in same order as they where
        initially put into this converter.

        This method may be called one or more times after calling ``convert()``,
        if this method is called before ``convert()`` its behavior is undefined.

        Returns:
            str: A converted comment
        """

        if self._index in self.raw_comments:
            comment = self.raw_comments[self._index]
        else:
            comment = self.converted_comments[self._index]
        self._index += 1
        return comment

    def _replace_proto_link(self, comment):
        def _format(m):
            return "`{}`".format(m.group('text'))

        return self._replace(comment, CommentsConverter._PROTO_LINK_RE, _format)

    def _replace_relative_link(self, comment):
        def _format(m):
            return "[{}](https://cloud.google.com{})".format(m.group('text'),
                                                             m.group('uri'))

        return self._replace(comment, CommentsConverter._RELATIVE_LINK_RE,
                             _format)

    def _insert_spaces(self, comment):
        # Comment is now a valid restructuredtext, but there is a problem. It
        # is being inserted back into a descriptor set, and there is an
        # expectation that each line of a comment will begin with a space, to
        # separate it from the '//' that begins the comment. You would think
        # that we could ignore this detail, but it will cause formatting
        # problems down the line in gapic-generator because parsing code will
        # try to remove the leading space, affecting the indentation of lines
        # that actually do begin with a space, so we insert the additional
        # space now.
        def _format(m):
            return "{} {}".format(m.group('newlines'), m.group('followup'))

        # After replacement, add a leading space
        return " " + self._replace(comment, CommentsConverter._NEW_LINES, _format)

    def _replace(self, comment, pattern, repl_fn):
        index = 0
        strs = []
        for m in pattern.finditer(comment):
            strs.append(comment[index:m.start()])
            strs.append(repl_fn(m))
            index = m.end()
        strs.append(comment[index:])
        return ''.join(strs)


def convert_desc(source_desc, dest_desc):
    """Converts proto comments to restructuredtext format.

    Proto comments are expected to be in markdown format, and to possibly
    contain links to other protobuf types and relative URLs that will not
    resolve to correct documentation using standard tools.

    This task performs the following transformations on the documentation
    in the descriptor set:
    - Replace proto links with literals (e.g. [Foo][bar.baz.Foo] -> `Foo`)
    - Resolve relative URLs to https://cloud.google.com
    - Run pandoc to convert from markdown to restructuredtext"""

    desc_set = desc.FileDescriptorSet()
    with open(source_desc, 'rb') as f:
        desc_set.ParseFromString(f.read())

    cb = CommentsConverter()

    for file_descriptor_proto in desc_set.file:
        sc_info = file_descriptor_proto.source_code_info
        locations = sc_info.location if sc_info else []
        for location in locations:
            cb.put_comment(location.leading_comments)
            cb.put_comment(location.trailing_comments)
            for c in location.leading_detached_comments:
                cb.put_comment(c)

    cb.convert()

    for file_descriptor_proto in desc_set.file:
        sc_info = file_descriptor_proto.source_code_info
        locations = sc_info.location if sc_info else []
        for location in locations:
            location.leading_comments = cb.get_next_comment()
            location.trailing_comments = cb.get_next_comment()
            detached = []
            for _ in location.leading_detached_comments:
                detached.append(cb.get_next_comment())
            del location.leading_detached_comments[:]
            location.leading_detached_comments.extend(detached)

    with open(dest_desc, mode='wb') as f:
        f.write(desc_set.SerializeToString())


if __name__ == '__main__':
    convert_desc(sys.argv[1], sys.argv[2])
