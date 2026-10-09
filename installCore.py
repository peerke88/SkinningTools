# -*- coding: utf-8 -*-
"""Verified directory installation with recoverable same-volume promotion."""
import hashlib
import json
import os
import shutil
import tempfile
import warnings

MANIFEST = 'package-manifest.json'
REQUIRED_FILES = ('__init__.py', 'Maya/api.py', 'Maya/pluginPaths.py',
                  'Maya/tools/shared.py', 'Maya/tools/weightWrite.py',
                  'Maya/tools/weightMath.py', 'Maya/plugin/SkinEditPlugin.py',
                  'UI/qt_util.py', 'UI/SkinningToolsUI.py')


def inventory(folder):
    result = {}
    for directory, folders, files in os.walk(folder):
        folders[:] = sorted(name for name in folders if name != '__pycache__')
        for name in folders + files:
            if os.path.islink(os.path.join(directory, name)):
                raise ValueError('Package links are unsupported: %s' % name)
        for name in sorted(files):
            if name.endswith(('.pyc', '.pyo')):
                continue
            path = os.path.join(directory, name)
            relative = os.path.relpath(path, folder).replace(os.sep, '/')
            with open(path, 'rb') as stream:
                digest = hashlib.sha256()
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    digest.update(block)
            result[relative] = digest.hexdigest()
    return result


def validatePackage(folder):
    if not os.path.isdir(folder) or os.path.islink(folder):
        raise ValueError('Replacement package must be a real directory')
    actual = inventory(folder)
    for path in REQUIRED_FILES:
        if path not in actual:
            raise ValueError('Replacement package is missing %s' % path)
    manifest = os.path.join(folder, MANIFEST)
    if os.path.isfile(manifest):
        with open(manifest, 'r') as stream:
            expected = json.load(stream)
        if expected.get('format') != 1 or not isinstance(expected.get('files'), dict):
            raise ValueError('Invalid package manifest')
        for path, digest in expected['files'].items():
            if actual.get(path) != digest:
                raise ValueError('Package checksum mismatch: %s' % path)
        if not set(REQUIRED_FILES).issubset(expected['files']):
            raise ValueError('Manifest does not cover required runtime files')
        if set(actual) != set(expected['files']) | set([MANIFEST]):
            raise ValueError('Package contains files outside its manifest')
    return actual


def _inside(path, parent):
    path, parent = os.path.normcase(os.path.realpath(path)), os.path.normcase(os.path.realpath(parent))
    return path == parent or path.startswith(parent + os.sep)


def installPackage(source, destination, keepSettings=True, keepTooltips=True,
                   keepBackup=True, prepare=None):
    """Copy/verify first; rename old tree only when the replacement is ready.

    prepare(stage) may download optional content into the disposable staging tree.
    A successful backup is retained only when requested. Failure retains/restores
    the old tree; a rollback failure reports its recoverable backup path.
    """
    source, destination = os.path.abspath(source), os.path.abspath(destination)
    if _inside(source, destination) or _inside(destination, source):
        raise ValueError('Source and destination installation trees must not overlap')
    if os.path.lexists(destination) and (os.path.islink(destination) or not os.path.isdir(destination)):
        raise ValueError('Existing installation must be a real directory')
    expected = validatePackage(source)
    parent = os.path.dirname(destination)
    if not os.path.isdir(parent):
        os.makedirs(parent)
    stage = tempfile.mkdtemp(prefix='.SkinningTools-stage-', dir=parent)
    backup = None
    promoted = False
    movedOld = False
    try:
        # copytree requires an absent leaf, so keep the owned staging container.
        replacement = os.path.join(stage, 'SkinningTools')
        shutil.copytree(source, replacement, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
        if inventory(replacement) != expected:
            raise ValueError('Staged package differs from replacement source')
        validatePackage(replacement)
        if keepSettings and os.path.isfile(os.path.join(destination, 'UI', 'settings.ini')):
            shutil.copy2(os.path.join(destination, 'UI', 'settings.ini'),
                         os.path.join(replacement, 'UI', 'settings.ini'))
        oldTooltips = os.path.join(destination, 'Maya', 'tooltips')
        if keepTooltips and os.path.isdir(oldTooltips):
            # Merge preserved optional assets without moving them out of the old tree.
            inventory(oldTooltips)  # Reject links before any copy.
            for directory, folders, files in os.walk(oldTooltips):
                target = os.path.join(replacement, 'Maya', 'tooltips', os.path.relpath(directory, oldTooltips))
                if not os.path.isdir(target):
                    os.makedirs(target)
                for name in files:
                    shutil.copy2(os.path.join(directory, name), os.path.join(target, name))
        if prepare is not None:
            prepare(replacement)
        final = inventory(replacement)
        if not set(REQUIRED_FILES).issubset(final):
            raise ValueError('Preparation removed required runtime files')
        # Optional preparation must not alter executable/core package files.
        for path, digest in expected.items():
            if path == 'UI/settings.ini' or path.startswith('Maya/tooltips/'):
                continue
            if final.get(path) != digest:
                raise ValueError('Preparation altered package file: %s' % path)
        if os.path.exists(destination):
            backup = tempfile.mkdtemp(prefix='Backup_SkinningTools-', dir=parent)
            os.rmdir(backup)
            os.rename(destination, backup)
            movedOld = True
        os.rename(replacement, destination)
        promoted = True
        if inventory(destination) != final:
            raise ValueError('Installed package differs from verified staging tree')
    except Exception:
        try:
            if promoted:
                # Only remove our verified promoted tree, under the selected parent.
                if not _inside(destination, parent):
                    raise RuntimeError('Invalid rollback destination')
                shutil.rmtree(destination)
            if movedOld:
                os.rename(backup, destination)
        except Exception as error:
            raise RuntimeError('Installation rollback failed; previous tree is at %s: %s' % (backup, error))
        raise
    finally:
        if _inside(stage, parent) and os.path.isdir(stage):
            try:
                shutil.rmtree(stage)
            except OSError as error:
                warnings.warn('Retained staging directory %s: %s' % (stage, error))
    if backup and not keepBackup:
        # Cleanup follows successful verification; failure leaves a safe extra backup.
        try:
            if not _inside(backup, parent):
                raise RuntimeError('Invalid backup path')
            shutil.rmtree(backup)
            backup = None
        except OSError as error:
            warnings.warn('Installed successfully; retained backup %s: %s' % (backup, error))
    return backup
