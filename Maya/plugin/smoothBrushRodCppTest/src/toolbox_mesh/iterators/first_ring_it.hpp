#ifndef TBX_FIRST_RING_IT_HPP
#define TBX_FIRST_RING_IT_HPP

#include <vector>
#include "toolbox_mesh/mesh_type.hpp"

// Forward defs ================================================================
namespace tbx_mesh {
    class Mesh_topology;
    class Mesh_topology_lvl_1;
}
// Forward defs ================================================================

// =============================================================================
namespace tbx_mesh {
// =============================================================================

class First_ring_it {
    const std::vector< std::vector<tbx_mesh::Vert_idx> >& _first_ring;
public:

    First_ring_it(const std::vector< std::vector<tbx_mesh::Vert_idx> >& first_ring)
        : _first_ring(first_ring)
    {

    }

    /// Shortcut to -> First_ring_it(topo.first_ring())
    First_ring_it(const Mesh_topology& topo);
    First_ring_it(const Mesh_topology_lvl_1& topo);

    ///@return number of direct neighbors adjacent to the vertex "idx"
    inline unsigned nb_neighbors(tbx_mesh::Vert_idx idx) const {
        return (unsigned)_first_ring[idx].size();
    }

    /// @brief alias to Maya_mesh::nb_neighbors()
    inline unsigned valence(tbx_mesh::Vert_idx idx) const { return nb_neighbors(idx); }

    ///@return index of the nth neighbor adjacent to vertex "idx"
    inline unsigned neighbor_to(tbx_mesh::Vert_idx idx, int n) const {
        return (unsigned)_first_ring[idx][n];
    }

    const std::vector< tbx_mesh::Vert_idx >& first_ring_at(tbx_mesh::Vert_idx vert_i) const {
        return _first_ring[vert_i];
    }

    int nb_vertices() const { return int(_first_ring.size()); }
};

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_FIRST_RING_IT_HPP
