#include "skinweights.h"
#include "utils.hpp"
#include <maya/MFnDependencyNode.h>
const char* kWeightShort = "nwt";
const char* kWeightLong = "newWeights";
SkinWeights::SkinWeights() : isQueryInstance(false), mReady(false) {}
void* SkinWeights::sCreator() { return new SkinWeights(); }
bool SkinWeights::isUndoable() const { return !isQueryInstance && mReady; }
bool SkinWeights::hasSyntax() const { return true; }
MSyntax SkinWeights::sNewSyntax() {
    MSyntax syntax;
    syntax.setObjectType(MSyntax::kStringObjects, 2, 2);
    syntax.useSelectionAsDefault(true);
    syntax.addFlag(kWeightShort, kWeightLong, MSyntax::kDouble);
    syntax.makeFlagMultiUse(kWeightShort);
    syntax.enableQuery(true);
    syntax.enableEdit(false);
    return syntax;
}
MStatus SkinWeights::doIt(const MArgList& args) {
    MStatus stat;
    MArgDatabase parser(syntax(), args, &stat); THROWSTAT;
    isQueryInstance = parser.isQuery(&stat); THROWSTAT;
    MStringArray objects;
    stat = parser.getObjects(objects); THROWSTAT;
    if (objects.length() != 2) return MS::kInvalidParameter;
    MStringArray parts;
    stat = objects[0].split('.', parts); THROWSTAT;
    objects[0] = parts[0];
    stat = ParseObjects(objects); THROWSTAT;
    if (isQueryInstance) return GetSkinWeights();
    unsigned int count;
    stat = mSkin.getWeights(mMeshPath, mMeshComponents, mUndoWeights, count); THROWSTAT;
    unsigned int uses = parser.numberOfFlagUses(kWeightShort);
    if (!uses || uses != mUndoWeights.length()) return MS::kInvalidParameter;
    mSetWeights.setLength(uses);
    for (unsigned int i = 0; i < uses; ++i) {
        MArgList flag;
        stat = parser.getFlagArgumentList(kWeightShort, i, flag); THROWSTAT;
        mSetWeights[i] = flag.asDouble(0, &stat); THROWSTAT;
    }
    if (!validWeights(mSetWeights) || !validWeights(mUndoWeights)) return MS::kInvalidParameter;
    // Preserve joint locks while retaining legacy raw (unnormalized) setter behavior.
    unsigned int influences = mMapping.paths.length();
    for (unsigned int i = 0; i < influences; ++i) {
        MFnDependencyNode joint(mMapping.paths[i].node(), &stat); THROWSTAT;
        MPlug lock = joint.findPlug("liw", false, &stat); THROWSTAT;
        bool locked = lock.asBool(&stat); THROWSTAT;
        if (locked) for (unsigned int row = i; row < uses; row += influences)
            mSetWeights[row] = mUndoWeights[row];
    }
    stat = SetSkinWeights(); THROWSTAT;
    mReady = true;
    return MS::kSuccess;
}
MStatus SkinWeights::redoIt() { return isQueryInstance ? GetSkinWeights() : SetSkinWeights(); }
MStatus SkinWeights::undoIt() { return SetSkinWeights(true); }
MStatus SkinWeights::ParseObjects(MStringArray objects) {
    MSelectionList selection;
    MStatus stat = MS::kFailure;
    const char* suffixes[] = {".vtx[*]", ".cv[*][*]", ".cv[*]", ".pt[*][*][*]"};
    for (const char* suffix : suffixes) {
        selection.clear();
        stat = MGlobal::getSelectionListByName(objects[0] + suffix, selection);
        if (stat && selection.length()) break;
    }
    THROWSTAT;
    stat = selection.getDagPath(0, mMeshPath, mMeshComponents); THROWSTAT;
    selection.clear();
    stat = selection.add(objects[1]); THROWSTAT;
    MObject skin;
    stat = selection.getDependNode(0, skin); THROWSTAT;
    stat = mSkin.setObject(skin); THROWSTAT;
    return mMapping.capture(mSkin, mMeshPath);
}
MStatus SkinWeights::GetSkinWeights() {
    MDoubleArray weights;
    unsigned int count;
    MStatus stat = mSkin.getWeights(mMeshPath, mMeshComponents, weights, count); THROWSTAT;
    setResult(weights);
    return MS::kSuccess;
}
MStatus SkinWeights::SetSkinWeights(bool isUndo) {
    return atomicWeights(mSkin, mMeshPath, mMeshComponents, mMapping,
                         isUndo ? mUndoWeights : mSetWeights);
}
