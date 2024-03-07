from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic.types import NonNegativeInt

from src.service import LineService


router = APIRouter()  # router to append to the main app
bytes_before_line = LineService().pre_process()  # pre-processing step made here to ensure it only runs once per app


@router.get("/{line_index}", responses={413: {"description": "Line index out of range"}})
async def get_line(service: Annotated[LineService, Depends()], line_index: NonNegativeInt) -> str:
    """
    Retrieve content of the line of the provided index, starting with index 0.
    If the provided index is beyond the end of the file, HTTP 413 is returned.\f
    :param service: `LineService` instance responsible for handling the business logic of retrieving a line
    :param line_index: Line index, as a non-negative integer. The first line of a file is index 0
    :return: desired line of the served file
    """
    return await service.get_line(line_index, bytes_before_line)
