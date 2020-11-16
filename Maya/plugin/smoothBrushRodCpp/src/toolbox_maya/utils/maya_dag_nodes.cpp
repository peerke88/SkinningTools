#include "toolbox_maya/utils/maya_dag_nodes.hpp"

#include <maya/MSelectionList.h>
#include <maya/MFnDagNode.h>
#include <maya/MFnMesh.h>
#include <maya/MPlug.h>
#include <maya/MGlobal.h>

#include "toolbox_maya/utils/maya_error.hpp"
#include "toolbox_maya/utils/type_conversion.hpp"

// =============================================================================
namespace tbx_maya {
// =============================================================================


MMatrix world_mmatrix(const MDagPath& path)
{
    MStatus status = MStatus::kSuccess;
    MMatrix world_mat = path.inclusiveMatrix(&status);
    mayaCheck(status);
    return world_mat;
}

tbx::Transfo world_transfo(const MDagPath& path){
    return to_transfo(world_mmatrix(path));
}

tbx::Transfo local_transfo(const MDagPath& path){
    return to_transfo( local_mmatrix(path) );
}

// -----------------------------------------------------------------------------

MMatrix world_mmatrix(const MObject dag_node)
{
    MStatus status;
    MDagPath node_path;
    mayaCheck(MDagPath::getAPathTo(dag_node, node_path));
    mayaCheck(status);

    MMatrix world_matrix = node_path.inclusiveMatrix(&status);
    mayaCheck(status);
    return world_matrix;
}

// -----------------------------------------------------------------------------

MMatrix local_mmatrix(const MDagPath& path)
{
    MStatus status = MStatus::kSuccess;
    MMatrix local_mat = path.exclusiveMatrix(&status);
    mayaCheck(status);
    return local_mat;
}

// -----------------------------------------------------------------------------


MObject get_MObject(const MString& node_name)
{
    MSelectionList slist;
    MStatus status = slist.add(node_name);
    mayaAssertMsg(status, "The node: \""+node_name+"\" could not be found.");

    int matches = slist.length(&status);
    mayaCheck(status);
    mayaAssertMsg(matches == 1, "Multiple nodes found for the same name: "+node_name);

    MObject obj;
    slist.getDependNode(0, obj);
    return obj;
}

// -----------------------------------------------------------------------------

MDagPath get_MDagPath(const MString& node_name)
//{ return get_MDagPath( get_MObject( path ) ); }
{
    MSelectionList slist;
    MStatus status = slist.add(node_name);
    mayaAssertMsg(status, "The node: \""+node_name+"\" could not be found.");

    int matches = slist.length(&status);
    mayaCheck(status);
    mayaAssertMsg(matches == 1, "Multiple nodes found for the same name: "+node_name);

    MDagPath path;
    slist.getDagPath(0, path);
    return path;
}

// -----------------------------------------------------------------------------

std::vector<MObject> get_MObjects(const MStringArray& array) {
    std::vector<MObject> vec(array.length());
    for(unsigned i = 0; i < vec.size(); ++i)
        vec[i] = get_MObject( array[i] );
    return vec;
}

// -----------------------------------------------------------------------------


MObject copy(MObject node)
{
    MStatus status;
    MFnDagNode dag_node(node, &status);
    mayaCheck(status);

    MObject copy;
    if( dag_node.hasObj( MFn::kMesh ) )
    {
        MFnMesh fn_mesh;
        copy = fn_mesh.copy( node, MObject::kNullObj, &status);
        mayaCheck(status);
        copy = get_shape( copy);
    }
    else
    {
        copy = dag_node.duplicate(false, false, &status);
        mayaCheck(status);
    }
    return copy;
}

// -----------------------------------------------------------------------------


MObject get_transform(MObject node)
{
    MStatus status;
    // Create an MFnDagNode for the node,
    // and use it to get an MDagPath.
    // (If there are multiple DAG paths to the node,
    // the one we get is undefined.)
    MFnDagNode dag_node(node, &status);
    mayaCheck(status);

    MDagPath dag_path;
    mayaCheck(dag_node.getPath(dag_path));

    // Find a shape node directly underneath the node.
    MObject tr = dag_path.transform(&status);
    return tr;
}

// -----------------------------------------------------------------------------

bool has_shape(MObject node)
{
    MStatus status;
    MFnDagNode dag_node(node, &status);
    if(status == MS::kFailure)
        return false;

    MDagPath dag_path;
    mayaCheck(dag_node.getPath(dag_path));

    unsigned nb_shapes = 0;
    status = dag_path.numberOfShapesDirectlyBelow(nb_shapes);
    return (status == MS::kSuccess) && (nb_shapes > 0);
}

// -----------------------------------------------------------------------------

bool has_shape(const MDagPath& path) {
    MDagPath tmp = path;
    unsigned nb_shapes = 0;
    MStatus status = tmp.numberOfShapesDirectlyBelow(nb_shapes);
    return (status == MS::kSuccess) && (nb_shapes > 0);
}

// -----------------------------------------------------------------------------

MDagPath get_shape(const MDagPath& path)
{
    mayaAssert( get_nb_shapes(path) );
    MDagPath dag_path = path;
    mayaCheck(dag_path.extendToShape());
    return dag_path;
}

// -----------------------------------------------------------------------------

MObject get_shape(MObject node)
{    
    MStatus status;

    MDagPath dag_path = get_MDagPath(node);
    // Find a shape node directly underneath the node.
    mayaCheck(dag_path.extendToShape());

    return dag_path.node();
}

// Alternate implementation:
/*
MDagPath get_shape(const MFnDagNode& inDagNode)
{
    if (inDagNode.childCount() > 0)
    {
        MObject aChild = inDagNode.child(0);
        MFnDagNode child(aChild);
        if (aChild.hasFn(MFn::kShape)){
            MDagPath path;
            child.getPath(path);
            return path;
        }
    }

    MDagPath dummy;
    return dummy;
}*/

// -----------------------------------------------------------------------------

unsigned get_nb_shapes(const MDagPath& dag_path)
{
    unsigned nb_shapes = 0;
    mayaCheck( dag_path.numberOfShapesDirectlyBelow(nb_shapes) );
    return  nb_shapes;
}

// -----------------------------------------------------------------------------

unsigned get_nb_shapes(const MObject& node)
{
    MDagPath path = get_MDagPath(node);
    unsigned nb_shapes = 0;
    mayaCheck( path.numberOfShapesDirectlyBelow(nb_shapes) );
    return  nb_shapes;
}

// -----------------------------------------------------------------------------

std::vector<MDagPath> get_all_shapes(const MDagPath& path)
{
    MDagPath dag_path = path;

    std::vector<MDagPath> result;
    for(unsigned i = 0; i < get_nb_shapes(path); ++i){
        mayaCheck(dag_path.extendToShapeDirectlyBelow(i));
        MDagPath p = dag_path;
        result.push_back( p );
    }
    return result;
}

// -----------------------------------------------------------------------------

std::vector<MObject> get_all_shapes(MObject node)
{
    MStatus status;
    MDagPath dag_path = get_MDagPath(node);
    std::vector<MObject> result;
    for(unsigned i = 0; i < get_nb_shapes(dag_path); ++i){
        mayaCheck(dag_path.extendToShapeDirectlyBelow(i));
        result.push_back( dag_path.node() );
    }

    return result;
}

// -----------------------------------------------------------------------------

MDagPath get_MDagPath(const MObject& obj)
{
    MStatus status;
    mayaAssertMsg(obj.hasFn(MFn::kDagNode), MString("This MObject is not a valid dag node, current type: ")+obj.apiTypeStr());
    MFnDagNode dag_node(obj, &status);
    mayaCheck(status);
    MDagPath dag_path;
    mayaCheck( dag_node.getPath( dag_path ) );
    return dag_path;
}

// -----------------------------------------------------------------------------

MString get_dag_long_name(const MObject& obj)
{
    MStatus status;
    MString str = get_MDagPath(obj).fullPathName(&status);
    mayaCheck(status);
    return str;
}

// -----------------------------------------------------------------------------

MString get_dag_long_name(const MString& name)
{
    MStatus status;
    MString str = get_MDagPath(name).fullPathName(&status);
    mayaCheck(status);
    return str;
}

// -----------------------------------------------------------------------------

MString get_dag_long_name(const MDagPath& dag_path)
{
    MStatus status;
    MString str = dag_path.fullPathName(&status);
    mayaCheck(status);
    return str;
}
// -----------------------------------------------------------------------------

MString get_short_name(const MObject& obj)
{
    MStatus status;
    MString str = get_MDagPath(obj).partialPathName(&status);
    mayaCheck(status);
    return str;
}

// -----------------------------------------------------------------------------

MString get_short_name(const MString& name)
{
    MStatus status;
    MString str = get_MDagPath(name).partialPathName(&status);
    mayaCheck(status);
    return str;
}

// -----------------------------------------------------------------------------

MString get_short_name(const MDagPath& dag_path)
{
    MStatus status;
    MString str = dag_path.partialPathName(&status);
    mayaCheck(status);
    return str;
}

// -----------------------------------------------------------------------------

void lock_transforms(MObject node)
{
    MStatus status = MS::kSuccess;

    MFnDependencyNode dep_node(node, &status);
    mayaCheck(status);
    for(const char *attr: {("translate"), ("rotate"), ("scale")})
    {
        MPlug plug = dep_node.findPlug(attr, true, &status);
        mayaCheck(status);

        status = plug.setLocked(true);
        mayaCheck(status);
    }
}

// -----------------------------------------------------------------------------

void freeze_transforms(MObject node)
{
    MString mesh_name = get_dag_long_name(get_transform(node));
    mayaCheck( MGlobal::executeCommand( "makeIdentity -apply true -translate 1 -rotate 1 -scale 1 -normal 0 -preserveNormals 1 \""+mesh_name+"\";", true) );
}

// -----------------------------------------------------------------------------

void set_parent(MObject parent, MObject child)
{
    MStatus status = MS::kSuccess;
    MFnDagNode dag_node(parent, &status);
    mayaCheck(status);
    mayaCheck( dag_node.addChild(child, 0) );
}

// -----------------------------------------------------------------------------

void set_parent(MDagPath parent, MObject child)
{
    MStatus status = MS::kSuccess;
    MFnDagNode dag_node(parent, &status);
    mayaCheck(status);
    mayaCheck( dag_node.addChild(child, 0) );
}

// -----------------------------------------------------------------------------

tbx::Bbox3 get_bbox3(MObject dag_obj){
    return to_bbox3(get_MBoundingBox(dag_obj));
}

// -----

MBoundingBox get_MBoundingBox(MObject dag_obj)
{
    MStatus status = MS::kSuccess;
    MFnDagNode dag_node(dag_obj, &status);
    mayaCheck(status);
    MBoundingBox mbbox = dag_node.boundingBox(&status);
    mayaCheck(status);
    return mbbox;
}

// -----------------------------------------------------------------------------


MObject get_MObject(const MDagPath& dag_path)
{
    MStatus status = MS::kSuccess;
    MObject node = dag_path.node( &status );
    mayaCheck( status );
    return node;
}


bool is_valid(const MDagPath& path) {
    MStatus status;
    bool state = path.isValid(&status);
    mayaCheck(status);
    return state;
}

// -----------------------------------------------------------------------------

std::vector<MDagPath> get_parents(const MDagPath& node)
{
    MStatus status;
    MFnDagNode dag_node(node, &status);
    mayaCheck( status );
    unsigned nb_parents = dag_node.parentCount( &status );
    std::vector<MDagPath> parents( nb_parents );
    for(unsigned i = 0; i < nb_parents; ++i)
    {
        MObject parent = dag_node.parent(i, &status);
        mayaCheck( status );
        parents[i] = get_MDagPath(parent);
    }

    return parents;
}

// -----------------------------------------------------------------------------

MDagPath get_the_parent(const MDagPath& dag_node)
{
    for(const MDagPath& path : get_parents(dag_node))
        if(is_valid(path))
            return path;

    return MDagPath();
}


// -----------------------------------------------------------------------------

std::vector<MDagPath> get_children(const MDagPath& dag_node)
{
    MStatus status;
    unsigned nb_children = dag_node.childCount(&status);
    mayaCheck(status);
    std::vector<MDagPath> children(nb_children);
    for(unsigned i = 0; i < nb_children; ++i)
    {
        MObject obj = dag_node.child(i, &status);
        mayaCheck(status);
        children[i] = get_MDagPath(obj);
    }
    return  children;
}

}// END tbx_maya Namespace =====================================================
