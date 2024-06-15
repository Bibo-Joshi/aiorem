``aiorem``
==========

.. image:: https://img.shields.io/pypi/v/aiorem.svg
   :target: https://pypi.org/project/aiorem/
   :alt: PyPi Package Version

.. image:: https://img.shields.io/pypi/pyversions/aiorem.svg
   :target: https://pypi.org/project/aiorem/
   :alt: Supported Python versions

.. image:: https://readthedocs.org/projects/aiorem/badge/?version=latest
   :target: https://aiorem.readthedocs.io/latest/
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


For more information on how to use ``aiorem``, please refer to the `documentation <https://aiorem.readthedocs.io/en/stable/>`_.
