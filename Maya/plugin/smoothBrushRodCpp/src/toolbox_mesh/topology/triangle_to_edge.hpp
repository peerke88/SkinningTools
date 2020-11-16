#ifndef TBX_TRIANGLE_TO_EDGE_HPP
#define TBX_TRIANGLE_TO_EDGE_HPP

#include <vector>
#include "toolbox_mesh/mesh_type.hpp"
#include "toolbox_mesh/mesh_geometry.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

struct Triangle_to_edge {

    void clear(){ _tri_edges.clear(); }

    /// List of triangles which are described using three edge indices
    /// corresponding to the "_edge_list"
    /// _tri_edges[tri_idx] = { 3 edge index of "_edge_list" }
    std::vector<Tri_edges> _tri_edges;

    void compute(const Mesh_geometry& mesh,
                 const std::vector<Edge>& edge_list,
                 const std::vector<std::vector<Tri_idx> >& tri_list_per_edge);

};

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_TRIANGLE_TO_EDGE_HPP
