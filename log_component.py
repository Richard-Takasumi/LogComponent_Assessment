# log_component.py
import asyncio
import aiofiles
import os
from datetime import datetime
from ilog import ILog

class LogComponent(ILog):
    def __init__(self, storage_directory: str):
        self.log_queue = asyncio.Queue()
        self.stop_event = asyncio.Event()
        self._task = asyncio.create_task(self._write_logs())

        self.log_directory = storage_directory  # Directory where log files will be stored
        os.makedirs(self.log_directory, exist_ok=True)  # Create the directory if it doesn't exist
        self.file_name = os.path.join(self.log_directory, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
       
       
    async def _write_logs(self):
        while not self.stop_event.is_set() or not self.log_queue.empty():
            message = await self.log_queue.get()
            try:
                # Rotate log file if crossing midnight
                current_date = datetime.now().strftime('%Y%m%d')
                file_date = os.path.basename(self.file_name)[:8] # Extracts the date from filename, e.g 20240317

                if current_date != file_date:
                    self.file_name = os.path.join(self.log_directory, f"{current_date}_{datetime.now().strftime('%H%M%S')}.txt")
                # Write message to file
                async with aiofiles.open(self.file_name, mode='a') as log_file:
                    await log_file.write(message + "\n")
            except Exception as e:
                # Log the error if needed, but do not raise to avoid affecting the calling application
                print(f"Error writing to log file: {e}")
            finally:
                self.log_queue.task_done()

    async def write(self, message: str):
        # Non-blocking write operation
        await self.log_queue.put(message)

    def stop(self, wait_for_completion: bool):
        self.stop_event.set()  # Set the stop event to signal the background task to stop
        if wait_for_completion:
            # Wait for all tasks to be completed
            asyncio.create_task(self._stop_when_done())
        else:
            # Stop immediately and cancel the background writing task
            self._task.cancel()

    async def _stop_when_done(self):
        await self.log_queue.join()  # Wait until all items in the queue are processed
        self.stop_event.set()
        self._task.cancel()  # Cancel the background writing task

# Example usage
if __name__ == "__main__":
    async def main():
        logger = LogComponent('logs')
        await logger.write("Log entry 1")
        await logger.write("Log entry 2")

        # Stop the logger and wait for all logs to be written
        logger.stop(wait_for_completion=True)
        await asyncio.sleep(1)  # Give some time for logs to be written before the script ends

    asyncio.run(main())