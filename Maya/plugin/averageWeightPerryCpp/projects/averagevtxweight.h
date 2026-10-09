#ifndef AVERAGE_VTX_WEIGHT_H

#include <maya/MPxCommand.h>
#include "utils.hpp"

#include <maya/MFnSingleIndexedComponent.h>
#include <maya/MFnSkinCluster.h>

#include <maya/MItMeshVertex.h>
#include <maya/MItSurfaceCV.h>

#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MDagPath.h>
#include <maya/MDagPathArray.h>
#include <maya/MDoubleArray.h>
#include <maya/MGlobal.h>
#include <maya/MObject.h>
#include <maya/MSelectionList.h>
#include <maya/MStatus.h>
#include <maya/MString.h>
#include <maya/MSyntax.h>
#include <maya/MIntArray.h>


class AverageVtxWeight : public MPxCommand
{
private:
	MDagPath mTargetPath;
	MObject mTargetComponents;

	MFnSkinCluster mSkinFn;
	WeightMapping mMapping;
	bool mReady;

	bool mNormalize;
	double mWeight;
	int mMaxinf;
	MDoubleArray mOldValues;
	MDoubleArray mNewValues;
	MDoubleArray mZeroValues;

	MStatus ParseArgs(const MArgList& args, MString* outSkinClusterName, MStringArray* outTargetNames);
	
public:
	AverageVtxWeight() : mReady(false), mNormalize(false), mWeight(1.0), mMaxinf(0) {}
	virtual ~AverageVtxWeight() {}
	static void* sCreator(){ return new AverageVtxWeight(); }
	virtual bool isUndoable() const override { return mReady; }
	virtual bool hasSyntax() const override { return true; }

	static MSyntax sNewSyntax();
	virtual MStatus doIt(const MArgList& args) override;
	virtual MStatus undoIt() override;
	virtual MStatus redoIt() override;
};


#define AVERAGE_VTX_WEIGHT_H
#endif
