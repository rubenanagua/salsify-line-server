import itertools
import logging
import os
from pathlib import Path

from src.file_handlers.exceptions import LineIndexOutOfRangeError


class FileManager:
    """Class responsible for handling the file to serve"""
    def __init__(self, path: os.PathLike, logger: logging.Logger) -> None:
        """
        :param path: Path to the file to serve, which must exist. Otherwise, HTTP 500 will be raised
        :param logger: Logger instance
        """
        self.path = Path(path).resolve()
        self.logger = logger

    async def get_line(self, line_index: int) -> str:
        """
        Retrieve the n-th line of the served file
        :param line_index: Index of the line to retrieve. Indices start at 0
        :raises LineIndexOutOfRangeError: if the n-th line doesn't exist in the file
        :return: line text
        """
        try:
            with open(self.path, "r") as f:
                return next(itertools.islice(f, line_index, line_index+1))
        except StopIteration:
            raise LineIndexOutOfRangeError
