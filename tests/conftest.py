# SPDX-FileCopyrightText: 2024-present Hinrich Mahler <aiorem@mahlerhome.de>
#
# SPDX-License-Identifier: MIT
from collections.abc import Collection

import pytest

from aiorem import AbstractResourceManager, AbstractResourceManagerCollection


class SimpleResourceManager(AbstractResourceManager):
    def __init__(self):
        self.resources_acquired = False
        self.resources_released = False

    async def acquire_resources(self):
        self.resources_acquired = True

    async def release_resources(self):
        self.resources_released = True
        self.resources_acquired = False


class SimpleResourceManagerWithOnError(SimpleResourceManager):

    def __init__(self):
        super().__init__()
        self.release_resources_on_error_called = False

    async def release_resources_on_error(self):
        await super().release_resources()
        self.release_resources_on_error_called = True


class SimpleResourceManagerCollection(AbstractResourceManagerCollection):
    def __init__(self, resources: Collection[SimpleResourceManager]):
        self.resources = resources

    @property
    def _resource_managers(self):
        return self.resources


@pytest.fixture()
def resource_manager():
    return SimpleResourceManager()


@pytest.fixture()
def resource_manager_with_on_error():
    return SimpleResourceManagerWithOnError()


@pytest.fixture()
def resource_manager_collection():
    return SimpleResourceManagerCollection([SimpleResourceManagerWithOnError() for _ in range(3)])
