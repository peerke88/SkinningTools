#ifndef TBX_EDGE_BOUNDARY_INFOS_HPP
#define TBX_EDGE_BOUNDARY_INFOS_HPP

#include <vector>
#include "toolbox_mesh/mesh_type.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

struct Edge_boundary_infos {

    void clear(){
        _on_side_edges.clear();
        _is_side_edge.clear();
    }

    /// List of edges on the boundary of the mesh
    std::vector<Edge_idx> _on_side_edges;

    /// Does the ith edge belongs to a mesh boundary
    std::vector<bool> _is_side_edge;

    void compute(const std::vector<Edge>& edge_list,
                 const std::vector<bool>& is_vert_on_side);

};

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_EDGE_BOUNDARY_INFOS_HPP
