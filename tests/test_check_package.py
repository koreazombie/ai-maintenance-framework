"""Verify real missing-file and broken-reference failures using isolated copies."""
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('checker', ROOT / 'scripts/check_package.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        shutil.copytree(ROOT, self.root,
                        ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))

    def test_complete_package_passes(self):
        errors, _ = checker.check(self.root)
        self.assertEqual(errors, [])

    def test_missing_rule_is_rejected(self):
        (self.root / 'framework/.ai/DATA_SAFETY.md').unlink()
        errors, _ = checker.check(self.root)
        self.assertTrue(any('Missing required file: framework/.ai/DATA_SAFETY.md' in e for e in errors))
        self.assertTrue(any('Broken entry reference' in e for e in errors))

    def test_broken_document_link_is_rejected(self):
        with (self.root / 'README.md').open('a') as f:
            f.write('\n[Missing](does-not-exist.md)\n')
        errors, _ = checker.check(self.root)
        self.assertTrue(any('Broken local link' in e and 'does-not-exist.md' in e for e in errors))

    def test_broken_claude_import_is_rejected(self):
        with (self.root / 'framework/CLAUDE.md').open('a') as f:
            f.write('\n@.ai/MISSING.md\n')
        errors, _ = checker.check(self.root)
        self.assertTrue(any('Broken import' in e and 'MISSING.md' in e for e in errors))

    def test_personal_path_is_rejected(self):
        with (self.root / 'README.md').open('a') as f:
            f.write('\n' + '/' + 'Users' + '/fixture/project/\n')
        errors, _ = checker.check(self.root)
        self.assertTrue(any('Personal filesystem path: README.md' in e for e in errors))

    def test_version_mismatch_is_rejected(self):
        (self.root / 'VERSION').write_text('9.9.9\n')
        errors, _ = checker.check(self.root)
        self.assertIn('Version differs from release.json', errors)


if __name__ == '__main__':
    unittest.main()
