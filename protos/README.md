## Reference Protos

The following `.proto` files represent the data model used by the
`protoc` plugin API. They are provided here for reference and are not
actually used by this plugin at runtime.

  * `plugin.proto` is copied from the [protobuf plugin API reference][1].
  * `descriptor.proto` is copied from [google/protobuf][2] on GitHub.

  [1]: https://developers.google.com/protocol-buffers/docs/reference/cpp/google.protobuf.compiler.plugin.pb#
  [2]: https://github.com/google/protobuf/blob/master/src/google/protobuf/descriptor.proto

One edit has been made to `plugin.proto`: on line 54, the `google/protobuf/`
path prefix on the import was removed.

Note that these files are covered by their original license (BSD 3-clause)
and not the license of this plugin (Apache).
