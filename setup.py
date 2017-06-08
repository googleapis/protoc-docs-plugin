#!/usr/bin/env python

# Copyright 2016 Google Inc. All Rights Reserved.
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


"""Setup tool for protoc_docs_plugin."""

import io
import os
import setuptools


setuptools.setup(
    name='protoc-docs-plugin',
    version='0.1.0',
    description='Plugin for reading and writing documentation from '
                'protobuf files into existing generated protoc output.',
    author='Luke Sneeringer',
    author_email='lukesneeringer@google.com',
    url='https://github.com/googleapis/protoc-docs-plugin',
    license='Apache-2.0',
    install_requires=(
        'protobuf >= 3.3.0',
        'pypandoc >= 1.4',
    ),
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'protoc-gen-pydocstring = protoc_docs.bin.py_docstring:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)
