import logging

from fastapi import HTTPException

from src import constants
from src.file_handlers.exceptions import LineIndexOutOfRangeError
from src.file_handlers.manager_with_preprocessing import FileManagerWithPreProcessing


class LineService:
    """Service responsible for bridging between the app and the business logic of serving lines from a file"""
    def __init__(self) -> None:
        self.logger = logging.getLogger("uvicorn")
        self.manager = FileManagerWithPreProcessing(constants.FILE_PATH_TO_SERVE, logger=self.logger)

    async def get_line(self, line_index: int, bytes_before_line: list[int] | None = None) -> str:
        """
        Retrieve the n-th line of the served file
        :param line_index: Index of the line to retrieve. Indices start at 0
        :param bytes_before_line: Optional list representing the number of bytes to skip before the n-th line starts.
            If this is provided, or if this method is not being called for the first time, the pre-processing step,
            which reads the entire file once, is not executed
        :raises HTTPException: with HTTP 500 status, if the file is not found or an unhandled error occurs, or
            with HTTP 413 status if the line index is higher than the number of lines existing in the file
        :return: line text
        """
        self.logger.info("Retrieving line from served file", extra={"line_index": line_index})
        if bytes_before_line:
            self.manager.bytes_before_line = bytes_before_line

        try:
            return await self.manager.get_line(line_index)
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="File not found")
        except LineIndexOutOfRangeError:
            raise HTTPException(status_code=413, detail="Line index is out of range")

    def pre_process(self) -> list[int]:
        """
        :return: list with the number of bytes written in the file before the line of a given index starts
        """
        self.logger.info("Pre-processing file to speed up future requests")
        from time import time
        start = time()
        result = self.manager.pre_process()
        end = time()
        self.logger.info(f"Pre-processed file in {end - start} seconds")
        return result
