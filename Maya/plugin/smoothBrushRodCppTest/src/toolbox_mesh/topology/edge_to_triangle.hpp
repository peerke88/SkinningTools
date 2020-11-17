#ifndef TBX_EDGE_TO_TRIANGLE_HPP
#define TBX_EDGE_TO_TRIANGLE_HPP

#include <vector>
#include "toolbox_mesh/mesh_type.hpp"
#include "toolbox_mesh/mesh_geometry.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

struct Edge_to_triangle {

    void clear(){
        _tri_list_per_edge.clear();
    }

    /// List of triangles per edge
    /// _tri_list_per_edge[edge_id] == list of tri id in '_tri'
    std::vector<std::vector<Tri_idx> > _tri_list_per_edge;


    void compute(const Mesh_geometry& mesh,
                 const std::vector<std::vector<Tri_idx> >& tri_list_per_vert,
                 const std::vector<Edge>& edge_list,
                 const std::vector<bool>& is_vert_on_side);
};

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_EDGE_TO_TRIANGLE_HPP
