#ifndef UTILS_HPP
#define UTILS_HPP
#include <maya/MFnSkinCluster.h>
#include <maya/MFnMesh.h>
#include <maya/MPlug.h>
#include <maya/MGlobal.h>
#include <maya/MDagPathArray.h>
#include <maya/MDagPath.h>
#include <maya/MIntArray.h>
#include <maya/MDoubleArray.h>
#include <cmath>
#define THROWSTAT if(stat != MS::kSuccess){ stat.perror(__FILE__); return stat; }

// Kept identical in both existing native projects until M4 consolidation.
struct WeightMapping {
    MDagPathArray paths;
    MIntArray logical;
    MIntArray physical;
    int vertices = -1;
    MStatus capture(MFnSkinCluster& skin, const MDagPath& dag) {
        MStatus stat;
        skin.influenceObjects(paths, &stat); THROWSTAT;
        for (unsigned int i = 0; i < paths.length(); ++i) {
            logical.append(skin.indexForInfluenceObject(paths[i], &stat)); THROWSTAT;
            physical.append(i);
        }
        if (dag.hasFn(MFn::kMesh)) {
            MFnMesh mesh(dag, &stat); THROWSTAT;
            vertices = mesh.numVertices(&stat); THROWSTAT;
        }
        return MS::kSuccess;
    }
    MStatus validate(MFnSkinCluster& skin, const MDagPath& dag) const {
        MStatus stat;
        MDagPathArray current;
        skin.influenceObjects(current, &stat); THROWSTAT;
        if (current.length() != paths.length()) return MS::kInvalidParameter;
        for (unsigned int i = 0; i < paths.length(); ++i) {
            if (current[i].fullPathName() != paths[i].fullPathName() ||
                skin.indexForInfluenceObject(current[i], &stat) != logical[i])
                return MS::kInvalidParameter;
            THROWSTAT;
        }
        if (vertices >= 0) {
            MFnMesh mesh(dag, &stat); THROWSTAT;
            if (mesh.numVertices(&stat) != vertices) return MS::kInvalidParameter;
            THROWSTAT;
        }
        return MS::kSuccess;
    }
};
inline bool validWeights(const MDoubleArray& weights) {
    for (unsigned int i = 0; i < weights.length(); ++i)
        if (!std::isfinite(weights[i]) || weights[i] < 0.0 || weights[i] > 1.0) return false;
    return true;
}
inline bool sameWeights(const MDoubleArray& a, const MDoubleArray& b) {
    if (a.length() != b.length()) return false;
    for (unsigned int i = 0; i < a.length(); ++i) if (a[i] != b[i]) return false;
    return true;
}
inline MStatus exactWeights(MFnSkinCluster& skin, const MDagPath& dag,
                           const MObject& component, MIntArray& indices,
                           MDoubleArray& weights, bool* attempted = nullptr) {
    if (attempted) *attempted = false;
    MStatus stat;
    MPlug normal = skin.findPlug("normalizeWeights", false, &stat); THROWSTAT;
    int normalValue = normal.asInt(&stat); THROWSTAT;
    MPlug maintain = skin.findPlug("maintainMaxInfluences", false, &stat); THROWSTAT;
    bool maintainValue = maintain.asBool(&stat); THROWSTAT;
    if ((normalValue && (normal.isLocked() || normal.isDestination())) ||
        (maintainValue && (maintain.isLocked() || maintain.isDestination())))
        return MS::kInvalidParameter;
    MStatus result = MS::kSuccess;
    if (normalValue) result = normal.setValue(0);
    if (result && maintainValue) result = maintain.setValue(false);
    if (result) {
        if (attempted) *attempted = true;
        result = skin.setWeights(dag, component, indices, weights, false);
    }
    // Always attempt both restorations, even when an earlier operation failed.
    MStatus restoreMaintain = maintainValue ? maintain.setValue(maintainValue) : MS::kSuccess;
    MStatus restoreNormal = normalValue ? normal.setValue(normalValue) : MS::kSuccess;
    if (!result) return result;
    if (!restoreMaintain) return restoreMaintain;
    return restoreNormal;
}
inline MStatus atomicWeights(MFnSkinCluster& skin, const MDagPath& dag,
                            const MObject& component, WeightMapping& mapping,
                            MDoubleArray& weights) {
    MStatus stat = mapping.validate(skin, dag); THROWSTAT;
    MDoubleArray before, actual;
    unsigned int count;
    stat = skin.getWeights(dag, component, before, count); THROWSTAT;
    if (weights.length() != before.length() || !validWeights(weights)) return MS::kInvalidParameter;
    bool attempted = false;
    stat = exactWeights(skin, dag, component, mapping.physical, weights, &attempted);
    if (!stat && !attempted) return stat;
    if (stat) stat = skin.getWeights(dag, component, actual, count);
    if (stat && sameWeights(actual, weights)) return MS::kSuccess;
    MStatus failed = stat ? MS::kFailure : stat;
    MStatus rollback = exactWeights(skin, dag, component, mapping.physical, before);
    if (rollback) rollback = skin.getWeights(dag, component, actual, count);
    if (!rollback || !sameWeights(actual, before)) MGlobal::displayError("Native skin weight rollback failed");
    return failed;
}
#endif
