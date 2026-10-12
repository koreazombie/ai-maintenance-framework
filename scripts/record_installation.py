"""Record already-installed, reviewed files; never installs, overwrites or stages guidance."""
from pathlib import Path
import argparse
import datetime
import json
import tempfile
import shutil
from validate_installation import VERSION, PRIVACY, safe_path, sha256, validate, read_json


def record(root, source, profile, privacy, refresh=False):
    root, source = Path(root).resolve(), Path(source).resolve()
    catalog = read_json(source / 'release-catalog.json')
    if catalog.get('version') != VERSION or privacy not in PRIVACY:
        raise ValueError('Release version/privacy choice not supported')
    spec = catalog['profiles'][profile]['files']
    target = root / '.ai/installation.json'
    if target.exists() and not refresh:
        raise ValueError('Baseline exists; review intentional changes before using --refresh')
    snapshots = {}
    for item in spec:
        installed = safe_path(root, item['target'])
        if not installed.is_file():
            raise ValueError(f'Install selected profile file first: {item["target"]}')
        actual = sha256(installed)
        if not item['mutable'] and actual != item['sha256']:
            raise ValueError(f'Immutable released file differs: {item["target"]}')
        snapshots[item['target']] = actual
    manifest = {'schema_version':1, 'version':VERSION, 'profile':profile,
                'privacy':privacy, 'recorded_at':datetime.date.today().isoformat(), 'files':snapshots}
    # Verify candidate metadata in isolation before writing to the real project.
    with tempfile.TemporaryDirectory() as folder:
        trial = Path(folder) / 'project'
        shutil.copytree(root / '.ai', trial / '.ai')
        for name in ('AGENTS.md','CLAUDE.md'):
            shutil.copyfile(root / name, trial / name)
        (trial / '.ai/installation.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        (trial / '.ai/release-catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        failures, _ = validate(trial, check_git=False)
        if failures:
            raise ValueError('Candidate baseline rejected: ' + '; '.join(failures))
    # Git is checked against the real target separately by the installed validator.
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (root / '.ai/release-catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return validate(root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--profile', choices=['solo','modular'], required=True)
    parser.add_argument('--privacy', choices=sorted(PRIVACY), required=True)
    parser.add_argument('--refresh', action='store_true', help='Record intentional, reviewed mutable file changes')
    args = parser.parse_args()
    try:
        errors, warnings = record(args.project, Path(__file__).resolve().parents[1], args.profile, args.privacy, args.refresh)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('ERROR: ' + str(exc))
        raise SystemExit(1)
    for error in errors: print('ERROR: ' + error)
    for warning in warnings: print('WARN: ' + warning)
    if errors: raise SystemExit(1)
    print('PASS: reviewed installation baseline recorded')
