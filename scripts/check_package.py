"""Offline structural checks; does not validate product behavior or live AI loading."""
from pathlib import Path
import json
import importlib.util
import re
import sys
from urllib.parse import unquote

RULES = ('CORE', 'ARCHITECTURE', 'MODULE_BOUNDARY', 'CONTRACT_FIRST',
         'DATA_SAFETY', 'VERIFICATION', 'REGENERATION', 'WORKFLOW')
REQUIRED = ('README.md', 'INSTALL.md', 'LICENSE', 'NOTICE.md', 'VERSION',
            'AGENTS.md', 'CLAUDE.md', 'release.json', 'CONTRIBUTING.md',
            'framework/AGENTS.md', 'framework/CLAUDE.md',
            'framework/.ai/verification/CHECKLIST.md', 'framework/.ai/verification/GATES.md',
            'framework/.ai/templates/PROJECT.md', 'framework/.ai/templates/CONTRACT.md',
            'framework/.ai/PROJECT.md', 'framework/.ai/PRIVACY.md',
            'framework/.ai/FRAMEWORK.md', 'framework/.ai/LICENSE',
            'framework/.ai/docs/README.md', 'docs/MIGRATING-0.2.md',
            'profiles.json', 'release-catalog.json', 'scripts/validate_installation.py',
            'scripts/record_installation.py', 'scripts/generate_catalog.py',
            'docs/MIGRATING-0.3.md', 'examples/single-script/README.md')


def check(root):
    root = Path(root).resolve()
    errors = []
    for name in (*REQUIRED, *(f'framework/.ai/rules/{rule}.md' for rule in RULES)):
        if not (root / name).is_file():
            errors.append(f'Missing required file: {name}')
    payload = root / 'framework'
    if payload.is_dir():
        extra = {p.name for p in payload.iterdir()} - {'AGENTS.md', 'CLAUDE.md', '.ai'}
        if extra:
            errors.append('Scattered payload files: ' + ', '.join(sorted(extra)))
    if (payload / '.ai/LICENSE').is_file() and (root / 'LICENSE').is_file():
        if (payload / '.ai/LICENSE').read_bytes() != (root / 'LICENSE').read_bytes():
            errors.append('Payload license differs from root LICENSE')
    files = [p for p in root.rglob('*') if p.is_file()
             and not any(part in {'.git', '__pycache__', '.venv'}
                         for part in p.relative_to(root).parts)]
    links = imports = 0
    for p in sorted(files):
        rel = p.relative_to(root)
        if p.suffix in {'.pyc', '.zip'}:
            continue
        try:
            body = p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            errors.append(f'Not UTF-8 text: {rel}')
            continue
        if not body.strip():
            errors.append(f'Empty file: {rel}')
        if '\ufffd' in body:
            errors.append(f'Replacement character: {rel}')
        if re.search(r'/(?:Users|home)/[A-Za-z0-9_.-]+/', body):
            errors.append(f'Personal filesystem path: {rel}')
        if re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}', body):
            errors.append(f'Possible GitHub token: {rel}')
        if p.suffix != '.md':
            continue
        if sum(line.startswith('```') for line in body.splitlines()) % 2:
            errors.append(f'Unclosed code fence: {rel}')
        prose = re.sub(r'```[^\n]*\n.*?```', '', body, flags=re.S)
        for target in re.findall(r'\]\(([^)]+)\)', prose):
            target = target.strip().strip('<>')
            if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                continue
            links += 1
            candidate = (p.parent / unquote(target.split('#')[0])).resolve()
            if not candidate.is_relative_to(root) or not candidate.exists():
                errors.append(f'Broken local link: {rel} -> {target}')
        for target in re.findall(r'^@([^\s]+)$', prose, re.M):
            imports += 1
            if not (p.parent / target).is_file():
                errors.append(f'Broken import: {rel} -> {target}')
        if rel.as_posix() in {'framework/AGENTS.md', 'framework/CLAUDE.md'}:
            for target in re.findall(r'`((?:\.ai|verification)/[^`]+\.md)`', body):
                if not (p.parent / target).is_file():
                    errors.append(f'Broken entry reference: {rel} -> {target}')
    try:
        metadata = json.loads((root / 'release.json').read_text())
        version = (root / 'VERSION').read_text().strip()
        if metadata['version'] != version:
            errors.append('Version differs from release.json')
        if metadata['license'] != 'MIT' or 'MIT License' not in (root / 'LICENSE').read_text():
            errors.append('License metadata differs from LICENSE')
    except (OSError, ValueError, KeyError) as exc:
        errors.append(f'Invalid release metadata: {exc}')
    try:
        spec = importlib.util.spec_from_file_location('release_catalog_checker', root / 'scripts/generate_catalog.py')
        catalog_checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(catalog_checker)
        if (root / 'release-catalog.json').read_text() != catalog_checker.serialized(root):
            errors.append('Release profile catalog differs from actual source files')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Invalid profile catalog: {exc}')
    return errors, {'files': len(files), 'local_links': links, 'imports': imports}


if __name__ == '__main__':
    failures, counts = check(Path(__file__).resolve().parents[1])
    for failure in failures:
        print(f'ERROR: {failure}')
    if failures:
        sys.exit(1)
    print('PASS: ' + ', '.join(f'{key}={value}' for key, value in counts.items()))
    print('Scope: package structure only; product tests and live AI loading excluded.')
