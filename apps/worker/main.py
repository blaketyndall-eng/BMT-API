import asyncio
import signal

from packages.core.config import get_settings

settings = get_settings()


class Worker:
    def __init__(self) -> None:
        self._shutdown = asyncio.Event()

    def request_shutdown(self) -> None:
        self._shutdown.set()

    async def run(self) -> None:
        print(f"worker starting in {settings.environment} mode")
        while not self._shutdown.is_set():
            await asyncio.sleep(5)


async def main() -> None:
    worker = Worker()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, worker.request_shutdown)

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
