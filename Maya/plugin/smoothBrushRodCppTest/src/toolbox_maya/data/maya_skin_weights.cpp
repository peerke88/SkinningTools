#include "toolbox_maya/data/maya_skin_weights.hpp"

#include "toolbox_maya/utils/maya_error.hpp"
#include "toolbox_maya/utils/sub_mesh.hpp"
#include "toolbox_maya/utils/maya_mfnmesh_utils.hpp"
#include "toolbox_maya/utils/maya_attributes.hpp"

// ----------------------------

#include <maya/MDagPathArray.h>
#include <maya/MObject.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MPlug.h>
#include <maya/MArrayDataBuilder.h>
#include <maya/MFnSkinCluster.h>
#include <maya/MDataBlock.h>
#include <maya/MDoubleArray.h>
#include <maya/MDagPath.h>
#include <maya/MItGeometry.h>
#include <maya/MFnSingleIndexedComponent.h>
#include <toolbox_stl/timer.hpp>
#include <maya/MItMeshVertex.h>

// =============================================================================
namespace tbx_maya {
// =============================================================================

// =============================================================================
namespace skin_weights {
// =============================================================================

void get_all_through_mfnskincluster(
        MObject skin_cluster_node,
        std::vector< std::map<tbx::bone::Id, float> >& weights)
{
    MStatus status = MStatus::kSuccess;
    MFnSkinCluster skin_cluster(skin_cluster_node, &status);
    mayaCheck(status);

    MDagPath mesh_dag_path;
    mayaCheck( skin_cluster.getPathAtIndex(0, mesh_dag_path) );

    MObject mesh = mesh_dag_path.node();
    MItMeshVertex geom_it(mesh, &status);
    mayaCheck(status);

    weights.clear();
    weights.resize( geom_it.count() );

    MDagPathArray influence_objs;
    skin_cluster.influenceObjects(influence_objs, &status);
    mayaCheck(status);


    for(int i = 0; !geom_it.isDone(); geom_it.next(), ++i )
    {        
        MObject component = geom_it.currentItem(&status);
        mayaCheck(status);

        MDoubleArray weights_per_joint;
        unsigned influence_count;
        status = skin_cluster.getWeights(mesh_dag_path, component, weights_per_joint, influence_count);
        mayaCheck(status);

        // Filter out weights without influence
        std::map<tbx::bone::Id, float> map;
        unsigned len = weights_per_joint.length();
        for(unsigned i = 0; i < len; ++i)
        {
            if( weights_per_joint[i] > 1e-6f ){
                unsigned j_id = skin_cluster.indexForInfluenceObject( influence_objs[i],  &status);
                mayaCheck(status);
                map[int(j_id)] = (float)weights_per_joint[i];
            }
        }

        weights[i] = map ;
    }

}

void get_subset_through_mfnskincluster(
        MObject skin_cluster_node,
        const std::vector<int>& vertex_list,
        std::vector< std::map<tbx::bone::Id, float> >& weights)
{
    MStatus status = MStatus::kSuccess;
    MFnSkinCluster skin_cluster(skin_cluster_node, &status);
    mayaCheck(status);

    MDagPath mesh_dag_path;
    mayaCheck( skin_cluster.getPathAtIndex(0, mesh_dag_path) );

    MObject mesh = mesh_dag_path.node();
    MItMeshVertex geom_it(mesh, &status);
    mayaCheck(status);


    MDagPathArray influence_objs;
    skin_cluster.influenceObjects(influence_objs, &status);
    mayaCheck(status);


    for(unsigned i = 0; i < vertex_list.size(); ++i )
    {
        int v_idx = vertex_list[i];
        int dummy;
        mayaCheck(geom_it.setIndex( v_idx, dummy ));
        MObject component = geom_it.currentItem(&status);
        mayaCheck(status);

        MDoubleArray weights_per_joint;
        unsigned influence_count;
        status = skin_cluster.getWeights(mesh_dag_path, component, weights_per_joint, influence_count);
        mayaCheck(status);

        // Filter out weights without influence
        std::map<tbx::bone::Id, float> map;
        unsigned len = weights_per_joint.length();
        for(unsigned j = 0; j < len; ++j)
        {
            if( weights_per_joint[j] > 1e-6f ){
                unsigned j_id = skin_cluster.indexForInfluenceObject( influence_objs[j],  &status);
                mayaCheck(status);
                map[int(j_id)] = (float)weights_per_joint[j];
            }
        }

        weights[i] = map ;
    }

}

// -----------------------------------------------------------------------------

void get_all_through_mplug(
        MObject skin_cluster_node,
        std::vector< std::map<tbx::bone::Id, float> >& weights)
{
    MStatus status;
    MFnDependencyNode deformer_node(skin_cluster_node, &status);
    mayaCheck(status);
    MPlug weight_list_plug = deformer_node.findPlug(("weightList"), true, &status);
    mayaCheck(status);
    unsigned nb_verts = weight_list_plug.numElements(&status);
    mayaCheck(status);
    weights.resize(nb_verts);
    for( unsigned i = 0; i < nb_verts; i++ )
    {
        weights[i].clear();
        // weightList[i]
        MPlug ith_weights_plug = weight_list_plug[i];

        // weightList[i].weight
        MPlug plug_weights = ith_weights_plug.child(0); // access first compound child

        int nb_weights = plug_weights.numElements();
        for( int j = 0; j < nb_weights; j++ ) {
            MPlug weight_plug = plug_weights[j];
            // weightList[i].weight[j]
            double w;
            mayaCheck( weight_plug.getValue(w) );
            unsigned j_id = weight_plug.logicalIndex(&status);
            mayaCheck(status);
            if( w > 1e-6f )
                weights[i][j_id] = (float)w;
        }
    }
}


void get_subset_through_mplug(
        MObject skin_cluster_node,
        const std::vector<int>& vertex_list,
        std::vector< std::map<tbx::bone::Id, float> >& weights)
{
    MStatus status;
    MFnDependencyNode deformer_node(skin_cluster_node, &status);
    mayaCheck(status);
    MPlug weight_list_plug = deformer_node.findPlug(("weightList"), true, &status);
    mayaCheck(status);
    unsigned nb_verts = weight_list_plug.numElements(&status);
    mayaCheck(status);
    weights.resize(nb_verts);
    for( unsigned l = 0; l < vertex_list.size(); l++ )
    {
        unsigned i = vertex_list[l];

        weights[i].clear();
        // weightList[i]
        MPlug ith_weights_plug = weight_list_plug[i];

        // weightList[i].weight
        MPlug plug_weights = ith_weights_plug.child(0); // access first compound child

        int nb_weights = plug_weights.numElements();
        for( int j = 0; j < nb_weights; j++ ) {
            MPlug weight_plug = plug_weights[j];
            // weightList[i].weight[j]
            double w;
            mayaCheck( weight_plug.getValue(w) );
            unsigned j_id = weight_plug.logicalIndex(&status);
            mayaCheck(status);
            if( w > 1e-6f )
                weights[i][j_id] = (float)w;
        }
    }

}

// -----------------------------------------------------------------------------

void set_all_through_mfncluster(
        MObject skin_cluster_node,
        const std::vector< std::map<tbx::bone::Id, float> >& weights)
{
    MStatus status = MStatus::kSuccess;
    MFnSkinCluster skin_cluster(skin_cluster_node, &status);
    mayaCheck(status);

    MDagPath mesh_dag_path;
    mayaCheck( skin_cluster.getPathAtIndex(0, mesh_dag_path) );
    MObject mesh_node = mesh_dag_path.node(&status);
    mayaCheck(status);
    int nb_verts = get_nb_vertices( mesh_node );

    MDagPathArray influence_objs;
    skin_cluster.influenceObjects(influence_objs, &status);
    mayaCheck(status);

    unsigned max_logical_index = 0;
    for(unsigned i = 0; i < influence_objs.length(); ++i)
    {
        unsigned j_id = skin_cluster.indexForInfluenceObject( influence_objs[i],  &status);
        mayaCheck(status);
        if(max_logical_index < j_id )
            max_logical_index = j_id;
    }

    std::vector<int> logical_to_sparse(max_logical_index+1);
    for(unsigned i = 0; i < influence_objs.length(); ++i)
    {
        unsigned j_id = skin_cluster.indexForInfluenceObject( influence_objs[i],  &status);
        mayaCheck(status);
        logical_to_sparse[j_id] = i;
    }

    // vertex indices
    MFnSingleIndexedComponent component_builder;
    MObject list_of_vertex_components = component_builder.create(MFn::kMeshVertComponent);
    for(int i = 0; i < nb_verts; ++i){
        component_builder.addElement(i);
    }

    MIntArray sparse_joint_indices;
    unsigned nb_joints = influence_objs.length();//joint_logical_idx.length();
    sparse_joint_indices.setLength( nb_joints );
    for(unsigned i = 0; i < nb_joints; i++)
        sparse_joint_indices[i] = i;

    // weight values
    MDoubleArray values(nb_verts * nb_joints, 0.0);

    for(int i = 0; i < nb_verts; ++i)
    {
        for(const std::pair<tbx::bone::Id, float>& value : weights[i])
        {
            int sparse_idx = logical_to_sparse[value.first];
            values[i * nb_joints + sparse_idx] = value.second;
        }
    }

    mayaCheck( skin_cluster.setWeights(mesh_dag_path,
                                       list_of_vertex_components,
                                       sparse_joint_indices,
                                       values,
                                       false,
                                       nullptr) );
}

// -----------------------------------------------------------------------------

void set_all_through_mplug(
        MObject skin_cluster_node,
        const std::vector< std::map<tbx::bone::Id, float> >& weights)
{
    MStatus status;
    MFnDependencyNode deformer_node(skin_cluster_node, &status);
    mayaCheck(status);
    MPlug weight_list_plug = deformer_node.findPlug(("weightList"), true, &status);
    mayaCheck(status);
    unsigned nb_verts = weight_list_plug.numElements(&status);
    mayaCheck(status);
    mayaAssert(nb_verts == weights.size());
    for( unsigned i = 0; i < nb_verts; i++ )
    {
        // weightList[i]
        MPlug ith_weights_plug = weight_list_plug[i];

        // weightList[i].weight
        MPlug plug_weights = ith_weights_plug.child(0); // access first compound child

        // First reset values to zero:
        int nb_weights = plug_weights.numElements();
        for( int j = 0; j < nb_weights; j++ ) {
            MPlug weight_plug = plug_weights[j];
            // weightList[i].weight[j]
            mayaCheck( weight_plug.setDouble( 0.0f ) );
        }

        for(const std::pair<tbx::bone::Id, float>& value : weights[i]) {
            MPlug weight_plug = plug_weights.elementByLogicalIndex( value.first );
            mayaCheck(status);

            // weightList[i].weight[value.second]
            mayaCheck( weight_plug.setDouble( value.second ) );
        }
    }
}

// -----------------------------------------------------------------------------

void set_subset_through_mplug(
        MObject skin_cluster_node,
        const std::vector<int>& vertex_list,
        const std::vector< std::map<tbx::bone::Id, float> >& weights)
{

    MStatus status;
    MFnDependencyNode deformer_node(skin_cluster_node, &status);
    mayaCheck(status);
    MPlug weight_list_plug = deformer_node.findPlug(("weightList"), true, &status);
    mayaCheck(status);
    //unsigned nb_verts = weight_list_plug.numElements(&status);
    unsigned nb_verts = weight_list_plug.evaluateNumElements(&status);
    mayaCheck(status);
    mayaAssert(nb_verts == weights.size());
    for( unsigned l = 0; l < vertex_list.size(); l++ )
    {
        unsigned index_vert = vertex_list[l];
        // weightList[i]
        //MPlug ith_weights_plug = weight_list_plug.elementByPhysicalIndex(index_vert, &status);
        MPlug ith_weights_plug = weight_list_plug.elementByLogicalIndex(index_vert, &status);
        mayaCheck(status);

        // weightList[i].weight
        MPlug plug_weights = ith_weights_plug.child(0, &status); // access first compound child
        mayaCheck(status);


        // First reset values to zero:
        int nb_weights = plug_weights.numElements();
        for( int j = 0; j < nb_weights; j++ ) {
            MPlug weight_plug = plug_weights[j];
            // weightList[i].weight[j]
            mayaCheck( weight_plug.setDouble( 0.0 ) );
        }

        for(const std::pair<tbx::bone::Id, float>& value : weights[index_vert]) {
            MPlug weight_plug = plug_weights.elementByLogicalIndex( value.first );
            mayaCheck(status);

            // weightList[i].weight[value.second]
            mayaCheck( weight_plug.setDouble( value.second ) );
        }
    }
}

}// END skin_weights Namespace =================================================

}// END tbx_maya Namespace =====================================================
