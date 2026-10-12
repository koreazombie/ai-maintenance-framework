from pathlib import Path
import tempfile
import unittest
from count_lines import count_nonblank


class CountLines(unittest.TestCase):
    def test_counts_nonblank_lines_and_preserves_input(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'input.txt'
            text = 'first\n\n   \nsecond\n'
            path.write_text(text)
            self.assertEqual(count_nonblank(path), 2)
            self.assertEqual(path.read_text(), text)

    def test_empty_input_is_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'empty.txt'
            path.write_text('')
            self.assertEqual(count_nonblank(path), 0)


if __name__ == '__main__':
    unittest.main()
