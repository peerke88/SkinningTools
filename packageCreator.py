# -*- coding: utf-8 -*-
"""Reproducible ZIP release tooling (Python 3.9+); importing does not build."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile

curFolder = os.path.normpath(os.path.dirname(__file__))
relPath = os.path.dirname(curFolder)
baseFolder = os.path.join(curFolder, 'package')
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def setVersionDate():
    """Return an explicit date version; source files are no longer rewritten."""
    return '5.0.' + datetime.date.today().strftime('%Y%m%d')


def releaseFiles(sourceRoot):
    """Tracked allowlisted runtime/assets; never collect local settings or data."""
    raw = subprocess.check_output(['git', 'ls-files', '-z'], cwd=str(sourceRoot))
    paths = []
    for name in raw.decode('utf-8').split('\0'):
        if not name:
            continue
        parts = name.split('/')
        if any(part.lower() in ('build', 'x64', '__pycache__', '.vs', '.git', 'promotion') for part in parts):
            continue
        if name.endswith(('.pyc', '.pyo', '.ma', '.mb', '.skinWeights', '.tmp', '.bak', '.user')):
            continue
        if name == 'UI/settings.ini':
            continue
        if name.startswith(('Maya/', 'UI/', 'ThirdParty/')) or name in (
                '__init__.py', 'py23.py', 'installCore.py', 'README.md',
                'docs/development/THIRD_PARTY.md', 'docs/development/RELEASE_PROCESS.md') or name.lower().startswith(('license', 'copying')):
            paths.append(name)
    # New required files must already be tracked/staged to enter a release.
    return sorted(paths)


def createPackage(output, sourceRoot=None, version=None, files=None):
    """Build without changing source/version/settings; same inputs give same bytes.

    files is for an explicit reviewed source list (used by disposable tests).
    Normal releases use Git's tracked allowlist, including all bundled license
    notices and native project sources/binaries. No archive is uploaded.
    """
    sourceRoot = Path(curFolder if sourceRoot is None else sourceRoot).resolve()
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('Refusing to overwrite existing package: %s' % output)
    names = releaseFiles(sourceRoot) if files is None else sorted(files)
    entries = {}
    for name in names:
        if name.startswith('/') or '\\' in name or '..' in name.split('/'):
            raise ValueError('Invalid package source path: %s' % name)
        source = sourceRoot / name
        if source.is_symlink() or sourceRoot not in source.resolve().parents:
            raise ValueError('Package source must stay inside source root: %s' % name)
        target = name[len('docs/development/'):] if name.startswith('docs/development/') else name
        entries['SkinningTools/' + target] = source.read_bytes()
    for name in ('dragDropInstall.mel', 'packageInstaller.py'):
        entries[name] = (sourceRoot / name).read_bytes()
    entries['__init__.py'] = b''
    readme = 'SkinningTools/README.md'
    if readme in entries:
        for name in ('THIRD_PARTY.md', 'RELEASE_PROCESS.md'):
            entries[readme] = entries[readme].replace(('docs/development/' + name).encode('ascii'), name.encode('ascii'))
    ui = 'SkinningTools/UI/SkinningToolsUI.py'
    if version is None:
        match = re.search(br'__VERSION__\s*=\s*["\']([^"\']+)', entries[ui])
        if match is None:
            raise ValueError('Missing release version')
        version = match.group(1).decode('ascii')
    if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)+', version):
        raise ValueError('Invalid release version')
    for name in (ui, 'packageInstaller.py'):
        entries[name] = re.sub(br'(__VERSION__\s*=\s*)["\'][^"\']+["\']',
                              lambda match: match.group(1) + b'"' + version.encode('ascii') + b'"', entries[name])
    debug = 'SkinningTools/UI/utils.py'
    if debug in entries:
        entries[debug] = entries[debug].replace(b'isDebug = True', b'isDebug = False')
    from installCore import REQUIRED_FILES, MANIFEST
    for name in REQUIRED_FILES:
        if 'SkinningTools/' + name not in entries:
            raise ValueError('Missing release runtime file: %s' % name)
    hashes = {name[len('SkinningTools/'):]: hashlib.sha256(data).hexdigest()
              for name, data in entries.items() if name.startswith('SkinningTools/')}
    entries['SkinningTools/' + MANIFEST] = (json.dumps(
        {'format': 1, 'version': version, 'files': hashes}, sort_keys=True, indent=2) + '\n').encode('utf-8')
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation avoids overwriting an existing release even in a race.
    with output.open('xb') as stream:
        with zipfile.ZipFile(stream, 'w') as archive:
            for name, data in sorted(entries.items()):
                info = zipfile.ZipInfo(name, FIXED_TIME)
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data, compresslevel=9)
    return {'version': version, 'files': len(entries),
            'sha256': hashlib.sha256(output.read_bytes()).hexdigest(), 'path': str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=os.path.join(baseFolder, 'SkinningTools.zip'))
    parser.add_argument('--version', help='Explicit stamp applied only to packaged copies')
    args = parser.parse_args()
    print(json.dumps(createPackage(args.output, version=args.version), indent=2))


if __name__ == '__main__':
    main()
