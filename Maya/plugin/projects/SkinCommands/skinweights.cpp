#include "skinweights.h"
#include "utils.hpp"
#include <iostream>


const char* kWeightShort = "nwt";
const char* kWeightLong = "newWeights";


SkinWeights::SkinWeights()
{
	isQueryInstance = false; 
}


void* SkinWeights::sCreator()
{ 
	return new SkinWeights();
}


bool SkinWeights::isUndoable() const
{
	return !isQueryInstance; 
} ///< If command was not used as query it is undoable


bool SkinWeights::hasSyntax() const
{ 
	return true; 
}


MSyntax SkinWeights::sNewSyntax()
{
	MSyntax syntax;
	syntax.setObjectType(MSyntax::kStringObjects, 2); //mesh_node_name, skin_cluster_node_name
	syntax.useSelectionAsDefault(true); //allow viewport based input
	syntax.setMinObjects(2);
	syntax.setMaxObjects(2); //we can't use anything other than 1 mesh and 1 skinCluster

	syntax.addFlag(kWeightShort, kWeightLong, MSyntax::kDouble); //assumed to be set in query by default, multi-use because it must take ALL the weights on the skinCluster in one go
	syntax.makeFlagMultiUse(kWeightShort);

	syntax.enableQuery(true);
	syntax.enableEdit(false); //default behaviour always edits

	return syntax;
}


MStatus SkinWeights::doIt( const MArgList& args )
{  
	MStatus stat;
	MArgList arg;
	MArgDatabase argParser(syntax(), args);
	isQueryInstance = argParser.isQuery(&stat);

	//get mesh and skin cluster
	MStringArray objects;
	stat = argParser.getObjects(objects); THROWSTAT;
	MStringArray name_attr;
	int n = objects.length();
	if (n < 2)
	{
		MGlobal::displayError("Call to get/set skin weights failed. Required a mesh & skin-cluster arguments missing.");
		return MS::kFailure;
	}
	
	objects[0].split('.', name_attr);
	objects[0] = name_attr[0];
	ParseObjects(objects);

	//get weights if setting weights
	if(!isQueryInstance)
	{
		unsigned int n = argParser.numberOfFlagUses(kWeightShort); //< for some reason it refuses to find the number of flags used by the set flag
		mSetWeights.setLength(n);
		for(unsigned int i = 0 ; i < n ; ++i)
		{
			argParser.getFlagArgumentList(kWeightShort, i, arg);
			mSetWeights[i] = arg.asDouble(i);
		}
	}

	return redoIt();
}


MStatus SkinWeights::redoIt()
{
	if(isQueryInstance)
	{
		GetSkinWeights();
	}
	else
	{
		SetSkinWeights();
	}
	return MS::kSuccess;
}


MStatus SkinWeights::undoIt()
{
	SetSkinWeights(true);
	return MS::kSuccess;
}

inline const char * const BoolToString(bool b)
{
  return b ? "true" : "false";
}
MStatus SkinWeights::ParseObjects(MStringArray objects)
{
	//get mesh
	MSelectionList selectionList;
	MStatus stat;
	bool Test = true;
	Test = MGlobal::getSelectionListByName(objects[0]+".vtx[*]", selectionList); THROWSTAT;
	
	if (Test == false){
		Test = MGlobal::getSelectionListByName(objects[0]+".cv[*][*]", selectionList); THROWSTAT;
	}
	if (Test == false){
		Test = MGlobal::getSelectionListByName(objects[0] +".cv[*]", selectionList); THROWSTAT;
	}

	if (Test == false){
		stat = MGlobal::getSelectionListByName(objects[0] +".pt[*][*][*]", selectionList); THROWSTAT;
	}
	stat = selectionList.getDagPath(0, mMeshPath, mMeshComponents); THROWSTAT;
	
	//get skin cluster
	stat = selectionList.clear(); THROWSTAT;
	stat = MGlobal::getSelectionListByName(objects[1], selectionList); THROWSTAT;
	MObject skinObj;
	stat = selectionList.getDependNode(0, skinObj); THROWSTAT;
	stat = mSkin.setObject(skinObj); THROWSTAT;

	//get influences
	MDagPathArray paths;
	unsigned int num = mSkin.influenceObjects(paths, &stat); THROWSTAT;
	for (unsigned int i = 0; i < num; ++i)
	{
		stat = mInfluenceIndices.append(mSkin.indexForInfluenceObject(paths[i])); THROWSTAT;
	}
	return stat;
}


MStatus SkinWeights::GetSkinWeights()
{
	MDoubleArray outWeights;
	int numInfluences = 0;
	MStatus stat = mSkin.getWeights(mMeshPath, mMeshComponents, mInfluenceIndices, outWeights); THROWSTAT;
	setResult(outWeights);
	return stat;
}


MStatus SkinWeights::SetSkinWeights(bool isUndo)
{
	if(isUndo)
		return mSkin.setWeights(mMeshPath, mMeshComponents, mInfluenceIndices, mUndoWeights, false);
	return mSkin.setWeights(mMeshPath, mMeshComponents, mInfluenceIndices, mSetWeights, false, &mUndoWeights);
}