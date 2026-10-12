"""Exercise real profile records, deliberate drift and Git privacy behavior in temp projects."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from record_installation import record
from validate_installation import validate, safe_path


class InstallationChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project'
        self.root.mkdir()
        self.catalog = json.loads((ROOT / 'release-catalog.json').read_text())

    def install(self, profile='solo', privacy='local-all', git=False):
        for item in self.catalog['profiles'][profile]['files']:
            target = self.root / item['target']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / item['source'], target)
        text = (ROOT / 'examples/single-script/PROJECT.example.md').read_text()
        text = text.replace('- 프로파일: solo', f'- 프로파일: {profile}').replace('local-all', privacy)
        (self.root / '.ai/PROJECT.md').write_text(text)
        if profile == 'modular':
            (self.root / '.ai/FRAMEWORK.md').write_text(
                f'- 배포 버전: 0.3.0\n- 프로파일: modular\n- 지침 관리 방식: {privacy}\n')
            path = self.root / '.ai/PRIVACY.md'
            path.write_text(path.read_text().replace('선택 상태: 미선택', f'선택 상태: {privacy}'))
        if git:
            self.git('init', '-q')
            patterns = '' if privacy == 'shared' else '/.ai/\n'
            if privacy == 'local-all': patterns += '/AGENTS.md\n/CLAUDE.md\n'
            (self.root / '.gitignore').write_text(patterns or '# no excluded guidance\n')
        errors, _ = record(self.root, ROOT, profile, privacy)
        self.assertEqual(errors, [])

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)

    def snapshot(self, name):
        path = self.root / '.ai/installation.json'
        data = json.loads(path.read_text())
        data['files'][name] = hashlib.sha256((self.root / name).read_bytes()).hexdigest()
        path.write_text(json.dumps(data))

    def test_solo_installs_exactly_three_guidance_documents(self):
        self.install()
        self.assertEqual({p.relative_to(self.root / '.ai').as_posix() for p in (self.root / '.ai').rglob('*.md')},
                         {'PROJECT.md','rules/CORE.md','rules/WORKFLOW.md'})
        self.assertEqual(validate(self.root, check_git=False)[0], [])

    def test_modular_installation_passes(self):
        self.install('modular', 'shared')
        self.assertEqual(validate(self.root, check_git=False)[0], [])

    def test_placeholder_is_rejected_even_with_current_snapshot(self):
        self.install()
        p = self.root / '.ai/PROJECT.md'
        p.write_text(p.read_text() + '\n- 목적 추가: <내용>\n')
        self.snapshot('.ai/PROJECT.md')
        self.assertTrue(any('placeholder' in x for x in validate(self.root, False)[0]))

    def test_mutable_drift_requires_reviewed_refresh(self):
        self.install()
        p = self.root / '.ai/PROJECT.md'
        p.write_text(p.read_text() + '\n추가 결정: 입력은 읽기 전용.\n')
        self.assertTrue(any('changed since recorded' in x for x in validate(self.root, False)[0]))
        self.assertEqual(record(self.root, ROOT, 'solo', 'local-all', refresh=True)[0], [])

    def test_rule_drift_cannot_be_hidden_by_snapshot(self):
        self.install()
        p = self.root / '.ai/rules/CORE.md'
        p.write_text(p.read_text() + '\nDifferent rule.\n')
        self.snapshot('.ai/rules/CORE.md')
        self.assertTrue(any('differs from released' in x for x in validate(self.root, False)[0]))
        with self.assertRaises(ValueError): record(self.root, ROOT, 'solo', 'local-all', refresh=True)

    def test_wrong_version_is_rejected(self):
        self.install()
        p = self.root / '.ai/installation.json'
        data = json.loads(p.read_text()); data['version'] = '0.2.0'; p.write_text(json.dumps(data))
        self.assertTrue(any('version differs' in x for x in validate(self.root, False)[0]))

    def test_framework_version_mismatch_is_rejected(self):
        self.install('modular', 'shared')
        p = self.root / '.ai/FRAMEWORK.md';p.write_text(p.read_text().replace('0.3.0','0.2.0'))
        self.snapshot('.ai/FRAMEWORK.md')
        self.assertTrue(any('FRAMEWORK.md version differs' in x for x in validate(self.root, False)[0]))

    def test_missing_file_is_rejected(self):
        self.install()
        (self.root / '.ai/rules/WORKFLOW.md').unlink()
        self.assertTrue(any('Missing installed file' in x for x in validate(self.root, False)[0]))

    def test_extra_modular_documents_are_rejected_for_solo(self):
        self.install()
        (self.root / '.ai/modules').mkdir()
        self.assertTrue(any('Unexpected guidance for solo' in x for x in validate(self.root, False)[0]))

    def test_local_all_checks_real_git_exclusion(self):
        self.install(privacy='local-all', git=True)
        self.assertEqual(validate(self.root)[0], [])
        self.git('add', '.')
        self.assertNotIn(b'AGENTS.md', self.git('ls-files').stdout)
        self.assertNotIn(b'.ai/', self.git('ls-files').stdout)

    def test_private_tracked_entrypoint_is_rejected(self):
        self.install(privacy='local-all', git=True)
        self.git('add', '-f', 'AGENTS.md')
        self.assertTrue(any('remain tracked/staged' in x for x in validate(self.root)[0]))

    def test_missing_private_entrypoint_ignore_is_rejected(self):
        self.install(privacy='local-all', git=True)
        (self.root / '.gitignore').write_text('/.ai/\n')
        errors, _ = validate(self.root)
        self.assertTrue(any('not effectively ignored: AGENTS.md' in x for x in errors))

    def test_shared_files_cannot_be_ignored_silently(self):
        self.install(privacy='shared', git=True)
        (self.root / '.gitignore').write_text('/.ai/\n')
        self.assertTrue(any('Shared managed file is ignored' in x for x in validate(self.root)[0]))

    def test_failed_refresh_does_not_replace_baseline(self):
        self.install()
        path = self.root / '.ai/installation.json'; original = path.read_bytes()
        p = self.root / '.ai/PROJECT.md';p.write_text(p.read_text()+'\nTODO\n')
        with self.assertRaises(ValueError): record(self.root, ROOT, 'solo', 'local-all', refresh=True)
        self.assertEqual(path.read_bytes(), original)

    def test_invalid_project_encoding_is_reported(self):
        self.install()
        (self.root / '.ai/PROJECT.md').write_bytes(b'\xff\xfe')
        self.assertTrue(any('Cannot read PROJECT.md' in x for x in validate(self.root, False)[0]))

    def test_malformed_metadata_is_reported(self):
        self.install()
        (self.root / '.ai/installation.json').write_text('[]')
        self.assertTrue(any('Expected object' in x for x in validate(self.root, False)[0]))

    def test_installed_cli_uses_its_own_project_root(self):
        self.install(privacy='local-all', git=True)
        result = subprocess.run([sys.executable, str(self.root / '.ai/tools/validate_installation.py')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS:', result.stdout)

    def test_installed_cli_returns_failure_for_missing_file(self):
        self.install()
        (self.root / '.ai/rules/WORKFLOW.md').unlink()
        result = subprocess.run([sys.executable, str(self.root / '.ai/tools/validate_installation.py')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Missing installed file', result.stdout)

    def test_paths_cannot_escape_the_project(self):
        with self.assertRaises(ValueError): safe_path(self.root, '../outside')


if __name__ == '__main__': unittest.main()
