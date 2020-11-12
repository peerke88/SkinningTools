#ifndef SKIN_WEIGHTS_CMD_H


#include <maya/MpxCommand.h>
#include <maya/MDoubleArray.h>
#include <maya/MDagPathArray.h>
#include <maya/MStringArray.h>
#include <maya/MIntArray.h>
#include <maya/MStatus.h>
#include <maya/MDagPath.h>
#include <maya/MObject.h>
#include <maya/MFnSkinCluster.h>
#include <maya/MSyntax.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MGlobal.h>
#include <maya/MSelectionList.h>
#include <maya/MDagPathArray.h>


class SkinWeights : public MPxCommand  
{  
private:
	bool isQueryInstance;
	MDoubleArray mSetWeights;
	MDoubleArray mUndoWeights;
	MDagPath mMeshPath;
	MObject mMeshComponents;
	MFnSkinCluster mSkin;
	MIntArray mInfluenceIndices;

	MStatus ParseObjects(MStringArray objects);
	MStatus GetSkinWeights();
	MStatus SetSkinWeights(bool isUndo = false);

public:  
	SkinWeights();
	virtual ~SkinWeights(){}
	static void* sCreator();
	virtual bool isUndoable() const; ///< If command was not used as query it is undoable
	virtual bool hasSyntax() const;
	static MSyntax sNewSyntax();

	virtual MStatus doIt(const MArgList& args);
	virtual MStatus redoIt();
	virtual MStatus undoIt();
};


#define SKIN_WEIGHTS_CMD_H
#endif