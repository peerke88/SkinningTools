#include "toolbox_maya/utils/maya_utils.hpp"


//// -----------

#include <maya/MGlobal.h>
#include <maya/MFnTransform.h>
#include <maya/MFnIkJoint.h>
#include <maya/MItSelectionList.h>
#include <maya/MSelectionList.h>
#include <maya/MDagPath.h>
#include <maya/MUserEventMessage.h>
#include <maya/MFnSkinCluster.h>
#include <maya/MDagPathArray.h>

//// -----------

#include "toolbox_maya/utils/maya_dag_nodes.hpp"
#include "toolbox_maya/utils/type_conversion.hpp"
#include "toolbox_maya/utils/maya_dependency_nodes.hpp"

//// ----------

#include <toolbox_stl/string.hpp>
#include <toolbox_stl/vector.hpp>

// =============================================================================
namespace tbx_maya {
// =============================================================================

MString get_plugin_path(const MString& plugin_name)
{
    MString result;
    MString name = plugin_name;

    if( MGlobal::executeCommand(MString(("pluginInfo -query -path "))+name, result)  )
        return to_MString( tbx::get_dir_name( to_str(result) ) );
    else
        return "./";
}

// -----------------------------------------------------------------------------

std::vector<MDagPath> to_stdvector(const MSelectionList& list)
{
    MStatus status;
    unsigned len = list.length(&status);
    mayaCheck(status);
    std::vector<MDagPath> vec;
    vec.reserve(len);
    for(unsigned i = 0; i < len; ++i)
    {
        MObject node;
        mayaCheck( list.getDependNode(i, node ) );
        if( node.hasFn(MFn::kDagNode))
        {
            MDagPath path;
            mayaCheck( list.getDagPath(i, path ) );
            vec.push_back( path );
        }
    }
    return vec;
}

// -----------------------------------------------------------------------------

MObject has(const MSelectionList& list, MFn::Type type)
{
    MStatus status;
    unsigned len = list.length(&status);
    mayaCheck(status);
    MObject object;
    for(unsigned i = 0; i < len; ++i){
        mayaCheck( list.getDependNode(i, object ) );
        if( object.apiType() == type)
            return object;
    }
    return MObject();
}

// -----------------------------------------------------------------------------

MString to_str(const MSelectionList& list)
{
    MString str;
    for(unsigned i = 0; i < list.length(); ++i) {
        MObject obj;
        mayaCheck( list.getDependNode(i, obj) );
        str += get_name(obj) + "\n";
    }
    return str;
}

// -----------------------------------------------------------------------------

MString to_str(const MArgList& args)
{
    MStatus status;
    MString str = "";
    unsigned len = args.length(&status);
    mayaCheck(status);

    for(unsigned i = 0; i < len; ++i)
    {
        MString val = args.asString(i, &status);

        if( status == MS::kSuccess )
            str += " " + val;
    }
    return str;
}

// -----------------------------------------------------------------------------

MStringArray split(const MString& str, char c)
{
    MStringArray array;
    mayaCheck(str.split(c, array));
    return array;
}

// -----------------------------------------------------------------------------

std::vector<MDagPath> get_active_selection(bool ordered_selection)
{
    MSelectionList list;
    mayaCheck( MGlobal::getActiveSelectionList(list, ordered_selection) );
    return to_stdvector(list);
}

// -----------------------------------------------------------------------------

std::vector<MDagPath> get_selected(const std::vector<MFn::Type>& type_list)
{
    std::vector<MDagPath> results;
    MStatus status;
    for( const MDagPath& path : get_active_selection() )
    {
        MFn::Type type = path.apiType(&status);
        mayaCheck(status);
        if( tbx::exists(type_list, type) )
            results.push_back( path );
    }
    return results;
}

// -----------------------------------------------------------------------------

std::vector<MDagPath> get_selected(MFn::Type object_type)
{
    return get_selected(std::vector<MFn::Type>({object_type}));
}

// -----------------------------------------------------------------------------

void post_user_event(const MString& string)
{
    mayaCheck( MUserEventMessage::postUserEvent(MString(string)) );
}

// -----------------------------------------------------------------------------

std::vector<MObject> get_influence_objects(MObject skin_cluster)
{
    MStatus status;
    std::vector<MObject> obj_list;
    MFnSkinCluster skin_cluster_fn(skin_cluster, &status);
    mayaCheck(status);

    MDagPathArray influence_objs;
    skin_cluster_fn.influenceObjects(influence_objs, &status);
    mayaCheck(status);

    for(int i = 0; i < (int)influence_objs.length(); ++i)
    {
        const MDagPath& path = influence_objs[i];
        mayaCheck(status);
        MObject node = path.node(&status);
        mayaCheck(status);
        obj_list.push_back(node);
    }
    return  obj_list;
}

}// END tbx_maya Namespace =====================================================
