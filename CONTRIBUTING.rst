############
Contributing
############

#. **Please sign one of the contributor license agreements below.**
#. Fork the repo, develop and test your code changes, add docs.
#. Make sure that your commit messages clearly describe the changes.
#. Send a pull request. (Please Read: `Faster Pull Request Reviews`_)

.. _Faster Pull Request Reviews: https://github.com/kubernetes/community/blob/master/contributors/devel/faster_reviews.md

.. contents:: Here are some guidelines for hacking on ``protoc-docs-plugin``.

***************
Adding Features
***************

In order to add a feature to ``protoc-docs-plugin``:

- The feature must be documented in both the API and narrative
  documentation (in ``docs/``).

- The feature must work fully on the following CPython versions:  2.7,
  3.4, and 3.5 on both UNIX and Windows.

- The feature must not add unnecessary dependencies (where
  "unnecessary" is of course subjective, but new dependencies should
  be discussed).

****************************
Using a Development Checkout
****************************

You'll have to create a development environment to hack on
``protoc-docs-plugin``, using a Git checkout:

- While logged into your GitHub account, navigate to the
  ``protoc-docs-plugin`` `repo`_ on GitHub.

- Fork and clone the ``protoc-docs-plugin`` repository to your GitHub account by
  clicking the "Fork" button.

- Clone your fork of ``protoc-docs-plugin`` from your GitHub account to your local
  computer, substituting your account username and specifying the destination
  as ``hack-on-protoc-docs-plugin``.  E.g.::

   $ cd ${HOME}
   $ git clone git@github.com:USERNAME/protoc-docs-plugin.git hack-on-protoc-docs-plugin
   $ cd hack-on-protoc-docs-plugin
   # Configure remotes such that you can pull changes from the protoc-docs-plugin
   # repository into your local repository.
   $ git remote add upstream git@github.com:GoogleCloudPlatform/protoc-docs-plugin.git
   # fetch and merge changes from upstream into master
   $ git fetch upstream
   $ git merge upstream/master

Now your local repo is set up such that you will push changes to your GitHub
repo, from which you can submit a pull request.

To work on the codebase and run the tests, we recommend using ``tox``,
but you can also use a ``virtualenv`` of your own creation.

.. _repo: https://github.com/GoogleCloudPlatform/protoc-docs-plugin

Using a custom ``virtualenv``
=============================

- To create a virtualenv in which to install ``protoc-docs-plugin``::

    $ cd ${HOME}/hack-on-protoc-docs-plugin
    $ virtualenv --python python2.7 ${ENV_NAME}

  You can choose which Python version you want to use by passing a ``--python``
  flag to ``virtualenv``.  For example, ``virtualenv --python python2.7``
  chooses the Python 2.7 interpreter to be installed.

- From here on in within these instructions, the
  ``${HOME}/hack-on-protoc-docs-plugin/${ENV_NAME}`` virtual environment you
  created above will be referred to as ``${VENV}``. To use the instructions
  in the steps that follow literally, use::

    $ export VENV=${HOME}/hack-on-protoc-docs-plugin/${ENV_NAME}

- To install ``protoc-docs-plugin`` from your source checkout into
  ``${VENV}``, run::

    $ # Make sure you are in the same directory as setup.py
    $ cd ${HOME}/hack-on-protoc-docs-plugin
    $ ${VENV}/bin/python setup.py install

  Unfortunately using ``setup.py develop`` is not possible with this
  project, because it uses `namespace packages`_.

*************
Running Tests
*************

- To run all tests for ``protoc-docs-plugin`` on a single Python version, run
  ``py.test`` from your development virtualenv (See
  `Using a Development Checkout`_ above).

.. _Using a Development Checkout: #using-a-development-checkout

- To run the full set of ``protoc-docs-plugin`` tests on all platforms, install
  ``nox`` (``pip install nox-automation``) into system Python.  The
  ``nox`` console script will be installed into the scripts location for that
  Python.

  While ``cd``'-ed to the ``protoc-docs-plugin`` checkout root
  directory (it contains ``nox.py``), invoke the ``nox`` console script.
  This will read the ``nox.py`` file and execute the tests on multiple
  Python versions and platforms; while it runs, it creates a ``virtualenv`` for
  each version/platform combination.  For example::

.. _Using a Development Checkout: #using-a-development-checkout

**********
Versioning
**********

This library follows `Semantic Versioning`_.

.. _Semantic Versioning: http://semver.org/

It is currently in major version zero (``0.y.z``), which means that anything
may change at any time and the public API should not be considered
stable.

******************************
Contributor License Agreements
******************************

Before we can accept your pull requests you'll need to sign a Contributor License Agreement (CLA):

- **If you are an individual writing original source code** and **you own the intellectual property**, then you'll need to sign an `individual CLA <https://developers.google.com/open-source/cla/individual>`__.
- **If you work for a company that wants to allow you to contribute your work**, then you'll need to sign a `corporate CLA <https://developers.google.com/open-source/cla/corporate>`__.

You can sign these electronically (just scroll to the bottom). After that, we'll be able to accept your pull requests.
