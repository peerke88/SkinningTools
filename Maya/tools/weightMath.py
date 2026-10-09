# -*- coding: utf-8 -*-
"""Deterministic row calculations. This module imports neither Maya nor Qt."""
from __future__ import division
import math
import numbers


def validateWeights(weights, checkType=True):
    """Validate values; SDK double arrays already guarantee the numeric type."""
    if any((checkType and not isinstance(w, numbers.Real)) or math.isnan(w) or math.isinf(w)
           or not 0.0 <= w <= 1.0 for w in weights):
        raise ValueError('Weights must be finite values in [0, 1]')


def normalizeWeights(weights, locked):
    """Return a normalized copy of one row, retaining locked and zero values."""
    if len(locked) != len(weights):
        raise ValueError('Lock dimensions do not match weights')
    result = list(weights)
    normalizeWeightsInPlace(result, locked)
    return result


def normalizeWeightsInPlace(weights, locked, offset=0):
    """Normalize a private flat-buffer row without allocating intermediate copies."""
    width = len(locked)
    if offset < 0 or offset + width > len(weights):
        raise ValueError('Lock dimensions do not match weights')
    locked_sum = sum(weights[offset+i] for i in range(width) if locked[i])
    if locked_sum > 1.0 + 1e-6:
        raise ValueError('Locked weights exceed normalization budget')
    unlocked = [i for i in range(width) if not locked[i]]
    total = sum(weights[offset+i] for i in unlocked)
    if total > 0.0:
        factor = max(0.0, 1.0-locked_sum) / total
        for i in unlocked:
            weights[offset+i] *= factor
    elif 0.0 < locked_sum < 1.0-1e-6 and unlocked:
        raise ValueError('No unlocked weight to fill normalization budget')


def limitInfluences(weights, locked, maximum):
    result = list(weights)
    if maximum < 1:
        raise ValueError('Maximum influences must be positive')
    locked_count = sum(locked[i] and result[i] > 0.0 for i in range(len(result)))
    if locked_count > maximum:
        raise ValueError('Locked influences exceed maximum influences')
    ranked = sorted((i for i in range(len(result)) if not locked[i]),
                    key=lambda i: (-result[i], i))
    for i in ranked[maximum-locked_count:]:
        result[i] = 0.0
    return result


def blendWeights(value, original, neighbors, count, normalize=False, maximum=None, locked=None):
    """Blend one row with flat neighbor rows, then apply limits and normalization."""
    if math.isnan(value) or math.isinf(value) or not 0.0 <= value <= 1.0:
        raise ValueError('Smoothing strength must be finite in [0, 1]')
    width = len(original)
    if not width or len(neighbors) != width * count or count < 0:
        raise ValueError('Smoothing weight dimensions do not match')
    validateWeights(original)
    validateWeights(neighbors)
    if value == 0.0 or count == 0:
        return list(original)
    locked = [False] * width if locked is None else list(locked)
    if len(locked) != width:
        raise ValueError('Lock dimensions do not match weights')
    result = [original[i] if locked[i] else original[i] * (1.0-value) +
              sum(neighbors[j] for j in range(i, len(neighbors), width)) / count * value
              for i in range(width)]
    if maximum is not None:
        result = limitInfluences(result, locked, maximum)
    if normalize:
        result = normalizeWeights(result, locked)
    return result


def normalizeEditedWeights(weights, original, locked, selected, current):
    """Preserve the table's selected-cell priority and zero-row fallback policy."""
    weights = list(weights)
    locked_sum = sum(weights[i] for i in locked)
    result = []
    recalc = True
    if locked_sum >= 1.0:
        return [w if i in locked else 0.0 for i, w in enumerate(weights)], recalc
    selected_sum = sum(weights[i] for i in selected if i is not None)
    remaining = list(set(current) - set(selected))
    rest_sum = sum(weights[i] for i in remaining) - locked_sum
    if rest_sum + selected_sum == 0.0:
        weights = list(original)
        selected_sum = sum(weights[i] for i in selected if i is not None)
    if selected_sum + locked_sum >= 1.0:
        for i, w in enumerate(weights):
            result.append(w if i in locked else
                          w/selected_sum*(1.0-locked_sum) if i in selected else 0.0)
    elif selected_sum < 1.0:
        total = selected_sum + locked_sum
        if total >= 1.0 or rest_sum == 0.0:
            if rest_sum == selected_sum == 0.0:
                recalc = False
            other = 0.0
            ratio = (1.0-locked_sum)/selected_sum if selected_sum else 0.0
        else:
            other = (1.0-total)/rest_sum
            ratio = 1.0
        for i, w in enumerate(weights):
            result.append(w if i in locked else w*ratio if i in selected else w*other)
    return result, recalc


def sliderWeights(values, enabled, selected, newValue, solver='uniform'):
    """Preserve the slider's uniform/low/high policies, including zero fallback."""
    count = len(values)
    offset = newValue
    locked_total = sum(values[i] for i in range(count) if i != selected and not enabled[i])
    if offset > 1.0-locked_total:
        offset = newValue = 1.0-locked_total
    result = [0.0] * count
    total = 0.0
    for i in range(count):
        if i == selected:
            continue
        if not enabled[i]:
            offset += values[i]
        else:
            result[i] = values[i]
            total += result[i]
    result[selected] = newValue
    scale = (1.0-offset)/(count-1) if total == 0.0 else (1.0-offset)/total
    for i in range(count):
        if i == selected:
            continue
        if not enabled[i]:
            result[i] = values[i]
        elif solver == 'low':
            result[i] = max(1e-8, result[i])*scale
        elif solver == 'high':
            result[i] *= result[i]/total if total > 0.0 else scale
        elif total == 0.0:
            result[i] = scale
        else:
            result[i] *= scale
    return result
