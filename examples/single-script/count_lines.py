"""Count nonblank lines in a UTF-8 text file without modifying it."""
from pathlib import Path
import argparse


def count_nonblank(path):
    with Path(path).open(encoding='utf-8') as stream:
        return sum(bool(line.strip()) for line in stream)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path)
    args = parser.parse_args()
    print(count_nonblank(args.file))
