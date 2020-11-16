#include "toolbox_maya/utils/maya_attributes.hpp"

#include <maya/MFnDependencyNode.h>
#include <maya/MDagModifier.h>
#include <toolbox_maya/utils/maya_error.hpp>

// -----------------------------------------------------------------------------

MPlug get_plug(const MObject& node, const MString& attribute)
{
    MStatus status;
    MFnDependencyNode dg_fn ( node );
    MPlug plug = dg_fn.findPlug ( attribute, true, &status );
    mayaCheck(status);
    return plug;
}

// -----------------------------------------------------------------------------

MPlug get_plug(const MObject& node, const MObject& attribute)
{
    MStatus status;
    MFnDependencyNode dg_fn ( node );
    MPlug plug = dg_fn.findPlug ( attribute, true, &status );
    mayaCheck(status);
    return plug;
}

// -----------------------------------------------------------------------------

bool is_connected(const MPlug& plug)
{
    MStatus status;
    bool state = plug.isConnected(&status);
    mayaCheck(status);
    return state;
}


// -----------------------------------------------------------------------------

void connect(const MPlug& source_plug, const MPlug& dest_plug)
{
    MDGModifier dg_modifier;
    mayaCheck( dg_modifier.connect(source_plug, dest_plug) );
    mayaCheck( dg_modifier.doIt() ); // Will actually perform the connections.
}

// -----------------------------------------------------------------------------

void connect(const MObject& source_obj, const MString& src_plug_name,
             const MObject& dest_obj  , const MString& dest_plug_name)
{
    MPlug src = get_plug(source_obj, src_plug_name);
    MPlug dst = get_plug(dest_obj, dest_plug_name);
    connect(src, dst);
}

// -----------------------------------------------------------------------------

void connect(const MObject& source_obj, const MObject& src_attribute,
             const MObject& dest_obj  , const MString& dest_plug_name)
{
    MPlug src = get_plug(source_obj, src_attribute);
    MPlug dst = get_plug(dest_obj, dest_plug_name);
    connect(src, dst);
}

// -----------------------------------------------------------------------------

void connect(const MObject& source_obj, const MString& src_plug_name,
             const MObject& dest_obj  , const MObject& dest_attribute)
{
    MPlug src = get_plug(source_obj, src_plug_name);
    MPlug dst = get_plug(dest_obj, dest_attribute);
    connect(src, dst);
}

// -----------------------------------------------------------------------------

void connect(const MObject& source_obj, const MObject& src_plug_name,
             const MObject& dest_obj  , const MObject& dest_attribute)
{
    MPlug src = get_plug(source_obj, src_plug_name);
    MPlug dst = get_plug(dest_obj, dest_attribute);
    connect(src, dst);
}

// -----------------------------------------------------------------------------

void disconnect(const MPlug& source_plug, const MPlug& dest_plug)
{
    MDGModifier dg_modifier;
    mayaCheck( dg_modifier.disconnect(source_plug, dest_plug) );
    mayaCheck( dg_modifier.doIt() ); // Will actually perform the disconnections.
}

// -----------------------------------------------------------------------------

void disconnect(const MObject& source_obj, const MString& src_plug_name,
                const MObject& dest_obj  , const MString& dest_plug_name)
{
    MPlug src = get_plug(source_obj, src_plug_name);
    MPlug dst = get_plug(dest_obj, dest_plug_name);
    disconnect(src, dst);
}

// -----------------------------------------------------------------------------

void disconnect(const MObject& source_obj, const MObject& src_attribute,
                const MObject& dest_obj  , const MString& dest_plug_name)
{
    MPlug src = get_plug(source_obj, src_attribute);
    MPlug dst = get_plug(dest_obj, dest_plug_name);
    disconnect(src, dst);
}

// -----------------------------------------------------------------------------

void disconnect(const MObject& source_obj, const MString& src_plug_name,
                const MObject& dest_obj  , const MObject& dest_attribute)
{
    MPlug src = get_plug(source_obj, src_plug_name);
    MPlug dst = get_plug(dest_obj, dest_attribute);
    disconnect(src, dst);
}

// -----------------------------------------------------------------------------

void disconnect(const MObject& source_obj, const MObject& src_plug_name,
                const MObject& dest_obj  , const MObject& dest_attribute)
{
    MPlug src = get_plug(source_obj, src_plug_name);
    MPlug dst = get_plug(dest_obj, dest_attribute);
    disconnect(src, dst);
}
