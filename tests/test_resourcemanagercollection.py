# SPDX-FileCopyrightText: 2024-present Hinrich Mahler <aiorem@mahlerhome.de>
#
# SPDX-License-Identifier: MIT
import asyncio
from typing import Literal

import pytest

from tests.conftest import (
    SimpleResourceManager,
    SimpleResourceManagerCollection,
    SimpleResourceManagerWithOnError,
)


class SleepResourceManager(SimpleResourceManager):

    def __init__(self, delay: float = 1):
        self.delay = delay
        super().__init__()

    async def acquire_resources(self):
        await asyncio.sleep(self.delay)
        await super().acquire_resources()

    async def release_resources(self):
        await asyncio.sleep(self.delay)
        await super().release_resources()


class EventResourceManager(SimpleResourceManagerWithOnError):
    def __init__(
        self,
        id: int,
        *,
        acquire_error: Literal[False] | str = False,
    ):
        super().__init__()
        self.id = id
        self.event = asyncio.Event()
        self.acquire_error = acquire_error

    async def acquire_resources(self):
        await self.event.wait()
        if self.acquire_error:
            raise Exception(self.acquire_error)
        await super().acquire_resources()

    async def release_resources(self):
        self.event.clear()
        await super().release_resources()


class TestAbstractResourceManagerCollection:

    async def test_context_manager(self, resource_manager_collection):
        async with resource_manager_collection:
            for rm in resource_manager_collection.resources:
                assert rm.resources_acquired
                assert not rm.resources_released

        for rm in resource_manager_collection.resources:
            assert not rm.resources_acquired
            assert rm.resources_released

    async def test_decorator(self, resource_manager_collection):
        @resource_manager_collection
        async def some_function():
            for resource_manager in resource_manager_collection.resources:
                assert resource_manager.resources_acquired
                assert not resource_manager.resources_released

        await some_function()
        for rm in resource_manager_collection.resources:
            assert not rm.resources_acquired
            assert rm.resources_released

    async def test_acquire_resources_concurrency(
        self,
    ):
        delay = 0.5
        rms = [SleepResourceManager(delay) for _ in range(10)]
        resource_manager_collection = SimpleResourceManagerCollection(rms)

        # ensure that acquiring resources takes less time
        # than the sum of the individual acquire times
        start = asyncio.get_event_loop().time()
        await resource_manager_collection.acquire_resources()
        end = asyncio.get_event_loop().time()
        assert end - start == pytest.approx(delay, 0.1)

    async def test_release_resources_concurrency(
        self,
    ):
        delay = 0.5
        rms = [SleepResourceManager(delay) for _ in range(10)]
        resource_manager_collection = SimpleResourceManagerCollection(rms)

        # ensure that acquiring resources takes less time
        # than the sum of the individual release times
        start = asyncio.get_event_loop().time()
        await resource_manager_collection.release_resources()
        end = asyncio.get_event_loop().time()
        assert end - start == pytest.approx(delay, 0.1)

    async def test_context_manager_error_in_context_block(self, resource_manager_collection):
        with pytest.raises(Exception, match="Test error"):
            async with resource_manager_collection:
                raise Exception("Test error")

        for i, rm in enumerate(resource_manager_collection.resources):
            assert not rm.resources_acquired
            assert rm.resources_released
            assert rm.release_resources_on_error_called, f"RM {i} not called"

    async def test_acquire_resources_error_simple(
        self, resource_manager_with_on_error, monkeypatch
    ):
        rm = resource_manager_with_on_error
        rm_collection = SimpleResourceManagerCollection([rm])

        async def acquire_resources_error():
            raise Exception("Test error")

        monkeypatch.setattr(rm, "acquire_resources", acquire_resources_error)

        with pytest.raises(ExceptionGroup) as exec_info:
            async with rm_collection:
                pass

        assert len(exec_info.value.exceptions) == 1
        assert exec_info.group_contains(Exception, match="Test error")

        assert not rm.resources_acquired
        assert rm.resources_released

    async def test_acquire_resources_error_multiple(self):
        rms = [
            EventResourceManager(0),
            EventResourceManager(1, acquire_error="Test Error"),
            EventResourceManager(2),
        ]
        rm_collection = SimpleResourceManagerCollection(rms)

        async def make_assertion():
            async with rm_collection:
                pass

        task = asyncio.create_task(make_assertion())

        assert not task.done()
        rms[0].event.set()
        await asyncio.sleep(0.1)

        assert rms[0].resources_acquired
        assert not rms[0].resources_released
        assert not rms[1].resources_acquired
        assert not rms[1].resources_released
        assert not rms[2].resources_acquired
        assert not rms[2].resources_released

        assert not task.done()
        rms[1].event.set()

        with pytest.raises(ExceptionGroup) as exec_info:
            await task

        assert len(exec_info.value.exceptions) == 1
        assert exec_info.group_contains(Exception, match="Test Error")

        for rm in rms:
            assert not rm.resources_acquired
            assert rm.resources_released
            assert rm.release_resources_on_error_called

    async def test_release_resources_error_simple(
        self, resource_manager_with_on_error, monkeypatch
    ):
        rm = resource_manager_with_on_error
        rm_collection = SimpleResourceManagerCollection([rm])

        async def acquire_resources_error():
            raise Exception("Test error")

        monkeypatch.setattr(rm, "acquire_resources", acquire_resources_error)

        with pytest.raises(ExceptionGroup) as exec_info:
            async with rm_collection:
                pass

        assert len(exec_info.value.exceptions) == 1
        assert exec_info.group_contains(Exception, match="Test error")

        assert not rm.resources_acquired
        assert rm.resources_released

    @pytest.mark.parametrize("on_error", [False, True])
    async def test_release_resources_error_multiple(self, on_error, monkeypatch):
        rms = [SimpleResourceManagerWithOnError() for _ in range(3)]
        rm_collection = SimpleResourceManagerCollection(rms)

        async def release_error():
            raise Exception("Release Error")

        suffix = "_on_error" if on_error else ""
        monkeypatch.setattr(rms[1], f"release_resources{suffix}", release_error)

        async def make_assertion():
            async with rm_collection:
                if on_error:
                    raise Exception("Context Error")

        task = asyncio.create_task(make_assertion())

        with pytest.raises(ExceptionGroup, match="1 resources where not released") as exec_info:
            await task

        assert len(exec_info.value.exceptions) == 1
        assert exec_info.group_contains(Exception, match="Release Error")

        for i, rm in enumerate(rms):
            assert rm.resources_acquired == (i == 1)
            assert rm.resources_released == (i != 1)
            assert rm.release_resources_on_error_called == (on_error and (i != 1))
