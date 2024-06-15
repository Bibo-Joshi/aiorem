``aiorem``
==========

.. image:: https://img.shields.io/pypi/v/aiorem.svg
   :target: https://pypi.org/project/aiorem/
   :alt: PyPi Package Version

.. image:: https://img.shields.io/pypi/pyversions/aiorem.svg
   :target: https://pypi.org/project/aiorem/
   :alt: Supported Python versions

.. image:: https://readthedocs.org/projects/aiorem/badge/?version=stable
   :target: https://aiorem.readthedocs.io/
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/l/aiorem.svg
   :target: https://mit-license.org/
   :alt: MIT License

.. image:: https://github.com/Bibo-Joshi/aiorem/actions/workflows/unit_tests.yml/badge.svg?branch=main
   :target: https://github.com/Bibo-Joshi/aiorem/
   :alt: Github Actions workflow

.. image:: https://codecov.io/gh/Bibo-Joshi/aiorem/graph/badge.svg?token=H1HUA2FDR3
 :target: https://codecov.io/gh/Bibo-Joshi/aiorem
   :alt: Code coverage

.. image:: https://results.pre-commit.ci/badge/github/Bibo-Joshi/aiorem/main.svg
   :target: https://results.pre-commit.ci/latest/github/Bibo-Joshi/aiorem/main
   :alt: pre-commit.ci status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code Style: Black

A simple asyncio context manager with explicit interface.

Introduction
------------

This library provides a simple context manager for managing resources in an asyncio environment.
It's designed to have an explicit interface, which makes it easy to use both as context manager and as a regular object for custom use cases.

Installing
----------

You can install or upgrade ``aiorem`` via

.. code:: shell

    $ pip install aiorem --upgrade

Motivation
----------

When working with ``asyncio`` Python libraries, async context managers are a common pattern for managing resources and snippets like

.. code:: python

    async with some_lib.Client() as client:
        ...

are often seen in the quickstart.
However, there are two use cases, where this pattern is hard to use and an explicit interface for acquiring and releasing resources is desirable.

1. Nested context managers: When writing a class that manages several resources, acquiring and releasing these resources should each usually be bundled in a single method.
2. Low level event loop usage: In some advanced cases, it can be desirable to use things like ``loop.run_until_complete`` than ``await``-ing a coroutine.

For both cases, one can then either explicitly call ``Client.__aenter__`` and ``Client.__aexit__`` or duplicate whatever logic is used within these methods.
Unfortunately, the behavior of ``Client.__aenter__`` and ``Client.__aexit__`` is not always well documented.
Moreover, using magic/dunder might be viewed as bad practice, as they are mostly intended to be used by the Python interpreter.

This shortcoming is what ``aiorem`` aims to improve.
As the Quick Start below shows, subclasses of ``aiorem.AbstractResourceManager`` can be used in different ways according to the needs of the use case while the behavior is well documented and explicit.
For the case of nested context managers, ``aiorem`` provides the `AbstractResourceManagerCollection <https://aiorem.readthedocs.io/stable/aiorem.html#aiorem.AbstractResourceManagerCollection>`_ class as a natural extension of `AbstractResourceManager <https://aiorem.readthedocs.io/stable/aiorem.html#aiorem.AbstractResourceManager>`_.

Quick Start
-----------

Here is a simple example of how to use ``aiorem``:

.. code:: python

    import asyncio
    from aiorem import AbstractResourceManager


    class ResourceManager(AbstractResourceManager):
        async def acquire_resources(self):
            print("Resource acquired")

        async def release_resources(self):
            print("Resource released")


    async def context_manager():
        async with ResourceManager():
            print("Context manager block")


    @ResourceManager()
    async def decorator():
        print("Decorator block")


    async def explicit_interface():
        rm = ResourceManager()
        await rm.acquire_resources()
        print("Explicit interface block")
        await rm.release_resources()


    async def main():
        await context_manager()
        await decorator()
        await explicit_interface()


    if __name__ == "__main__":
        asyncio.run(main())


For more information on how to use ``aiorem``, please refer to the `documentation <https://aiorem.readthedocs.io/>`_.