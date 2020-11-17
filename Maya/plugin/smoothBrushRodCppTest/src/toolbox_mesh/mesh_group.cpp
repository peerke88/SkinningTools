#include "toolbox_mesh/mesh_group.hpp"

#include <algorithm>

// =============================================================================
namespace tbx_mesh {
// =============================================================================

void check_partition(const Mesh_geometry& geom,
                     const std::vector<Mesh_group>& groups)
{
    std::vector<tbx_mesh::Vert_idx> all_idx;
    for (auto group : groups)
    {
        all_idx.insert(all_idx.end(), group._vertices.begin(), group._vertices.end());
    }

    std::sort(all_idx.begin(), all_idx.end());

    tbx_assert( all_idx.size()  == geom._vertices.size());

    for (unsigned i = 0 ; i < all_idx.size() ; ++i)
    {
       tbx_assert(all_idx[i] == i);
    }
}

}// END tbx_mesh NAMESPACE =====================================================
