import unittest
from pathlib import Path
from unittest.mock import MagicMock
from tempfile import NamedTemporaryFile, TemporaryDirectory

from src.file_handlers.exceptions import LineIndexOutOfRangeError
from src.file_handlers.manager import FileManager


class TestFileManager(unittest.IsolatedAsyncioTestCase):
    async def test_get_line_valid(self) -> None:
        content = ["I am line 0\n", "I am line 1\n", "I am line 2\n"]
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=False) as served_file:
                served_file.writelines(content)
            manager = FileManager(Path(served_file.name), MagicMock())

            result = await manager.get_line(1)

        self.assertEqual(result, content[1])

    async def test_get_line_empty_line(self) -> None:
        content = ["l0\n", "\n", "l2\n"]
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=False) as served_file:
                served_file.writelines(content)
            manager = FileManager(Path(served_file.name), MagicMock())

            result = await manager.get_line(1)

        self.assertEqual(result, "\n")

    async def test_get_line_out_of_range(self) -> None:
        content = ["a\n", "b\n", "c\n"]
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=False) as served_file:
                served_file.writelines(content)
            manager = FileManager(Path(served_file.name), MagicMock())

            with self.assertRaises(LineIndexOutOfRangeError):
                await manager.get_line(len(content))

    async def test_get_line_file_empty(self) -> None:
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=False) as served_file:
                pass
            manager = FileManager(Path(served_file.name), MagicMock())

            with self.assertRaises(LineIndexOutOfRangeError):
                await manager.get_line(0)

    async def test_get_line_file_not_found(self) -> None:
        with TemporaryDirectory() as tmpdir:
            with NamedTemporaryFile(dir=tmpdir, mode="w", delete=True) as served_file:
                pass
            manager = FileManager(Path(served_file.name), MagicMock())

            with self.assertRaises(FileNotFoundError):
                await manager.get_line(0)


if __name__ == '__main__':
    unittest.main()
