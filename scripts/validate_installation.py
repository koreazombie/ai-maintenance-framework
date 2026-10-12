"""Offline installation consistency checks, not proof of product behavior or truthfulness."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

VERSION = '0.3.0'
PRIVACY = {'shared', 'local-guidance', 'private-sync', 'local-all'}
PLACEHOLDER = re.compile(r'<[^>\n]+>|미설정|미선택|\b(?:TODO|TBD|PLACEHOLDER)\b', re.I)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_path(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute() or '..' in Path(name).parts:
        raise ValueError(f'Unsafe managed path: {name!r}')
    result = (root / name).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError(f'Path leaves project: {name}')
    return result


def read_json(path):
    result = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(result, dict):
        raise ValueError(f'Expected object: {path.name}')
    return result


def project_fields(text):
    return dict(re.findall(r'^- ([^:\n]+):\s*(.*?)\s*$', text, re.M))


def validate(project, check_git=True):
    root = Path(project).resolve()
    errors, warnings = [], []
    try:
        manifest = read_json(root / '.ai/installation.json')
        catalog = read_json(root / '.ai/release-catalog.json')
        if manifest.get('schema_version') != 1 or catalog.get('schema_version') != 1:
            raise ValueError('Unsupported metadata schema')
        if manifest.get('version') != VERSION or catalog.get('version') != VERSION:
            raise ValueError('Installation/catalog version differs from validator version')
        profile = manifest.get('profile')
        if profile not in {'solo', 'modular'}:
            raise ValueError('Unknown installation profile')
        privacy = manifest.get('privacy')
        if privacy not in PRIVACY:
            raise ValueError('Unknown privacy choice')
        spec = catalog['profiles'][profile]['files']
        if not isinstance(spec, list) or not spec:
            raise ValueError('Empty profile')
        expected = {item['target']: item for item in spec}
        if len(expected) != len(spec):
            raise ValueError('Duplicate profile target')
        managed = manifest['files']
        if not isinstance(managed, dict) or set(managed) != set(expected):
            raise ValueError('Recorded files differ from selected profile file list')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [str(exc)], warnings
    for name, item in expected.items():
        try:
            path = safe_path(root, name)
            if not path.is_file():
                errors.append(f'Missing installed file: {name}')
                continue
            actual = sha256(path)
            snapshot = managed[name]
            if not isinstance(snapshot, str) or not re.fullmatch(r'[0-9a-f]{64}', snapshot):
                errors.append(f'Invalid recorded hash: {name}')
            elif actual != snapshot:
                errors.append(f'Installed file changed since recorded baseline: {name}')
            if not item['mutable'] and actual != item['sha256']:
                errors.append(f'Installed file differs from released profile: {name}')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f'{name}: {exc}')
    def document_text(path):
        try:
            return path.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as exc:
            errors.append(f'Cannot read {path.name}: {exc}')
            return ''
    project_doc = root / '.ai/PROJECT.md'
    if project_doc.is_file():
        text = document_text(project_doc)
        for number, line in enumerate(text.splitlines(), 1):
            if PLACEHOLDER.search(line):
                errors.append(f'PROJECT.md placeholder at line {number}')
        fields = project_fields(text)
        if fields.get('프레임워크 버전') != VERSION:
            errors.append('PROJECT.md version differs from installed version')
        if fields.get('프로파일') != profile:
            errors.append('PROJECT.md profile differs from installation.json')
        if fields.get('지침 관리 방식') != privacy:
            errors.append('PROJECT.md privacy differs from installation.json')
        required_fields = ['목적', '언어·런타임', '실행 명령', '검증 명령']
        if profile == 'solo':
            required_fields += ['진입 파일', '보존할 동작']
        for field in required_fields:
            if not fields.get(field):
                errors.append(f'PROJECT.md missing required field: {field}')
        if '미확인' in text:
            warnings.append('PROJECT.md has explicitly unconfirmed facts; this check does not confirm them')
    if profile == 'modular':
        path = root / '.ai/FRAMEWORK.md'
        if path.is_file():
            fields = project_fields(document_text(path))
            if fields.get('배포 버전') != VERSION:
                errors.append('FRAMEWORK.md version differs from installed version')
            if fields.get('프로파일') != profile:
                errors.append('FRAMEWORK.md profile differs from installed profile')
            if fields.get('지침 관리 방식') != privacy:
                errors.append('FRAMEWORK.md privacy differs from installed choice')
        path = root / '.ai/PRIVACY.md'
        if path.is_file():
            text = document_text(path)
            choice = re.search(r'^선택 상태:\s*(\S+)', text, re.M)
            if not choice or choice.group(1) != privacy:
                errors.append('PRIVACY.md selected choice differs from installation.json')
    if profile == 'solo':
        for name in ('modules', 'templates', 'verification', 'changes', 'docs', 'examples', 'profile-templates'):
            if (root / '.ai' / name).exists():
                errors.append(f'Unexpected guidance for solo profile: .ai/{name}')
        for name in ('ARCHITECTURE', 'MODULE_BOUNDARY', 'CONTRACT_FIRST', 'DATA_SAFETY', 'VERIFICATION', 'REGENERATION'):
            if (root / f'.ai/rules/{name}.md').exists():
                errors.append(f'Unselected modular rule present in solo profile: {name}')
        for name in ('FRAMEWORK.md', 'PRIVACY.md'):
            if (root / '.ai' / name).exists():
                errors.append(f'Unselected modular document present in solo profile: {name}')
    for name in ('AGENTS.md', 'CLAUDE.md'):
        path = root / name
        if not path.is_file():
            continue
        text = document_text(path)
        for target in re.findall(r'^@([^\s]+)$', text, re.M):
            try:
                if not safe_path(root, target).is_file():
                    errors.append(f'Broken entry import: {name} -> {target}')
            except ValueError as exc:
                errors.append(str(exc))
    if check_git:
        try:
            probe = subprocess.run(['git', '-C', str(root), 'rev-parse', '--show-toplevel'],
                                   capture_output=True, text=True)
            if probe.returncode != 0:
                warnings.append('No Git repository: tracking/ignore checks not performed')
            elif Path(probe.stdout.strip()).resolve() != root:
                errors.append('Project is not Git root; resolve monorepo exclusion scope before validation')
            else:
                hidden = ['.ai'] if privacy in {'local-guidance', 'private-sync', 'local-all'} else []
                if privacy == 'local-all':
                    hidden += ['AGENTS.md', 'CLAUDE.md']
                if hidden:
                    tracked = subprocess.run(['git', '-C', str(root), 'ls-files', '-z', '--', *hidden],
                                             capture_output=True)
                    if tracked.returncode != 0:
                        errors.append('Cannot inspect Git tracked files')
                    elif tracked.stdout:
                        errors.append('Private paths remain tracked/staged: ' + ', '.join(
                            p.decode('utf-8', errors='replace') for p in tracked.stdout.split(b'\0') if p))
                    for target in ['.ai/PROJECT.md'] + (['AGENTS.md', 'CLAUDE.md'] if privacy == 'local-all' else []):
                        ignored = subprocess.run(['git', '-C', str(root), 'check-ignore', '--no-index', '--quiet', '--', target],
                                                 capture_output=True)
                        if ignored.returncode != 0:
                            errors.append(f'Private path is not effectively ignored: {target}')
                else:
                    for target in expected:
                        ignored = subprocess.run(['git', '-C', str(root), 'check-ignore', '--no-index', '--quiet', '--', target],
                                                 capture_output=True)
                        if ignored.returncode == 0:
                            errors.append(f'Shared managed file is ignored: {target}')
                        elif ignored.returncode != 1:
                            errors.append(f'Cannot inspect ignore status: {target}')
        except OSError as exc:
            warnings.append(f'Git inspection unavailable: {exc}')
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    errors, warnings = validate(args.project)
    for message in errors:
        print('ERROR: ' + message)
    for message in warnings:
        print('WARN: ' + message)
    if errors:
        return 1
    print('PASS: installation metadata, file hashes and project settings are consistent')
    print('Scope excludes truth of prose, product behavior, live AI loading and past public Git history')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
