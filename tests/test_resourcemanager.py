# SPDX-FileCopyrightText: 2024-present Hinrich Mahler <aiorem@mahlerhome.de>
#
# SPDX-License-Identifier: MIT
import pytest

from tests.conftest import (
    SimpleResourceManagerWithOnError,
)


class TestAbstractResourceManager:

    async def test_context_manager(self, resource_manager):
        async with resource_manager:
            assert resource_manager.resources_acquired
            assert not resource_manager.resources_released

        assert not resource_manager.resources_acquired
        assert resource_manager.resources_released

    async def test_decorator(self, resource_manager):
        @resource_manager
        async def some_function():
            assert resource_manager.resources_acquired
            assert not resource_manager.resources_released

        await some_function()
        assert not resource_manager.resources_acquired
        assert resource_manager.resources_released

    async def test_acquire_resources_error(
        self, resource_manager, resource_manager_with_on_error, monkeypatch
    ):
        for rm in [resource_manager, resource_manager_with_on_error]:

            async def acquire_resources_error():
                raise Exception("Test error")

            monkeypatch.setattr(rm, "acquire_resources", acquire_resources_error)

            with pytest.raises(Exception, match="Test error"):
                async with rm:
                    assert not rm.resources_acquired

            assert not rm.resources_acquired
            assert rm.resources_released
            if isinstance(rm, SimpleResourceManagerWithOnError):
                assert rm.release_resources_on_error_called

    async def test_context_manager_error_in_context_block(
        self, resource_manager, resource_manager_with_on_error
    ):
        for rm in [resource_manager, resource_manager_with_on_error]:

            with pytest.raises(RuntimeError, match="Test error"):
                async with rm:
                    raise RuntimeError("Test error")

            assert not rm.resources_acquired
            assert rm.resources_released
            if isinstance(rm, SimpleResourceManagerWithOnError):
                assert rm.release_resources_on_error_called
