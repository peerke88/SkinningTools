#include "toolbox_mesh/topology/edge_to_triangle.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

void Edge_to_triangle::compute(
        const Mesh_geometry& mesh,
        const std::vector<std::vector<Tri_idx> >& tri_list_per_vert,
        const std::vector<Edge>& edge_list,
        const std::vector<bool>& is_vert_on_side)
{
    int nb_edges = (int)edge_list.size();

    // Compute triangle list per edges
    // and tag/store edges on the mesh's boundaries
    _tri_list_per_edge.resize( nb_edges );
    for(int i = 0; i < nb_edges; i++)
    {
        const Edge edge = edge_list[i];
        // Choose first vertex
        const int vert_id = edge.a;
        // Look up tris of this vertex and seek for the edge 'e'
        const std::vector<int>& tri_list = tri_list_per_vert[vert_id];
        _tri_list_per_edge[i].reserve( is_vert_on_side[vert_id] ? 1 : 2 );
        for(unsigned t = 0; t < tri_list.size(); t++)
        {
            const int tri_idx = tri_list[t];
            Tri_face tri = mesh.triangle( tri_idx );

            for(int e = 0; e < 3; ++e) {
                if( tri.edge(e) == edge ){
                    _tri_list_per_edge[i].push_back( tri_idx );
                    break;
                }
            }
        }
    }
}

}// END tbx_mesh NAMESPACE =====================================================
