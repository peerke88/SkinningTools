#pragma once
#include <maya/MString.h>
#include <maya/MDagPath.h>
#include <toolbox_maya/utils/forward_declaration.hpp>
#include <toolbox_maths/skel/bone_type.hpp>
#include "data/brush.hpp"
#include <vector>
#include <map>

// Forward declaration ---------------------------------------------------------
TBX_MAYA_FORWARD_DECLARATION(class MObject);
TBX_MAYA_FORWARD_DECLARATION(class MString);
namespace tbx_maya {
    struct Maya_mesh;
    struct Maya_skeleton;
    class Sub_mesh;

}
namespace tbx_mesh {
    class First_ring_it;
}
namespace skin_brush {
    class Node_swe_cache;    
    class Rig;    
}
// END Forward declaration -----------------------------------------------------

// =============================================================================
namespace skin_brush {
// =============================================================================

void normalize(std::vector<std::map<int, float> >& weights,
               std::vector<std::map<int, float> >& buffer_weights,
               const tbx_maya::Sub_mesh& sub_mesh);

void normalize_sub(std::vector<std::map<int, float> >& weights,
                   std::vector<std::map<int, float> >& sub_buffer_weights,
                   const tbx_maya::Sub_mesh& sub_mesh);

void normalize_sub(std::vector<std::map<int, float> >& weights,
                   const std::vector<bool>& joint_scopes,
                   const tbx_maya::Sub_mesh& sub_mesh);

/// Increase selected area to included direct vertex neighbors
/// @warning unoptimized, likely too slow for a large selection set.
std::vector<int> grow_selection(const std::vector<int>& selection,
                                const tbx_mesh::First_ring_it& connectivity,
                                int level = 1);

///@return 'vertex_list' the currently selected vertices components
/// in maya if any
void get_maya_selection(std::vector<int>& vertex_list,
                        MObject skin_cluster);

///@return 'vertex_list' containing either the vertices' brush_mask
/// or the current maya selection
void build_selection(
        std::vector<int>& vertex_list,
        MObject skin_cluster,
        const std::vector<Brush>& brush_mask = {});

/// @brief attempts to find the cache (clean up uninitialized cache nodes
/// as well)
/// @param update: update the cache when found
/// @return null if no valid cache were found
Node_swe_cache* find_cache(MObject& skin_cluster, bool update = true);

MString get_joint_name(bone::Id id, const Node_swe_cache* cache);

///@return has_influence[joint_id] = wether this joint influence the mesh or not
//std::vector<bool> compute_has_influence(const tbx_maya::Maya_skeleton& skel);

}// END skin_brush Namespace ========================================
