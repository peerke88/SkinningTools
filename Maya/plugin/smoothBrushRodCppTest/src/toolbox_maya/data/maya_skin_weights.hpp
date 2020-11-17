#pragma once

#include <vector>
#include <map>

#include <toolbox_maths/skel/bone.hpp>

// Maya Forward declaration ----------------------------------------------------
namespace tbx_maya {
    class Sub_mesh;
}
#include "toolbox_maya/utils/forward_declaration.hpp"
TBX_MAYA_FORWARD_DECLARATION(class MDataBlock);
TBX_MAYA_FORWARD_DECLARATION(class MObject);
// END Maya Forward declaration ------------------------------------------------

// =============================================================================
namespace tbx_maya {
// =============================================================================

// =============================================================================
namespace skin_weights {
// =============================================================================

void get_all_through_mfnskincluster(
        MObject skin_cluster_node,
        std::vector< std::map<tbx::bone::Id, float> >& weights);

void get_subset_through_mfnskincluster(
        MObject skin_cluster_node,
        const std::vector<int>& vertex_list,
        std::vector< std::map<tbx::bone::Id, float> >& weights);

// -----------------------------------------------------------------------------

void set_all_through_mfncluster(
        MObject skin_cluster_node,
        const std::vector< std::map<tbx::bone::Id, float> >& weights);

void set_subset_through_mfncluster(
        MObject skin_cluster_node,
        const std::vector<int>& vertex_list,
        const std::vector< std::map<tbx::bone::Id, float> >& weights);

void get_all_through_mplug(
        MObject skin_cluster_node,
        std::vector< std::map<tbx::bone::Id, float> >& weights);

void get_subset_through_mplug(
        MObject skin_cluster_node,
        const std::vector<int>& vertex_list,
        std::vector< std::map<tbx::bone::Id, float> >& weights);
// -----------------------------------------------------------------------------

void set_all_through_mplug(
        MObject skin_cluster_node,
        const std::vector< std::map<tbx::bone::Id, float> >& weights);

// -----------------------------------------------------------------------------

void set_subset_through_mplug(
        MObject skin_cluster_node,
        const std::vector<int>& vertex_list,
        const std::vector< std::map<tbx::bone::Id, float> >& weights);

}// END skin_weights Namespace =================================================

}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"
