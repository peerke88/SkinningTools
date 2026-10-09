#include "averagevtxweight.h"
#include "utils.hpp"
#include <maya/MFnDependencyNode.h>
#include <algorithm>
#include <vector>
#include <cmath>
MSyntax AverageVtxWeight::sNewSyntax() {
    MSyntax syntax;
    syntax.addFlag("sc", "skinCluster", MSyntax::kString);
    syntax.addFlag("wt", "weight", MSyntax::kDouble);
    syntax.addFlag("n", "normalize", MSyntax::kBoolean);
    syntax.useSelectionAsDefault();
    syntax.setObjectType(MSyntax::kStringObjects, 0);
    return syntax;
}
MStatus AverageVtxWeight::ParseArgs(const MArgList& args, MString* skinName, MStringArray* targets) {
    MStatus stat;
    MArgDatabase parser(syntax(), args, &stat); THROWSTAT;
    if (!parser.isFlagSet("sc")) return MS::kInvalidParameter;
    *skinName = parser.flagArgumentString("sc", 0, &stat); THROWSTAT;
    stat = parser.getObjects(*targets); THROWSTAT;
    if (!targets->length()) {
        MSelectionList active;
        stat = MGlobal::getActiveSelectionList(active); THROWSTAT;
        stat = active.getSelectionStrings(*targets); THROWSTAT;
    }
    mWeight = parser.isFlagSet("wt") ? parser.flagArgumentDouble("wt", 0, &stat) : 1.0;
    THROWSTAT;
    if (!std::isfinite(mWeight) || mWeight < 0.0 || mWeight > 1.0) return MS::kInvalidParameter;
    MSelectionList selection;
    stat = selection.add(*skinName); THROWSTAT;
    MObject skin;
    stat = selection.getDependNode(0, skin); THROWSTAT;
    stat = mSkinFn.setObject(skin); THROWSTAT;
    MPlug normal = mSkinFn.findPlug("normalizeWeights", false, &stat); THROWSTAT;
    mNormalize = normal.asInt(&stat) == 1; THROWSTAT;
    if (parser.isFlagSet("n")) { mNormalize = parser.flagArgumentBool("n", 0, &stat); THROWSTAT; }
    MPlug maintain = mSkinFn.findPlug("maintainMaxInfluences", false, &stat); THROWSTAT;
    bool limit = maintain.asBool(&stat); THROWSTAT;
    mMaxinf = 0;
    if (limit) {
        MPlug maximum = mSkinFn.findPlug("maxInfluences", false, &stat); THROWSTAT;
        mMaxinf = maximum.asInt(&stat); THROWSTAT;
        if (mMaxinf < 1) return MS::kInvalidParameter;
    }
    return MS::kSuccess;
}
MStatus AverageVtxWeight::doIt(const MArgList& args) {
    MString skinName;
    MStringArray targets;
    MStatus stat = ParseArgs(args, &skinName, &targets); THROWSTAT;
    MSelectionList merged;
    for (unsigned int i = 0; i < targets.length(); ++i) {
        MSelectionList item;
        stat = item.add(targets[i]); THROWSTAT;
        stat = merged.merge(item); THROWSTAT;
    }
    // One native command owns one mesh; do not silently drop another mesh.
    if (merged.length() != 1) return MS::kInvalidParameter;
    stat = merged.getDagPath(0, mTargetPath, mTargetComponents); THROWSTAT;
    if (mTargetPath.hasFn(MFn::kTransform)) { stat = mTargetPath.extendToShape(); THROWSTAT; }
    if (!mTargetPath.hasFn(MFn::kMesh) || (!mTargetComponents.isNull() &&
        !mTargetComponents.hasFn(MFn::kMeshVertComponent))) return MS::kInvalidParameter;
    stat = mMapping.capture(mSkinFn, mTargetPath); THROWSTAT;
    unsigned int count = mMapping.paths.length();
    if (!count) return MS::kInvalidParameter;
    MItMeshVertex iterator(mTargetPath, mTargetComponents, &stat); THROWSTAT;
    // Canonicalize component order before reading and assembling arrays.
    std::vector<int> selected;
    for (; !iterator.isDone(); iterator.next()) selected.push_back(iterator.index());
    if (selected.empty()) return MS::kInvalidParameter;
    std::sort(selected.begin(), selected.end());
    MIntArray vertices;
    for (int vertex : selected) vertices.append(vertex);
    MFnSingleIndexedComponent component;
    mTargetComponents = component.create(MFn::kMeshVertComponent, &stat); THROWSTAT;
    stat = component.addElements(vertices); THROWSTAT;
    stat = mSkinFn.getWeights(mTargetPath, mTargetComponents, mOldValues, count); THROWSTAT;
    if (mOldValues.length() != vertices.length() * count || !validWeights(mOldValues)) return MS::kInvalidParameter;
    std::vector<bool> locked(count, false);
    for (unsigned int i = 0; i < count; ++i) {
        MFnDependencyNode joint(mMapping.paths[i].node(), &stat); THROWSTAT;
        MPlug lock = joint.findPlug("liw", false, &stat); THROWSTAT;
        locked[i] = lock.asBool(&stat); THROWSTAT;
    }
    mNewValues = mOldValues;
    MItMeshVertex mesh(mTargetPath, MObject::kNullObj, &stat); THROWSTAT;
    for (unsigned int row = 0; row < vertices.length(); ++row) {
        if (mWeight == 0.0) continue;
        int previous;
        stat = mesh.setIndex(vertices[row], previous); THROWSTAT;
        MIntArray neighbors;
        stat = mesh.getConnectedVertices(neighbors); THROWSTAT;
        if (!neighbors.length()) continue; // Isolated vertex is an exact no-op.
        MFnSingleIndexedComponent neighborFn;
        MObject neighborComp = neighborFn.create(MFn::kMeshVertComponent, &stat); THROWSTAT;
        stat = neighborFn.addElements(neighbors); THROWSTAT;
        MDoubleArray adjacent;
        unsigned int adjacentCount;
        stat = mSkinFn.getWeights(mTargetPath, neighborComp, adjacent, adjacentCount); THROWSTAT;
        if (adjacentCount != count || adjacent.length() != neighbors.length()*count || !validWeights(adjacent))
            return MS::kInvalidParameter;
        unsigned int offset = row * count;
        for (unsigned int i = 0; i < count; ++i) {
            if (locked[i]) continue;
            double sum = 0.0;
            for (unsigned int j = i; j < adjacent.length(); j += count) sum += adjacent[j];
            mNewValues[offset+i] = mOldValues[offset+i] * (1.0-mWeight) + sum/neighbors.length()*mWeight;
        }
        if (mMaxinf > 0) {
            unsigned int lockedCount = 0;
            std::vector<unsigned int> ranked;
            for (unsigned int i = 0; i < count; ++i) {
                if (locked[i]) { if (mNewValues[offset+i] > 0.0) ++lockedCount; }
                else ranked.push_back(i);
            }
            if (lockedCount > static_cast<unsigned int>(mMaxinf)) return MS::kInvalidParameter;
            std::sort(ranked.begin(), ranked.end(), [&](unsigned int a, unsigned int b) {
                double left = mNewValues[offset+a], right = mNewValues[offset+b];
                return left == right ? a < b : left > right;
            });
            unsigned int budget = static_cast<unsigned int>(mMaxinf)-lockedCount;
            for (unsigned int i = budget; i < ranked.size(); ++i) mNewValues[offset+ranked[i]] = 0.0;
        }
        if (mNormalize) {
            double lockedSum = 0.0, total = 0.0;
            bool anyUnlocked = false;
            for (unsigned int i = 0; i < count; ++i) {
                if (locked[i]) lockedSum += mNewValues[offset+i];
                else { total += mNewValues[offset+i]; anyUnlocked = true; }
            }
            if (lockedSum > 1.0+1e-6) return MS::kInvalidParameter;
            if (total > 0.0) {
                double factor = std::max(0.0, 1.0-lockedSum) / total;
                for (unsigned int i = 0; i < count; ++i) if (!locked[i]) mNewValues[offset+i] *= factor;
            } else if (lockedSum > 0.0 && lockedSum < 1.0-1e-6 && anyUnlocked) return MS::kInvalidParameter;
        }
    }
    stat = redoIt(); THROWSTAT;
    mReady = true;
    return MS::kSuccess;
}
MStatus AverageVtxWeight::undoIt() {
    return atomicWeights(mSkinFn, mTargetPath, mTargetComponents, mMapping, mOldValues);
}
MStatus AverageVtxWeight::redoIt() {
    return atomicWeights(mSkinFn, mTargetPath, mTargetComponents, mMapping, mNewValues);
}
