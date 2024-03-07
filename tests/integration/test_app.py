import json
import os
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient


class TestApp(unittest.TestCase):
    path = None
    client = None

    @classmethod
    def setUpClass(cls) -> None:
        content = ["I am line 0\n", "I am line 1\n", "I am line 2\n"]
        _, cls.path = tempfile.mkstemp(text=True)

        with open(cls.path, "w") as f:
            f.writelines(content)

        with patch.dict(os.environ, {"FILE_PATH_TO_SERVE": cls.path}):
            from src import main  # Import can only occur after we patch the desired env var
            cls.client = TestClient(main.app)

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.path)  # Remove temporary file after all tests run

    def test_get_line_valid(self) -> None:
        response = self.client.get("/lines/1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, json.dumps("I am line 1\n"))

    def test_get_line_out_of_range(self) -> None:
        response = self.client.get("/lines/3")

        self.assertEqual(response.status_code, 413)
