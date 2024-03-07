import logging
import os

from src.file_handlers.exceptions import LineIndexOutOfRangeError
from src.file_handlers.manager import FileManager


class FileManagerWithPreProcessing(FileManager):
    def __init__(self, path: os.PathLike, logger: logging.Logger, bytes_before_line: list[int] | None = None) -> None:
        """
        :param path: Path to the file to serve, which must exist. Otherwise, HTTP 500 will be raised
        :param logger: Logger instance
        :param bytes_before_line: List representing the number of bytes in a file before the n-th line begins. From
            the moment this is populated, retrieving a line will not require the pre-processing step
        """
        super().__init__(path, logger)
        self.bytes_before_line = bytes_before_line

    def pre_process(self) -> list[int]:
        """
        Pre-process the served file by reading all of its contents, with only one line in memory at a time,
        and computing the number of bytes appearing before each line begins.
        This is an expensive operation as it requires reading the entire file; as such, it should occur only once
        :return: list representing the number of bytes in a file before the n-th line begins
        """
        with open(self.path, "r") as f:
            bytes_per_line = [len(line) for line in f]

        if bytes_per_line:  # if the file is not empty
            self.bytes_before_line = [0] + [sum(bytes_per_line[:i]) for i in range(1, len(bytes_per_line))]
        else:
            self.bytes_before_line = []
        return self.bytes_before_line

    async def get_line(self, line_index: int) -> str:
        """
        Retrieve the n-th line from the served file, with `n` starting at 0.
        If the served file has not been pre-processed yet, this step will occur at this time
        :param line_index: Index of the line to retrieve. Indices start at 0
        :raises LineIndexOutOfRangeError: if the n-th line doesn't exist in the file
        :return: line text
        """
        if self.bytes_before_line is None:
            self.pre_process()

        return await self._get_line_pre_processed(line_index)

    async def _get_line_pre_processed(self, line_index: int) -> str:
        """
        Internal method to retrieve the n-th line from the served file, with `n` starting at 0.
        This method assumes that the pre-processed step has occurred
        :param line_index: Index of the line to retrieve. Indices start at 0
        :raises LineIndexOutOfRangeError: if the n-th line doesn't exist in the file
        :return: line text
        """
        try:
            with open(self.path, "r") as f:
                f.seek(self.bytes_before_line[line_index])
                return f.readline()
        except IndexError:
            raise LineIndexOutOfRangeError()


