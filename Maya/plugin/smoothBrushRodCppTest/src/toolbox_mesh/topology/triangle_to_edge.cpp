#include "toolbox_mesh/topology/triangle_to_edge.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

void Triangle_to_edge::compute(
        const Mesh_geometry& mesh,
        const std::vector<Edge>& edge_list,
        const std::vector<std::vector<Tri_idx> >& tri_list_per_edge)
{
    int nb_edges = (int)edge_list.size();

    // Find the edge indices in _edge_list for every triangles.
    // We look up every edges and update triangles in the neighborhood.
    _tri_edges.clear();
    _tri_edges.resize( mesh.nb_triangles() );
    for(int edge_idx = 0; edge_idx < nb_edges; edge_idx++)
    {
        Edge edge = edge_list[edge_idx];
        const std::vector<int>& tri_list = tri_list_per_edge[edge_idx];
        for(unsigned t = 0; t < tri_list.size(); ++t)
        {
            const int tri_idx = tri_list[t];
            Tri_face tri = mesh.triangle(tri_idx);

            // Seek the triangle edge matching ours
            int u = 0;
            for(; u < 3; ++u) {
                if( Edge( tri[u], tri[(u+1) % 3] ) == edge )
                    break;
            }
            // Update our list
            _tri_edges[tri_idx][u] = edge_idx;
        }
    }

    #ifndef NDEBUG
    for(int i = 0; i < mesh.nb_triangles(); ++i) {
        for( int j = 0; j < 3; ++j) {
            // Check if every edges has been properly updated
            tbx_assert( _tri_edges[i][j] >= 0 );
        }
    }
    #endif
}

}// END tbx_mesh NAMESPACE =====================================================
