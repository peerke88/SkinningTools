#ifndef TOOLBOX_MAYA_FIND_NODE_HPP
#define TOOLBOX_MAYA_FIND_NODE_HPP

#include <maya/MFnDagNode.h>
#include <maya/MSelectionList.h>
#include <vector>

// =============================================================================
namespace tbx_maya {
// =============================================================================

/**
  @code
                     down stream
            +-------------------------->
     -----------                   ----------------
    |source node| --------------- |destination node|
     -----------                   ----------------
           <---------------------------+
                       up stream
  @endcode
*/
enum class Stream {
    eDOWN, ///< from source nodes (inputs) to destination nodes (outputs)
    eUP    ///< from destination nodes (outputs) to source nodes (inputs)
};

// -----------------------------------------------------------------------------

/// @brief find the dag node representing the bind pose of the skin cluster.
/// Note that several bind pose may be defined, we return the first occurence.
bool find_dag_bind_pose_skin_cluster(const MObject& skin_cluster, MObject& dag_pose );

/// Find skin cluster from its output mesh shape
/// @param[in] mesh_shape : dfm output mesh shape from which we seek the skin cluster
/// @param[out] skin_cluster : object convertible to MFnSkinCluster
/// @return wether or not a skin cluster was found.
bool find_skin_cluster_from_output_mesh(const MObject& mesh_shape, MObject& skin_cluster);

/// Find skin cluster from its input mesh shape
/// @param[in] mesh_shape : dfm input mesh shape from which we seek the skin cluster
/// @param[out] skin_cluster : object convertible to MFnSkinCluster
/// @return wether or not a skin cluster was found.
bool find_skin_cluster_from_input_mesh(const MObject& mesh_shape, MObject& skin_cluster);

/// Find skin cluster from a joint
/// @param[in] joint : input joint from which we seek the skin cluster
/// @param[out] skin_cluster : object convertible to MFnSkinCluster
/// @return wether or not a skin cluster was found.
bool find_skin_cluster_from_joint(const MObject& joint,
                                  std::vector<MObject>& skin_clusters);

/// Find output mesh shape associated to a deformer node
/// @param[in] deformer : input deformer
/// @param[out] mesh_shape : the first mesh we encounter tracing back the
/// deformer output mesh.
/// @return wether or not a mesh shape was found.
bool find_dfm_output_deformed_mesh(const MObject& deformer, MObject& mesh_shape);

/// Find input mesh shape associated to a deformer node
/// (whith a skincluster most likely the mesh in rest pose)
/// @param[in] deformer : input deformer
/// @param[out] mesh_shape : the first mesh we encounter tracing back the
/// deformer input mesh.
/// @return wether or not a mesh shape was found.
bool find_dfm_input_deformed_mesh(const MObject& deformer, MObject& mesh_shape);

/// @return plug of: skin_cluster.outputGeometry[0]
MPlug get_skincluster_out_mesh_plug(MObject skin_cluster);

/// @return plug of: MPxDeformerNode.input[multi_index].inputGeom
MPlug get_dfm_input_mesh_plug(MObject deformer, int multi_index);

/// @brief find a node of a certain type starting from a specified plug
/// @param source_plug: the plug we start looking from
/// @param type: stream type (up-stream or down-stream the graph of nodes)
/// @param[out] results : *first* found node if any or null
/// @return true when a node of type "node_type" is found
bool find_node_of_type(MPlug source_plug, Stream direction, MFn::Type node_type, MObject& result );

/// @brief find a node of a certain type starting from a specified plug
/// @param source_plug: the plug we start looking from
/// @param type: stream type (up-stream or down-stream the graph of nodes)
/// @param[out] results : *first* found node if any or null
/// @return true when a node of type "node_type" is found
bool find_node_of_type(MPlug source_plug, Stream direction, const MString& type, MObject& result );

// -----------------------------------------------------------------------------
/// @name Look up dependency graph
// -----------------------------------------------------------------------------

/// @return The list of dag nodes whose type match "filter"
MSelectionList find_dag_nodes_of_type(MFn::Type filter);

std::vector<MObject> find_nodes_of_type(MFn::Type filter);

std::vector<MObject> find_nodes_of_type_id(MTypeId id, MFn::Type filter = MFn::kInvalid);


}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_FIND_NODE_HPP
