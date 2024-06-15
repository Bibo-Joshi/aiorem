# SPDX-FileCopyrightText: 2024-present Hinrich Mahler <aiorem@mahlerhome.de>
#
# SPDX-License-Identifier: MIT
import abc
import contextlib
from types import TracebackType
from typing import Self


class AbstractResourceManager(
    contextlib.AbstractAsyncContextManager["AbstractResourceManager"],
    contextlib.AsyncContextDecorator,
    abc.ABC,
):
    """
    Abstract base class for asynchronous resource managers.
    Instances of this class can be used as asynchronous context managers while at the same time
    providing explicit methods to acquire and release resources.

    The context manager usage

    .. code:: python

        async with resource_manager as rm:
            # code

    is roughly equivalent to

    .. code:: python

        try:
            await rm.acquire_resources()
            # code
            await rm.release_resources()
        except Exception as exc:
            await rm.release_resources_on_error()
            raise exc

    .. seealso:: :meth:`__aenter__` and :meth:`__aexit__`.

    Instances of this class can also be used as decorators for asynchronous functions.

    Example:

        .. code:: python

            @resource_manager
            async def some_function():
                # code

    """

    @abc.abstractmethod
    async def acquire_resources(self) -> None:
        """Acquire resources used by this class. Must be implemented by a subclass.

        Returns:
            None
        """

    @abc.abstractmethod
    async def release_resources(self) -> None:
        """Release resources used by this class. Must be implemented by a subclass.

        Returns:
            None
        """

    async def release_resources_on_error(self) -> None:
        """Release resources used by this class in case of an error either in
        :meth:`acquire_resources` or in the context block of the context manager.
        Defaults to calling :meth:`release_resources`.
        """
        await self.release_resources()

    async def __aenter__(self) -> Self:
        """Entry point for the asynchronous context manager.

        Returns:
            The initialized instance.

        Raises:
            :exc:`Exception`: If an exception is raised during acquiring resources,
                :meth:`release_resources_on_error` is called.
        """
        try:
            await self.acquire_resources()
            return self
        except Exception as exc:
            await self.release_resources_on_error()
            raise exc

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit point for the asynchronous context manager. Calls either :meth:`release_resources`
        or :meth:`release_resources_on_error` depending on whether an exception occurred in
        the context block.

        Returns:
            None
        """
        if exc_type is not None:
            await self.release_resources_on_error()
        else:
            await self.release_resources()
