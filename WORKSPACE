workspace(name = "protoc_docs_plugin")

load(
    "//:repositories.bzl",
    "protoc_docs_plugin_repositories",
    "protoc_docs_plugin_register_toolchains",
)

protoc_docs_plugin_repositories()

protoc_docs_plugin_register_toolchains()

load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")

protobuf_deps()
