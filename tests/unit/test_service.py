import unittest
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException

from src.file_handlers.exceptions import LineIndexOutOfRangeError
from src.service import LineService


class TestLineService(unittest.IsolatedAsyncioTestCase):
    def test_pre_process(self) -> None:
        service = LineService()
        service.manager.pre_process = MagicMock()

        service.pre_process()

        service.manager.pre_process.assert_called_once()

    async def test_get_line_valid(self) -> None:
        content = "hi! I am a line\n"
        line_index = 1234567
        service = LineService()
        service.manager.get_line = AsyncMock(return_value=content)

        await service.get_line(line_index)

        service.manager.get_line.assert_awaited_once_with(line_index)

    async def test_get_line_valid_with_bytes_before_line(self) -> None:
        content = "hi! I am a line\n"
        line_index = 1234567
        bytes_before_line = [0, 1, 2, 3]
        service = LineService()
        service.manager.get_line = AsyncMock(return_value=content)

        await service.get_line(line_index, bytes_before_line)

        service.manager.get_line.assert_awaited_once_with(line_index)
        self.assertEqual(service.manager.bytes_before_line, bytes_before_line)

    async def test_get_line_file_not_found(self) -> None:
        service = LineService()
        service.manager.get_line = AsyncMock(side_effect=FileNotFoundError)

        with self.assertRaises(HTTPException) as e_context:
            await service.get_line(1234567)

        self.assertEqual(500, e_context.exception.status_code)

    async def test_get_line_out_of_range(self) -> None:
        service = LineService()
        service.manager.get_line = AsyncMock(side_effect=LineIndexOutOfRangeError)

        with self.assertRaises(HTTPException) as e_context:
            await service.get_line(1234567)

        self.assertEqual(413, e_context.exception.status_code)


if __name__ == '__main__':
    unittest.main()
