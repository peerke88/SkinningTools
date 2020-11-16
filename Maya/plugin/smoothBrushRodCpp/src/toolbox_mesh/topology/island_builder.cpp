#include "toolbox_mesh/topology/island_builder.hpp"

#include "toolbox_stl/stack.hpp"


// =============================================================================
namespace tbx_mesh {
// =============================================================================

static
int compute_mesh_islands(std::vector<int>& island_index,
                         std::vector<std::vector<tbx_mesh::Vert_idx> >& island_lists,
                         const First_ring_it& topo)
{
    int nb_islands = 0;
    std::vector<bool> visited(topo.nb_vertices(), false);
    island_index.clear();
    island_index.resize( topo.nb_vertices(), -1);
    island_lists.clear();
    for(int vert_i = 0; vert_i < topo.nb_vertices(); ++vert_i)
    {
        if(visited[vert_i])
            continue;

        std::stack<tbx_mesh::Vert_idx> to_visit;
        to_visit.push(vert_i);
        island_lists.push_back({});
        while(to_visit.size() > 0)
        {
            tbx_mesh::Vert_idx idx = tbx::pop( to_visit );
            visited[idx] = true;
            island_index[idx] = nb_islands;
            island_lists[nb_islands].push_back(idx);
            for(tbx_mesh::Vert_idx vert_j : topo.first_ring_at(idx))
            {
                if( !visited[vert_j] ){
                    to_visit.push( vert_j );
                }
            }
        }
        nb_islands++;
    }

    tbx_assert(island_lists.size() == nb_islands);
    return nb_islands;
}

// -----------------------------------------------------------------------------

void Island_builder::compute(const First_ring_it& first_ring)
{
    compute_mesh_islands(_vertex_to_island_index,
                         _island_idx_to_vertices_list,
                         first_ring);
}

}// END tbx_mesh NAMESPACE =====================================================
