import asyncio
import signal
import uuid

from packages.core.config import get_settings
from packages.workers.browser_fetch_jobs import process_one_browser_fetch_job

settings = get_settings()


class Worker:
    def __init__(self) -> None:
        self._shutdown = asyncio.Event()
        self.worker_id = f"browser-fetch-worker-{uuid.uuid4()}"

    def request_shutdown(self) -> None:
        self._shutdown.set()

    async def run(self) -> None:
        print(f"worker starting in {settings.environment} mode as {self.worker_id}")
        while not self._shutdown.is_set():
            processed = await process_one_browser_fetch_job(worker_id=self.worker_id)
            await asyncio.sleep(1 if processed else 5)


async def main() -> None:
    worker = Worker()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, worker.request_shutdown)

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
