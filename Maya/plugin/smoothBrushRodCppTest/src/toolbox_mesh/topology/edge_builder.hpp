#ifndef TBX_EDGE_BUILDER_HPP
#define TBX_EDGE_BUILDER_HPP

#include <vector>
#include "toolbox_mesh/mesh_type.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

/// @brief From a 1st ring adjency list build a list of edges
struct Edge_builder {

    /// List of edges built from the input geometry
    std::vector<Edge> _edge_list;

    /// List of edges per vertex
    /// _edge_list_per_vert[vert_id] == list of edge id in '_edge_list'
    std::vector<std::vector<Edge_idx> > _1st_ring_edges;

    void clear(){
        _edge_list.clear();
        _1st_ring_edges.clear();
    }

    /// compute allocate edge data.
    void compute(const std::vector< std::vector<tbx_mesh::Vert_idx> >& fst_ring_verts);
};

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_EDGE_BUILDER_HPP
