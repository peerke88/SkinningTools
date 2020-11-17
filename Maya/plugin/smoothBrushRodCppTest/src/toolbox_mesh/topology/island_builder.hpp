#ifndef TBX_ISLAND_BUILDER_HPP
#define TBX_ISLAND_BUILDER_HPP

#include <vector>
#include "toolbox_mesh/mesh_type.hpp"
#include "toolbox_mesh/iterators/first_ring_it.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

/// @brief Compute groups of connected mesh vertices (i.e a mesh island)
/// A mesh may be composed of several unconnected surfaces, a group of connected
/// faces is called a "mesh island".
struct Island_builder {

    /// @brief associate each vertex to an island index
    /// _vertex_to_island_index[index_vertex] == island index
    std::vector<Island_idx> _vertex_to_island_index;

    /// @brief list of islands
    /// _island_idx_to_vertices_list[island_id] = list of vertex ids;
    std::vector<std::vector<tbx_mesh::Vert_idx> > _island_idx_to_vertices_list;

    void clear() {
        _vertex_to_island_index.clear();
        _island_idx_to_vertices_list.clear();

    }

    /// Allocate and compute attributes
    void compute(const First_ring_it& first_ring);
};

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_ISLAND_BUILDER_HPP
