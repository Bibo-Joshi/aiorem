# SPDX-FileCopyrightText: 2024-present Hinrich Mahler <aiorem@mahlerhome.de>
#
# SPDX-License-Identifier: MIT
import abc
import asyncio
import contextlib
from collections.abc import Collection
from typing import Any, TypeGuard

from ._resourcemanager import AbstractResourceManager


def _exception_filter(obj: Any) -> TypeGuard[Exception]:
    return isinstance(obj, Exception)


class AbstractResourceManagerCollection(AbstractResourceManager, abc.ABC):
    """
    Abstract base class for collections of asynchronous resource managers.
    This is a simple implementation of :class:`AbstractResourceManager` that manages a collection
    of :class:`AbstractResourceManager` instances.
    """

    @property
    @abc.abstractmethod
    def _resource_managers(self) -> Collection[AbstractResourceManager]:
        """Return a collection of :class:`AbstractResourceManager` instances used by this
        resource manager collection. Must be implemented by a subclass.

        Returns:
            Collection[AbstractResourceManager]:
        """

    async def acquire_resources(self) -> None:
        """Calls :meth:`acquire_resources` on all resource managers in the
        :attr:`_resource_managers` in a concurrent fashion. If an exception occurs during the
        acquisition of resources, the already acquired resources are released.

        Returns:
            None

        Raises:
            ExceptionGroup: If an error occurs while acquiring resources, an :exc:`ExceptionGroup`
                is raised containing all exceptions that occurred.
        """
        async with contextlib.AsyncExitStack() as exit_stack:
            async with asyncio.TaskGroup() as task_group:
                for manager in self._resource_managers:
                    task_group.create_task(exit_stack.enter_async_context(manager))

            # If we reach this point, all resources have been acquired successfully
            # Hence, we want to keep the resources
            exit_stack.pop_all()

    async def release_resources(self) -> None:
        """Calls :meth:`release_resources` on all resource managers in the
        :attr:`_resource_managers` in a concurrent fashion. If an exception occurs during the
        release of resources, the remaining resources are still released.

        Returns:
            None

        Raises:
            ExceptionGroup: If an error occurs while releasing resources, an :exc:`ExceptionGroup`
                is raised containing all exceptions that occurred.
        """
        await self._release_resources(error=False)

    async def release_resources_on_error(self) -> None:
        """Like :meth:`release_resources`, but calls :meth:`release_resources_on_error` on all
        resource managers in the :attr:`_resource_managers`.

        Returns:
            None

        Raises:
            ExceptionGroup: If an error occurs while releasing resources, an :exc:`ExceptionGroup`
                is raised containing all exceptions that occurred.
        """
        await self._release_resources(error=True)

    async def _release_resources(self, error: bool) -> None:
        result = await asyncio.gather(
            *(
                manager.release_resources_on_error() if error else manager.release_resources()
                for manager in self._resource_managers
            ),
            return_exceptions=True,
        )
        exceptions = list(filter(_exception_filter, result))
        if exceptions:
            raise ExceptionGroup(
                f"Errors occurred while releasing resources. {len(exceptions)} resources where "
                f"not released.",
                exceptions,
            )
