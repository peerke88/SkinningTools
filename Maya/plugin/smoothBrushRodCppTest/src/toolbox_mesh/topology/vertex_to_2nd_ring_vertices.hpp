#ifndef TBX_VERTEX_TO_2ND_RING_VERTICES_HPP
#define TBX_VERTEX_TO_2ND_RING_VERTICES_HPP

#include <vector>
#include "toolbox_mesh/mesh_type.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

struct Vertex_to_2nd_ring_vertices {

    void clear(){ _2nd_ring_verts.clear(); }

    /// Compute the second neighborhood list of every vertices
    void compute(const std::vector< std::vector<tbx_mesh::Vert_idx> >& fst_ring_verts);

    /// List of 2nd ring neighborhood vertices per vertex.
    /// @warning list is not ordered
    std::vector< std::vector<tbx_mesh::Vert_idx> > _2nd_ring_verts;
};

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_VERTEX_TO_2ND_RING_VERTICES_HPP
