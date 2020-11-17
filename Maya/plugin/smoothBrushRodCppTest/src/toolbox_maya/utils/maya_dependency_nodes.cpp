#include "toolbox_maya/utils/maya_dependency_nodes.hpp"

#include <maya/MDGModifier.h>
#include <maya/MSelectionList.h>
#include "toolbox_maya/utils/maya_dag_nodes.hpp"

// =============================================================================
namespace tbx_maya {
// =============================================================================

void delete_node(MObject node)
{
    MDGModifier dg;
    //mayaAssertMsg(!has_connections(node), "Disconnect any out/in connection to this node before deletion.");

    // It seems maya crashes when deleting some nodes (in my case node color)
    // while selecting, so for safety I unselect before deletion:
    if(false){
        MString cmd = MString(("select -deselect ")) + get_name(node) + MString((";"));
        mayaCheck( MGlobal::executeCommand(cmd, g_debug_mode) );
    }else
        mayaCheck( MGlobal::unselect(node) );

    mayaCheck( dg.deleteNode(node) );
    mayaCheck( dg.doIt() );

//    MString cmd = MString(("delete ")) + get_name(node) + MString((";"));
//    mayaCheck( MGlobal::executeCommand(cmd, g_debug_mode) );

#if 0
    // How about? ->
    MGlobal::deleteNode( node );
#endif
}

// -----------------------------------------------------------------------------

bool node_exists(const MString& node_name)
{
    MSelectionList slist;
    return slist.add(node_name, true) == MStatus::kSuccess;
}

// -----------------------------------------------------------------------------

MString get_name(MObject obj)
{
    MStatus status;
    MFnDependencyNode dep(obj);
    MString name = dep.name(&status);
    mayaCheck(status);
    return name;
}

// -----------------------------------------------------------------------------

MString get_name(MDagPath path)
{
    MStatus status;
    MObject obj = path.node(&status);
    mayaCheck( status );
    return get_name( obj );
}

// -----------------------------------------------------------------------------

MTypeId get_type_id(MObject obj)
{
    MStatus status;
    MFnDependencyNode node_fn(obj, &status);
    mayaCheck(status);
    MTypeId id = node_fn.typeId(&status);
    mayaCheck(status);
    return id;
}

// -----------------------------------------------------------------------------

MString get_type_name(MObject obj)
{
    MStatus status;
    MFnDependencyNode node_fn(obj, &status);
    mayaCheck(status);
    MString name = node_fn.typeName(&status);
    mayaCheck(status);
    return name;
}


}// END tbx_maya Namespace =====================================================
