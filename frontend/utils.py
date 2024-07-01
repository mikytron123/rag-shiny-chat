import asyncio
import inspect
from typing import TypeVar, Generic, Callable, Any, Coroutine

from shiny import reactive

T = TypeVar("T")


class StreamResult(Generic[T]):
    _read: Callable[[], tuple[T, ...]]
    _cancel: Callable[[], bool]

    def __init__(self, read: Callable[[], tuple[T, ...]], cancel: Callable[[], bool]):
        self._read = read
        self._cancel = cancel

    def __call__(self) -> tuple[T, ...]:
        """
        Perform a reactive read of the stream. You'll get the latest value, and you will
        receive an invalidation if a new value becomes available.
        """
        return self._read()

    def cancel(self) -> bool:
        """
        Stop the underlying stream from being consumed. Returns False if the task is
        already done or cancelled.
        """
        return self._cancel()


running_tasks: set[asyncio.Task[Any]] = set()


def safe_create_task(task: Coroutine[Any, Any, T]) -> asyncio.Task[T]:
    t = asyncio.create_task(task)
    running_tasks.add(t)
    t.add_done_callback(running_tasks.remove)
    return t


def stream_to_reactive(
    func
) -> StreamResult[T]:
    val: reactive.Value[tuple[T, ...]] = reactive.Value(tuple())

    async def task_main():
        nonlocal func
        if inspect.isawaitable(func):
            func = await func  # type: ignore
        # func = cast(AsyncGenerator[T, None], func)

        message_batch: list[T] = []

        # for message in func(chunk_size=1024):
        async for message in func.aiter_bytes():
            # This print will display every message coming from the server.
            message_batch.append(message)

            async with reactive.lock():
                val.set(tuple(message_batch))
                await reactive.flush()

            # last_message_time = time.time()
            message_batch = []

        # # Once the stream has ended, flush the remaining messages.
        if len(message_batch) > 0:
            async with reactive.lock():
                val.set(tuple(message_batch))
                await reactive.flush()
        await func.aclose()

    task = safe_create_task(task_main())

    return StreamResult(val.get, lambda: task.cancel())
