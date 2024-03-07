import argparse
import os
import random
import string
from pathlib import Path


def generate_file(path: os.PathLike, n_lines: int, max_characters_per_line: int,
                  character_pool: str) -> None:
    """
    Create or overwrite a file on the provided path, and populate it with the provided number of lines, with a
    random number of characters (up to a given limit per line), selected randomly from a predefined pool, per line.
    It is assumed that the directory already exists.
    :param path: path to the file to generate
    :param n_lines: number of lines to generate as the file contents
    :param max_characters_per_line: maximum number of characters to write per line
    :param character_pool: pool of characters to select randomly from
    """
    with open(Path(path).resolve(), "w") as f:
        for _ in range(n_lines):
            line = generate_line(max_characters_per_line, character_pool)
            f.write(line)


def generate_line(max_chars: int, char_pool: str) -> str:
    """
    Generate a line by selecting a character from a predefined string, and repeating this process up to the
    provided maximum number of characters. It is possible that a line is empty if the randomly selected
    number of characters is 0
    :param max_chars: maximum number of characters to write per line
    :param char_pool: pool of characters to select randomly from
    :return: generated line, including the newline character
    """
    n_chars = random.randint(0, max_chars)
    return "".join(random.choices(char_pool, k=n_chars)) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="File generator",
        description="Creates a file at the provided path, with the provided number of lines, and a random number of "
                    "characters per line until the provided limit"
    )
    parser.add_argument("path", type=str, help="Path to the file to create")
    parser.add_argument("-l", "--lines", type=int, default=1000, help="Number of lines to create")
    parser.add_argument("-c", "--max-chars-per-line", type=int, default=1000,
                        help="Maximum number of characters to create per line")
    args = parser.parse_args()

    pool = string.ascii_letters + string.digits + string.punctuation + " \t"
    generate_file(args.path, args.lines, args.max_chars_per_line, pool)
