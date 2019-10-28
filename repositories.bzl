load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

_DEFAULT_PY_BUILD_FILE = """
py_library(
    name = "lib",
    srcs = glob(["**/*.py"]),
    visibility = ["//visibility:public"],
)
"""

_PANDOC_BUILD_FILE = """
filegroup(
    name = "pandoc",
    srcs = ["bin/pandoc"],
    visibility = ["//visibility:public"],
)"""

def protoc_docs_plugin_repositories():
    _maybe(
        http_archive,
        name = "com_google_protobuf",
        strip_prefix = "protobuf-c60aaf79e63b911b2c04c04e1eacb4f3c36ef790",  # this is 3.9.1 with fixes
        urls = ["https://github.com/protocolbuffers/protobuf/archive/c60aaf79e63b911b2c04c04e1eacb4f3c36ef790.zip"],
    )

    _maybe(
        http_archive,
        name = "pypi_pypandoc",
        url = "https://files.pythonhosted.org/packages/71/81/00184643e5a10a456b4118fc12c96780823adb8ed974eb2289f29703b29b/pypandoc-1.4.tar.gz",
        strip_prefix = "pypandoc-1.4",
        build_file_content = _DEFAULT_PY_BUILD_FILE,
    )

    _maybe(
        http_archive,
        name = "pandoc_linux",
        build_file_content = _PANDOC_BUILD_FILE,
        strip_prefix = "pandoc-2.2.1",
        url = "https://github.com/jgm/pandoc/releases/download/2.2.1/pandoc-2.2.1-linux.tar.gz",
    )

    _maybe(
        http_archive,
        name = "pandoc_macOS",
        build_file_content = _PANDOC_BUILD_FILE,
        strip_prefix = "pandoc-2.2.1",
        url = "https://github.com/jgm/pandoc/releases/download/2.2.1/pandoc-2.2.1-macOS.zip",
    )

def protoc_docs_plugin_register_toolchains():
    native.register_toolchains(
        "@protoc_docs_plugin//:pandoc_toolchain_linux",
        "@protoc_docs_plugin//:pandoc_toolchain_macOS",
    )

def _maybe(repo_rule, name, strip_repo_prefix = "", **kwargs):
    if not name.startswith(strip_repo_prefix):
        return
    repo_name = name[len(strip_repo_prefix):]
    if repo_name in native.existing_rules():
        return
    repo_rule(name = repo_name, **kwargs)