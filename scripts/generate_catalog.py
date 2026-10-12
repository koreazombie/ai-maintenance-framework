"""Create or verify the release profile hash catalog without third-party dependencies."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def build_catalog(root=ROOT):
    registry = json.loads((root / 'profiles.json').read_text(encoding='utf-8'))
    version = (root / 'VERSION').read_text(encoding='utf-8').strip()
    if registry['version'] != version:
        raise ValueError('profiles.json version differs from VERSION')
    common = [
        {'source':'framework/AGENTS.md', 'target':'AGENTS.md', 'mutable':True},
        {'source':'framework/CLAUDE.md', 'target':'CLAUDE.md', 'mutable':True},
        {'source':'LICENSE', 'target':'.ai/LICENSE', 'mutable':False},
        {'source':'scripts/validate_installation.py', 'target':'.ai/tools/validate_installation.py', 'mutable':False},
    ]
    result = {'schema_version':1, 'version':version, 'profiles':{}}
    for name, profile in registry['profiles'].items():
        records = []
        seen = set()
        for item in profile['files'] + common:
            if item['target'] in seen:
                raise ValueError(f'Duplicate target: {item["target"]}')
            seen.add(item['target'])
            source = root / item['source']
            if not source.resolve().is_relative_to(root.resolve()):
                raise ValueError('Source outside repository')
            records.append({**item, 'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
        result['profiles'][name] = {'label':profile['label'], 'files':records}
    return result


def serialized(root=ROOT):
    return json.dumps(build_catalog(root), ensure_ascii=False, indent=2) + '\n'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    content = serialized()
    target = ROOT / 'release-catalog.json'
    if args.check:
        if not target.is_file() or target.read_text(encoding='utf-8') != content:
            print('ERROR: release-catalog.json is stale; regenerate after reviewed source changes')
            sys.exit(1)
        print('PASS: release profile catalog matches actual released source files')
    else:
        target.write_text(content, encoding='utf-8')
        print('Generated release-catalog.json')
