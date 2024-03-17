import asyncio
import os
import unittest
from unittest.mock import patch
from datetime import datetime
from log_component import LogComponent

class TestLogComponent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.test_directory = 'test_logs'
        self.logger = LogComponent(self.test_directory)

    async def asyncTearDown(self):
        self.logger.stop(wait_for_completion=True)
        await asyncio.sleep(0.1)  # Give some time for logs to be written before cleaning up
        for file in os.listdir(self.test_directory):
            os.remove(os.path.join(self.test_directory, file))
        os.rmdir(self.test_directory)

    async def test_write_log(self):
        log_message = "Test log entry"
        await self.logger.write(log_message)
        self.logger.stop(wait_for_completion=True)
        await asyncio.sleep(0.1)  # Give some time for logs to be written

        log_files = os.listdir(self.test_directory)
        self.assertEqual(len(log_files), 1, "Expected one log file to be created")

        with open(os.path.join(self.test_directory, log_files[0]), 'r') as log_file:
            content = log_file.read()
            self.assertIn(log_message, content, "Expected the log message to be written to the file")


    @patch('log_component.datetime')
    async def test_new_file_created_at_midnight(self, mock_datetime):
        # Set up the mock to return a time just before midnight
        mock_datetime.now.return_value = datetime(2023, 3, 17, 23, 59, 59)
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        # Create a log entry - should use the initial file name
        await self.logger.write("Log entry before midnight")
        await asyncio.sleep(0.1)  # Allow time for the log entry to be processed

        # Change the mock to return a time just after midnight
        mock_datetime.now.return_value = datetime(2023, 3, 18, 0, 0, 1)

        # Create another log entry - should trigger a new file to be created
        await self.logger.write("Log entry after midnight")
        self.logger.stop(wait_for_completion=True)
        await asyncio.sleep(0.1)  # Allow time for all log entries to be processed

        # Check that two files have been created
        log_files = os.listdir(self.test_directory)
        self.assertEqual(len(log_files), 2, "Expected two log files to be created due to crossing midnight")

        # Sort the files by name to ensure the correct order for assertions
        log_files.sort()

        # Check the contents of the first file
        with open(os.path.join(self.test_directory, log_files[0]), 'r') as log_file:
            content = log_file.read()
            self.assertIn("Log entry before midnight", content, "Expected the log message before midnight to be in the first file")

        # Check the contents of the second file
        with open(os.path.join(self.test_directory, log_files[1]), 'r') as log_file:
            content = log_file.read()
            self.assertIn("Log entry after midnight", content, "Expected the log message after midnight to be in the second file")

    async def test_stop_immediate(self):
        await self.logger.write("Log entry 1")
        await self.logger.write("Log entry 2")

        self.logger.stop(wait_for_completion=False)
        await asyncio.sleep(0.1)  # Give some time for the logger to stop

        log_files = os.listdir(self.test_directory)
        self.assertLessEqual(len(log_files), 1, "Expected at most one log file to be created")

        if log_files:
            with open(os.path.join(self.test_directory, log_files[0]), 'r') as log_file:
                content = log_file.read()
                self.assertNotIn("Log entry 2", content, "Expected 'Log entry 2' to not be written to the file")

    async def test_stop_wait_for_completion(self):
        await self.logger.write("Log entry 1")
        await self.logger.write("Log entry 2")

        self.logger.stop(wait_for_completion=True)
        await asyncio.sleep(0.1)  # Give some time for the logger to stop

        log_files = os.listdir(self.test_directory)
        self.assertEqual(len(log_files), 1, "Expected one log file to be created")

        with open(os.path.join(self.test_directory, log_files[0]), 'r') as log_file:
            content = log_file.read()
            self.assertIn("Log entry 1", content, "Expected 'Log entry 1' to be written to the file")
            self.assertIn("Log entry 2", content, "Expected 'Log entry 2' to be written to the file")
    

if __name__ == "__main__":
    unittest.main()

