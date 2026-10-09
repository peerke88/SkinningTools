# -*- coding: utf-8 -*-
"""Deterministic native ownership and loading; no Qt dependency."""
import os
import platform


def mayaVersion(commands):
    """Use Maya's API year, independent of launcher path and update labels."""
    value = int(commands.about(apiVersion=True))
    text = str(value)
    year = int(text[:4])
    if len(text) < 6 or not 2000 <= year <= 2099:
        raise ValueError('Unsupported Maya API version: %s' % value)
    return str(year)


def pluginSuffix(system=None):
    system = platform.system() if system is None else system
    try:
        return {'Windows': '.mll', 'Darwin': '.bundle', 'Linux': '.so'}[system]
    except KeyError:
        raise ValueError('Unsupported plugin platform: %s' % system)


def _exactPath(root, parts):
    """Accept legacy folder/file casing, but never an ambiguous match."""
    for part in parts:
        if not os.path.isdir(root):
            return None
        matches = sorted(name for name in os.listdir(root) if name.lower() == part.lower())
        if len(matches) > 1:
            raise RuntimeError('Ambiguous plugin path in %s: %s' % (root, matches))
        if not matches:
            return None
        root = os.path.join(root, matches[0])
    return root if os.path.isfile(root) else None


def resolve(pluginName, version, system=None, root=None):
    """Resolve only known command owners for the exact host; no ABI fallback."""
    root = os.path.join(os.path.dirname(__file__), 'plugin') if root is None else root
    suffix = pluginSuffix(system)
    name = pluginName.lower()
    if name.endswith(suffix):
        name = name[:-len(suffix)]
    if name == 'skincommands':
        owners = [('averageWeightPerryCpp', 'comp', 'Maya%s' % version, 'plug-ins'),
                  ('skinToolWeightsCpp', 'comp', 'Maya%s' % version, 'plug-ins')]
        filename = 'skinCommands' + suffix
    elif name == 'smooth_brush_maya':
        # The other tree contains same-named binaries with uncertain ownership.
        owners = [('smoothBrushRodCpp', 'lib', 'maya%s' % version, 'release')]
        filename = 'smooth_brush_maya' + suffix
    else:
        raise ValueError('Unknown native plugin owner: %s' % pluginName)
    for owner in owners:
        path = _exactPath(root, owner + (filename,))
        if path:
            return path
    return None


def loadPlugin(path, commands):
    """Load the exact file or propagate failure before running its caller."""
    if not path or not os.path.isfile(path):
        raise RuntimeError('Matching Maya plugin is unavailable: %s' % path)
    path = os.path.abspath(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    loaded = path if commands.pluginInfo(path, query=True, loaded=True) else None
    if loaded is None and commands.pluginInfo(stem, query=True, loaded=True):
        loaded = stem
    if loaded is not None:
        actual = commands.pluginInfo(loaded, query=True, path=True)
        if os.path.normcase(os.path.realpath(actual)) != os.path.normcase(os.path.realpath(path)):
            raise RuntimeError('Plugin name is already owned by %s; requested %s' % (actual, path))
    else:
        commands.loadPlugin(path)
    if not commands.pluginInfo(path, query=True, loaded=True):
        raise RuntimeError('Maya did not load plugin: %s' % path)
