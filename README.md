## protoc-docs-plugin

This is a `protoc` plugin intended to augment protoc's default Python
output with docstrings. It has been loosely designed to be able to support
docstrings for other langauges also, but this is contingent upon the
availability of appropriate insertion points in those languages.

### Installation & Dependencies

This package depends on the current version of `protobuf` and `pypandoc`
from PyPI.

```bash
$ pip install protoc-docs-plugin
```

Additionally, this package also depends on the `pandoc` OS package, which
you will need to install from your OS package manager.

While it will run standalone as well, it only ever actually makes sense
to invoke it from `protoc`.

### Usage

Add `--pydocstring_out` _to the same command_ to protoc that has a previous
`--python_out` directive.

Example:

```bash
$ protoc foo.proto --python_out=. --pydocstring_out=.
```

Order does matter here; `protoc` must write the plain Python output first
before it can augment it with the output from this plugin.

### More Information

  * [protoc plugins][1]

  [1]: https://developers.google.com/protocol-buffers/docs/reference/other
