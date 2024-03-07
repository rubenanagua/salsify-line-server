import os
from pathlib import Path


FILENAME = os.getenv("FILENAME", ".base.txt")
FILE_PATH_TO_SERVE = Path(os.getenv("FILE_PATH_TO_SERVE", Path(__file__).parent.parent.joinpath(FILENAME))).resolve()
