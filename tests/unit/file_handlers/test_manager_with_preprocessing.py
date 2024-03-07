import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
from tempfile import NamedTemporaryFile, TemporaryDirectory

from src.file_handlers.exceptions import LineIndexOutOfRangeError
from src.file_handlers.manager_with_preprocessing import FileManagerWithPreProcessing


class TestFileManagerWithPreProcessing(unittest.IsolatedAsyncioTestCase):
    async def test_pre_process_valid(self) -> None:
        content = ["I am line 0\n", "I am line 1\n", "I am line 2\n"]
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=False) as served_file:
                served_file.writelines(content)
            manager = FileManagerWithPreProcessing(Path(served_file.name), MagicMock())

            result = manager.pre_process()

        self.assertEqual(result, [0, len(content[0]), len(content[0])+len(content[1])])
        self.assertEqual(manager.bytes_before_line, result)  # assert that the instance attribute is populated

    async def test_pre_process_empty_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=False) as served_file:
                pass
            manager = FileManagerWithPreProcessing(Path(served_file.name), MagicMock())

            result = manager.pre_process()

        self.assertEqual(len(result), 0)

    async def test_get_line_not_pre_processed(self) -> None:
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=False) as served_file:
                pass
            manager = FileManagerWithPreProcessing(Path(served_file.name), MagicMock())

            with patch.object(manager, "pre_process") as mock_pre_process, \
                 patch.object(manager, "_get_line_pre_processed", AsyncMock()) as mock_internal_get_line:
                await manager.get_line(0)

                mock_pre_process.assert_called_once()
                mock_internal_get_line.assert_awaited_once_with(0)

    async def test_get_line_already_pre_processed(self) -> None:
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=False) as served_file:
                pass
            manager = FileManagerWithPreProcessing(Path(served_file.name), MagicMock())
            manager.bytes_before_line = [0, 1, 2, 3]  # pre-processing step occurred already

            with patch.object(manager, "pre_process") as mock_pre_process, \
                 patch.object(manager, "_get_line_pre_processed", AsyncMock()) as mock_internal_get_line:
                await manager.get_line(0)

                mock_pre_process.assert_not_called()
                mock_internal_get_line.assert_awaited_once_with(0)

    async def test_internal_get_line_valid(self) -> None:
        content = ["I am line 0\n", "I am line 1\n", "I am line 2\n"]
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=False) as served_file:
                served_file.writelines(content)
            manager = FileManagerWithPreProcessing(Path(served_file.name), MagicMock())
            manager.bytes_before_line = [0, len(content[0]), len(content[0])+len(content[1])]

            result = await manager._get_line_pre_processed(1)

        self.assertEqual(result, content[1])

    async def test_internal_get_line_empty_line(self) -> None:
        content = ["l0\n", "\n", "l2\n"]
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=False) as served_file:
                served_file.writelines(content)
            manager = FileManagerWithPreProcessing(Path(served_file.name), MagicMock())
            manager.bytes_before_line = [0, len(content[0]), len(content[0])+len(content[1])]

            result = await manager._get_line_pre_processed(1)

        self.assertEqual(result, "\n")

    async def test_internal_get_line_out_of_range(self) -> None:
        content = ["a\n", "b\n", "c\n"]
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=False) as served_file:
                served_file.writelines(content)
            manager = FileManagerWithPreProcessing(Path(served_file.name), MagicMock())
            manager.bytes_before_line = [0, len(content[0]), len(content[0])+len(content[1])]

            with self.assertRaises(LineIndexOutOfRangeError):
                await manager.get_line(len(content))

    async def test_get_line_file_empty(self) -> None:
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=False) as served_file:
                pass
            manager = FileManagerWithPreProcessing(Path(served_file.name), MagicMock())
            manager.bytes_before_line = []

            with self.assertRaises(LineIndexOutOfRangeError):
                await manager.get_line(0)

    async def test_get_line_file_not_found(self) -> None:
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=True) as served_file:
                pass
            manager = FileManagerWithPreProcessing(Path(served_file.name), MagicMock())

            with self.assertRaises(FileNotFoundError):
                await manager.get_line(0)


if __name__ == '__main__':
    unittest.main()
