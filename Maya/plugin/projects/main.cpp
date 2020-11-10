#include <vector>

#undef NT_PLUGIN
#define MNoVersionString
#include <maya/MFnPlugin.h>
#undef MNoVersionString
#define NT_PLUGIN

#ifdef WIN32
#define _WINSOCKAPI_
#include <windows.h>
#endif
#ifndef MACOS
#include <GL/gl.h>
#else
#include <OpenGL/gl.h>
#endif

#include <maya/MObject.h>
#include "utils.hpp"
#include "skinweights.h"
#include "averagevtxweight.h"

// Node ID Block is: 0x00131770 - 0x0013177f
int __id = 0x00131770;
std::vector<int> ids;
int id()
{
	ids.push_back(__id);
	return __id++;
}

std::vector<MString> cmds;

#define REGISTERCOMMAND(COMMAND) cmds.push_back(#COMMAND); stat = plugin.registerCommand(#COMMAND, COMMAND::sCreator, COMMAND::sNewSyntax); THROWSTAT

MStatus initializePlugin(MObject pluginObj)
{
	MFnPlugin plugin(pluginObj, "Trevor van Hoof & Perry Leijten", "1.0", "any");
	MStatus stat;
	
	REGISTERCOMMAND(AverageVtxWeight);
	REGISTERCOMMAND(SkinWeights);
	
	return stat;
}


MStatus uninitializePlugin(MObject pluginObj)
{
	MFnPlugin plugin(pluginObj);
	MStatus stat;

	size_t i = ids.size();
	while (i > 0)
	{
		--i;
		stat = plugin.deregisterNode(ids[i]);
		THROWSTAT;
	}

	i = cmds.size();
	while (i > 0)
	{
		--i;
		stat = plugin.deregisterCommand(cmds[i]);
		THROWSTAT;
	}

	return stat;
}
