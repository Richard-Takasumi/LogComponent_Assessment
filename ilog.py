from abc import ABC, abstractmethod

class ILog(ABC):
    @abstractmethod
    async def write(self, message: str):
        """
        Asynchronously writes a message to the log.
        :param message: String message to be written to the log.
        """
        pass
    
    @abstractmethod
    def stop(self, wait_for_completion: bool):
        """
        Stops the logging component.
        :param wait_for_completion: if True, the logger will finish writing all outstanding logs before stopping.
                                    if False, the logger will stop immediately without writing outstanding logs.
        """
        pass