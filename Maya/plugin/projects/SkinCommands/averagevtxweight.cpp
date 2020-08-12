#include "AverageVtxWeight.h"
#include "utils.hpp"
#include <vector>
#include <algorithm> 

#define ALMOSTONE 0.99999999

MSyntax AverageVtxWeight::sNewSyntax()
{
	MSyntax syntax;
	syntax.addFlag("sc", "skinCluster", MSyntax::kString);
	syntax.addFlag("wt", "weight", MSyntax::kDouble);
	syntax.addFlag("n", "normalize", MSyntax::kBoolean);
	syntax.useSelectionAsDefault();
	syntax.setObjectType(MSyntax::kStringObjects, 1);
	return syntax;
}


MStatus AverageVtxWeight::ParseArgs(const MArgList& args, MString* outSkinClusterName, MStringArray* outTargetNames)
{
	MStatus stat;
	MArgDatabase argData(syntax(), args);

	if(argData.isFlagSet("sc", &stat)) 
	{
		THROWSTAT;
		*outSkinClusterName = argData.flagArgumentString("sc", 0, &stat);
	}
	else if(argData.isFlagSet("skinCluster", &stat))
	{
		THROWSTAT;
		*outSkinClusterName = argData.flagArgumentString("skinCluster", 0, &stat);
	}
	else //-skinCluster flag is required
	{
		THROWSTAT;
		return MS::kInvalidParameter;
	}
	THROWSTAT;

	stat = argData.getObjects(*outTargetNames);
	THROWSTAT;

	if(argData.isFlagSet("wt", &stat))
	{
		THROWSTAT;
		mWeight = argData.flagArgumentDouble("wt", 0, &stat);
		THROWSTAT;
	}
	else if(argData.isFlagSet("weight", &stat))
	{
		THROWSTAT;
		mWeight = argData.flagArgumentDouble("weight", 0, &stat);
		THROWSTAT;
	}
	else
	{
		mWeight = 1;
	}

	if(argData.isFlagSet("n", &stat))
	{
		THROWSTAT;
		mNormalize = argData.flagArgumentBool("n", 0, &stat);
		THROWSTAT;
	}
	else if(argData.isFlagSet("normalize", &stat))
	{
		THROWSTAT;
		mNormalize = argData.flagArgumentBool("normalize", 0, &stat);
		THROWSTAT;
	}
	else
	{
		MString result;
		MGlobal::executePythonCommand( MString( "cmds.getAttr( '") + *outSkinClusterName + ".normalizeWeights');", result);
		int normal = atoi(result.asChar());

		if (normal == 1){
			mNormalize = true;	
		}
		else{
			mNormalize = false;
		}
	}
	MString result1;
	MGlobal::executePythonCommand( MString( "cmds.getAttr( '") + *outSkinClusterName + ".maintainMaxInfluences');", result1);
	bool maintainMax = (bool)result1.asChar();
	// MGlobal::executePythonCommand( MString( "print 'DEBUG:','" )+maintainMax +"';");
	if (maintainMax == true){
		MString result2;
		MGlobal::executePythonCommand( MString( "cmds.getAttr( '") + *outSkinClusterName + ".maxInfluences');", result2);
		mMaxinf	= atoi(result2.asChar());
		// MGlobal::executePythonCommand( MString( "print 'DEBUG:','" )+mMaxinf +"';");
	}
	else{
		mMaxinf = 0;
	}

	return MS::kSuccess;
}


MStatus AverageVtxWeight::doIt(const MArgList& args)
{
	MString* skinClusterName = new MString();
	MStringArray* targetNames = new MStringArray();
	MStatus stat = ParseArgs(args, skinClusterName, targetNames);
	//mNewValues = MDoubleArray();
	// check whether all required flags were found, else return error
	if(stat != MStatus::kSuccess)
	{
		MGlobal::displayError("Call to AverageVtxWeight() is missing required flag(s) -skinCluster (sc) and/or -index (i).");
		return stat;
	}

	// get skin cluster
	MSelectionList li;
	li.add(*skinClusterName);
	MObject skinObj;
	li.getDependNode(0, skinObj);

	if(skinObj.isNull()) // Object with name given to -skinCluster flag does not exist.
	{
		MGlobal::displayError("AverageVtxWeight() flag -skinCluster (sc) could not find the object: " + *skinClusterName);
		return MS::kInvalidParameter; 
	}

	// if(!skinObj.hasFn(MFn::kSkinClusterFilter)) // Object with name given to -skinCluster flag is not a skinCluster
	// {
	// 	MGlobal::displayError("AverageVtxWeight() flag -skinCluster (sc) got a non-skincluster object: " + *skinClusterName);
	// 	return MS::kInvalidParameter; 
	// }
	mSkinFn.setObject(skinObj);


	// get target component
	li.clear();
	for(unsigned int i = 0; i < targetNames->length(); ++i)
	{
		stat = li.add((*targetNames)[i]);
		if(stat != MStatus::kSuccess)
		{
			MGlobal::displayError("Object passed to AveragetVtxWeight() could not be found: " + (*targetNames)[i]);
			return stat;
		}
	}
	li.getDagPath(0, mTargetPath, mTargetComponents);
	// mTargetComponents = MFn::kMeshVertComponent;
	return redoIt();
}


MStatus AverageVtxWeight::undoIt()
{
	return mSkinFn.setWeights(mTargetPath, mTargetComponents, mInfluenceIndices, mOldValues, false);
}

MStatus AverageVtxWeight::redoIt()
{
	MStatus stat;
	MItMeshVertex iter(mTargetPath, mTargetComponents);
	
    MDagPathArray temp;
	unsigned int numInfluences = mSkinFn.influenceObjects(temp);
	if(mInfluenceIndices.length() == 0)
	{
		for (unsigned int i = 0; i < numInfluences; ++i)
		{
			mInfluenceIndices.append(i);
		}
	}

	bool firstDoIt = false;
	if(mNewValues.length() == 0)
	{
		// iterate over all given components
		while(!iter.isDone())
		{
			MDoubleArray adjacentValues;
			MDoubleArray oldValues;
			MIntArray adjacentIndices;
			// get adjacent vertices to copy weights fro
			iter.getConnectedVertices(adjacentIndices);
			MObject adjacentComponents = MFnSingleIndexedComponent().create(MFn::kMeshVertComponent);
			MFnSingleIndexedComponent(adjacentComponents).addElements(adjacentIndices);
			// get current values of involved vertices
			stat = mSkinFn.getWeights(mTargetPath, iter.currentItem(), oldValues, numInfluences);
			stat = mSkinFn.getWeights(mTargetPath, adjacentComponents, adjacentValues, numInfluences);
			if(stat != MS::kSuccess)
			{
				MGlobal::displayError("Error in AverageVtxWeight. Probably the skinCluster provided does not belong to the vertices provided.");
				return MS::kFailure;
			}
			// compute new average weight for this component
			MDoubleArray newValues(numInfluences, 0.0);
			// stack all adjacent weights
			for(unsigned int i = 0 ; i < adjacentValues.length() ; ++i)
			{
				newValues[i % numInfluences] += adjacentValues[i];
			}
			// get average by dividing by num influences
			unsigned int numAdjacentVertices = adjacentIndices.length();
			for(unsigned int i = 0 ; i < numInfluences ; ++i)
			{
				newValues[i] /= (double)numAdjacentVertices;
				// apply weight flag
				newValues[i] = (newValues[i] - oldValues[i]) * mWeight + oldValues[i];
			}

			// cache results for undo & redo
			for(unsigned int i = 0; i < newValues.length(); ++i)
			{
				double v = newValues[i] > ALMOSTONE ? ALMOSTONE : newValues[i];
				v = v < 0.0 ? 0.0 : v;
				mNewValues.append(newValues[i]);
				mZeroValues.append(0.0f);
			}

			iter.next();
		}
		
		if (mNewValues.length() == 0) {
			MGlobal::displayInfo("huile");
			return MS::kSuccess;
		}
		

		// calculated per vertex so go nuts!!
		// make sure only "maxinfluences" amount influences are used
		// MGlobal::executePythonCommand( MString( "print 'DEBUG:','" )+mMaxinf +"';");
		if( mMaxinf > 0 )
		{	
			int len = mNewValues.length();
			double* foo = new double[len];
			double* foo1 = new double[len];
			
			std::vector<double> vec(len, 0.0);
			for (int w = 0; w < len; ++w) {
				vec[w] = mNewValues[w];
				foo[w] = mNewValues[w];
				foo1[w] = 0.0;
			}
			MDoubleArray newDoubleArray( len, 0.0 ); 
			// MGlobal::executePythonCommand( MString( "print 'DEBUG:','" )+mMaxinf +"';");
			for (int minf = 0; minf < mMaxinf; ++minf) {
				double maxElement = *std::max_element(vec.begin(), vec.end());
				auto it = std::find(vec.begin(), vec.end(), maxElement);
				int index;
				if (it == vec.end())
				{
				  // element not in vector
				} else
				{
				  index = std::distance(vec.begin(), it);
				}
				vec[index] = -1.0;
				foo1[index] = maxElement;
    			newDoubleArray[index] = maxElement;
				// MGlobal::executePythonCommand( MString( "print 'DEBUG:','" )+(int)index +"';");
			} 
			for (int w = 0; w < len; ++w) {
				mNewValues [w] = foo1[w];
			}
		}
		
		if(mNormalize)
		{
			double total = 0.0;
			for(unsigned int i = 0 ; i < mNewValues.length() ; ++i)
			{
				total += mNewValues[i];
			}
			if(total != 0.0)
			{
				for (unsigned int i = 0; i < mNewValues.length(); ++i)
				{
					mNewValues[i] /= total;
				}
			}
		}
	}

	// apply results	
	mSkinFn.setWeights(mTargetPath, mTargetComponents, mInfluenceIndices, mNewValues, false, &mOldValues);

	return MS::kSuccess;
}