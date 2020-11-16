#include "toolbox_mesh/topology/vertex_to_2nd_ring_vertices.hpp"

#include <set>
#include "toolbox_stl/set.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

void Vertex_to_2nd_ring_vertices::compute(
        const std::vector< std::vector<tbx_mesh::Vert_idx> >& fst_ring_verts)
{
    _2nd_ring_verts.resize( fst_ring_verts.size() );

    std::set<tbx_mesh::Vert_idx> exclude;
    std::vector<tbx_mesh::Vert_idx> list_1st_ring;
    list_1st_ring.reserve( 20 );

    // We don't know if _2nd_ring_neigh is gonna be ordered it depends on the
    // fst_ring_neigh which has to be ordered and always turning the same way
    for(tbx_mesh::Vert_idx i = 0; i < (int)fst_ring_verts.size(); i++)
    {
        exclude.clear();
        list_1st_ring.clear();
        exclude.insert( i );

        // Explore first ring neighbor
        for(unsigned j = 0; j < fst_ring_verts[i].size(); j++)
        {
            int neigh = fst_ring_verts[i][j];
            exclude.insert( neigh );
            list_1st_ring.push_back( neigh );
        }

        // Explore second ring neighbor
        for(unsigned n = 0; n < list_1st_ring.size(); n++)
        {
            int vert_idx = list_1st_ring[n];
            for(unsigned j = 0; j < fst_ring_verts[vert_idx].size(); j++)
            {
                int neigh = fst_ring_verts[vert_idx][j];
                if( !tbx::exists( exclude, neigh) )
                {
                    _2nd_ring_verts[i].push_back( neigh );
                    exclude.insert( neigh );
                }
            }
        }
    }
}

}// END tbx_mesh NAMESPACE =====================================================
