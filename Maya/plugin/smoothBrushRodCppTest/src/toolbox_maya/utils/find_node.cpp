#include "toolbox_maya/utils/find_node.hpp"

#include "toolbox_maya/utils/maya_error.hpp"
#include "toolbox_maya/utils/maya_utils.hpp"
#include "toolbox_maya/utils/maya_attributes.hpp"
#include "toolbox_maya/utils/maya_dependency_nodes.hpp"
#include "toolbox_maya/utils/maya_dag_nodes.hpp"

#include <maya/MFnDagNode.h>
#include <maya/MItDependencyNodes.h>
#include <maya/MItDependencyGraph.h>

// =============================================================================
namespace tbx_maya {
// =============================================================================

bool find_dag_bind_pose_skin_cluster(const MObject& skin_cluster, MObject& dag_pose )
{
    MStatus status;
    MPlug in_bind_pose_plug = get_plug(skin_cluster, ("bindPose"));
    mayaCheck(status);
    if( is_connected(in_bind_pose_plug) )
    {
        // walk the tree upstream from this plug
        MItDependencyGraph dg_it(in_bind_pose_plug,
                                MFn::kInvalid,
                                MItDependencyGraph::kUpstream,
                                MItDependencyGraph::kDepthFirst,
                                MItDependencyGraph::kPlugLevel,
                                &status);

        mayaCheck(status);
        dg_it.disablePruningOnFilter();
        for ( ; ! dg_it.isDone(); dg_it.next() )
        {
            MObject curr_node = dg_it.currentItem(&status);
            mayaCheck(status);
            // go until we find a skinCluster
            if (curr_node.apiType() == MFn::kDagPose)
            {
                dag_pose = curr_node;
                return true;
            }
        }
    }

    dag_pose = MObject::kNullObj;
    return false;
}

// -----------------------------------------------------------------------------

bool find_skin_cluster_from_output_mesh(const MObject& mesh_shape, MObject& skin_cluster)
{
    MStatus status;
    MFnDependencyNode mesh(mesh_shape, &status);
    mayaCheck(status);

    // the deformed mesh comes into the visible mesh
    // through its "inmesh" plug
    MPlug in_mesh_plug = mesh.findPlug(("inMesh"), true, &status);
    mayaCheck(status);
    if( is_connected(in_mesh_plug) )
    {
        // walk the tree of stuff upstream from this plug
        MItDependencyGraph dg_it(in_mesh_plug,
                                MFn::kInvalid,
                                MItDependencyGraph::kUpstream,
                                MItDependencyGraph::kDepthFirst,
                                MItDependencyGraph::kPlugLevel,
                                &status);

        mayaCheck(status);
        dg_it.disablePruningOnFilter();
        for ( ; ! dg_it.isDone(); dg_it.next() )
        {
            MObject curr_node = dg_it.currentItem(&status);
            mayaCheck(status);
            // go until we find a skinCluster
            if (curr_node.apiType() == MFn::kSkinClusterFilter)
            {
                skin_cluster = curr_node;
                return true;
            }
        }
    }

    skin_cluster = MObject::kNullObj;
    return false;
}

// -----------------------------------------------------------------------------

bool find_skin_cluster_from_input_mesh(const MObject& mesh_shape, MObject& skin_cluster)
{
    MStatus status;
    MFnDependencyNode node_mesh(mesh_shape, &status);
    mayaCheck(status);

    MPlug out_mesh_plug = node_mesh.findPlug(("worldMesh"), true, &status);
    mayaCheck(status);
    MPlug mesh = out_mesh_plug[0];
    if( is_connected(mesh) )
    {
        // walk the tree of stuff upstream from this plug
        MItDependencyGraph dg_it(mesh,
                                MFn::kInvalid,
                                MItDependencyGraph::kDownstream,
                                MItDependencyGraph::kDepthFirst,
                                MItDependencyGraph::kPlugLevel,
                                &status);

        mayaCheck(status);
        dg_it.disablePruningOnFilter();
        for ( ; ! dg_it.isDone(); dg_it.next() )
        {
            MObject curr_node = dg_it.currentItem(&status);
            mayaCheck(status);
            // go until we find a skinCluster
            if (curr_node.apiType() == MFn::kSkinClusterFilter)
            {
                skin_cluster = curr_node;
                return true;
            }
        }
    }

    skin_cluster = MObject::kNullObj;
    return false;
}

// -----------------------------------------------------------------------------

bool find_skin_cluster_from_joint(const MObject& joint,
                                  std::vector<MObject>& skin_clusters)
{
    skin_clusters.clear();
    MStatus status;
    MFnDependencyNode joint_node(joint, &status);
    mayaCheck(status);

    MPlug array = joint_node.findPlug(("worldMatrix"), true, &status);
    mayaCheck(status);

    MPlug matrix_plug = array.elementByLogicalIndex(0, &status);
    mayaCheck(status);

    if( is_connected(matrix_plug) )
    {
        MItDependencyGraph dg_it(matrix_plug,
                                 MFn::kInvalid,
                                 MItDependencyGraph::kDownstream,
                                 MItDependencyGraph::kDepthFirst,
                                 MItDependencyGraph::kPlugLevel,
                                 &status);

        mayaCheck(status);
        dg_it.disablePruningOnFilter();
        for ( ; ! dg_it.isDone(); dg_it.next() )
        {
            MObject curr_node = dg_it.currentItem(&status);
            mayaCheck(status);
            // go until we find a skinCluster
            if (curr_node.apiType() == MFn::kSkinClusterFilter)
            {
                skin_clusters.push_back( curr_node );
            }
        }
    }

    return skin_clusters.size() > 0;
}

// -----------------------------------------------------------------------------

bool find_dfm_output_deformed_mesh(const MObject& deformer, MObject& mesh_shape)
{
    /*
     * It's possible that the following code is equivalent to the much simpler code:
     * deformer.getPathAtIndex(0, dag_path);
     * return get_MObject(dag_path);
     * (perhaps even more robust?)
    */
    MStatus status;
    MFnDependencyNode deformer_node(deformer, &status);
    mayaCheck(status);

    MPlug out_mesh_plug = deformer_node.findPlug(("outputGeometry"), true, &status);
    mayaCheck(status);
    MPlug plug_mesh = out_mesh_plug[0];
    if( is_connected(plug_mesh) )
    {
        // walk the tree of stuff downstream from this plug
        MItDependencyGraph dg_it(plug_mesh,
                                 MFn::kInvalid,
                                 MItDependencyGraph::kDownstream,
                                 MItDependencyGraph::kDepthFirst,
                                 MItDependencyGraph::kPlugLevel,
                                 &status);

        mayaCheck(status);
        dg_it.disablePruningOnFilter();
        for ( ; ! dg_it.isDone(); dg_it.next() )
        {
            MObject curr_node = dg_it.currentItem(&status);
            mayaCheck(status);
            if (curr_node.apiType() == MFn::kMesh)
            {
                mesh_shape = curr_node;
                return true;
            }
        }
    }
    mesh_shape = MObject::kNullObj;
    return false;
}

// -----------------------------------------------------------------------------

bool find_dfm_input_deformed_mesh(const MObject& deformer, MObject& mesh_shape)
{
    MStatus status;
    MFnDependencyNode deformer_node(deformer, &status);
    mayaCheck(status);

    MPlug in_mesh_plug = deformer_node.findPlug(("input"), true, &status);
    mayaCheck(status);
    MPlug plug = in_mesh_plug[0];
    MPlug plug_mesh = plug.child(0, &status); // <- input[0].inputGeometry
    mayaCheck(status);
    if( is_connected(plug_mesh) )
    {
        // walk the tree of stuff downstream from this plug
        MItDependencyGraph dg_it(plug_mesh,
                                 MFn::kInvalid,
                                 MItDependencyGraph::kUpstream,
                                 MItDependencyGraph::kDepthFirst,
                                 MItDependencyGraph::kPlugLevel,
                                 &status);

        mayaCheck(status);
        dg_it.disablePruningOnFilter();
        for ( ; ! dg_it.isDone(); dg_it.next() )
        {
            MObject curr_node = dg_it.currentItem(&status);
            mayaCheck(status);
            if (curr_node.apiType() == MFn::kMesh)
            {
                mesh_shape = curr_node;
                return true;
            }
        }
    }
    mesh_shape = MObject::kNullObj;
    return false;
}

// -----------------------------------------------------------------------------

MPlug get_skincluster_out_mesh_plug(MObject skin_cluster)
{
    MStatus status;
    MPlug out_mesh_plug = get_plug(skin_cluster, ("outputGeometry"));
    mayaCheck(status);
    MPlug plug_mesh = out_mesh_plug.elementByPhysicalIndex(0, &status);
    mayaCheck(status);

    return plug_mesh;
}

// -----------------------------------------------------------------------------

MPlug get_dfm_input_mesh_plug(MObject deformer, int multi_index)
{
    MStatus status;

    MPlug input_plug = get_plug(deformer, ("input"));
    MPlug element = input_plug.elementByLogicalIndex(multi_index, &status);
    mayaCheck(status);
    MPlug input_mesh_plug = element.child(0, &status); // <- input[0].inputGeometry
    mayaCheck(status);
    return input_mesh_plug;
}

// -----------------------------------------------------------------------------

bool find_node_of_type(MPlug source_plug,
                       Stream direction,
                       MFn::Type node_type,
                       MObject& result )
{
    MStatus status;
    if( is_connected(source_plug) )
    {        
        MItDependencyGraph dg_it(source_plug,
                                 MFn::kInvalid,
                                 direction == Stream::eUP ? MItDependencyGraph::kUpstream : MItDependencyGraph::kDownstream,
                                 MItDependencyGraph::kDepthFirst,
                                 MItDependencyGraph::kPlugLevel,
                                 &status);

        mayaCheck(status);
        dg_it.disablePruningOnFilter();
        for ( ; ! dg_it.isDone(); dg_it.next() )
        {
            MObject curr_node = dg_it.currentItem(&status);
            mayaCheck(status);
            if (curr_node.apiType() == node_type)
            {
                result = curr_node;
                return true;
            }
        }
    }
    result = MObject::kNullObj;
    return false;
}

// -----------------------------------------------------------------------------

bool find_node_of_type(MPlug source_plug,
                       Stream direction,
                       const MString& type,
                       MObject& result )
{
    MStatus status;
    if( is_connected(source_plug) )
    {
        MItDependencyGraph dg_it(source_plug,
                                 MFn::kInvalid,
                                 direction == Stream::eUP ? MItDependencyGraph::kUpstream : MItDependencyGraph::kDownstream,
                                 MItDependencyGraph::kDepthFirst,
                                 MItDependencyGraph::kPlugLevel,
                                 &status);

        mayaCheck(status);
        dg_it.disablePruningOnFilter();
        for ( ; ! dg_it.isDone(); dg_it.next() )
        {
            MObject curr_node = dg_it.currentItem(&status);
            mayaCheck(status);
            MString type_name = get_type_name(curr_node);
            if (type_name == type)
            {
                result = curr_node;
                return true;
            }
        }
    }
    result = MObject::kNullObj;
    return false;
}

// -----------------------------------------------------------------------------

MSelectionList find_dag_nodes_of_type(MFn::Type filter)
{
    MStatus status;
    MSelectionList list;
    MItDependencyNodes node_it(filter, &status);
    mayaCheck(status);
    while( !node_it.isDone(&status) )
    {
        mayaCheck(status);
        MObject j = node_it.thisNode(&status);
        if(j.hasFn(MFn::kDagNode))
        {
            // Note: we must use the dag path otherwise the object is not
            // recognized by the selection list as a DAG object but just
            // as a dependency node, which cause the node to be ignored by the
            // list...
            mayaCheck(list.add( get_MDagPath(j) ));
        }
        mayaCheck(status);
        mayaCheck(node_it.next());
    }
    return list;
}

// -----------------------------------------------------------------------------

std::vector<MObject> find_nodes_of_type(MFn::Type filter)
{
    std::vector<MObject> list;
    MStatus status;
    MItDependencyNodes node_it(filter, &status);
    mayaCheck(status);
    while( !node_it.isDone(&status) )
    {
        mayaCheck(status);
        MObject j = node_it.thisNode(&status);
        mayaCheck(status);
        list.push_back( j );
        mayaCheck(node_it.next());
    }
    return list;
}

// -----------------------------------------------------------------------------

std::vector<MObject> find_nodes_of_type_id(MTypeId id, MFn::Type filter)
{
    std::vector<MObject> list;
    MStatus status;
    MItDependencyNodes node_it(filter, &status);
    mayaCheck(status);
    while( !node_it.isDone(&status) )
    {
        mayaCheck(status);
        MObject j = node_it.thisNode(&status);
        mayaCheck(status);
        if( id == get_type_id(j) )
            list.push_back( j );
        mayaCheck(node_it.next());
    }
    return list;
}

}// END tbx_maya Namespace =====================================================

