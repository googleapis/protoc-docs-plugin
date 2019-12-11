import os
import sys

from protoc_docs.bin import py_desc_converter

if __name__ == '__main__':
    os.environ['PYPANDOC_PANDOC'] = os.path.join(
        os.path.abspath(__file__).rsplit("protoc_docs", 1)[0], "pandoc")
    py_desc_converter.convert_desc(sys.argv[1], sys.argv[2])
