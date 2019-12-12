import os

from protoc_docs.bin import py_docstring

if __name__ == '__main__':
    os.environ['PYPANDOC_PANDOC'] = os.path.join(
        os.path.abspath(__file__).rsplit("protoc_docs", 1)[0], "pandoc")
    py_docstring.main()
