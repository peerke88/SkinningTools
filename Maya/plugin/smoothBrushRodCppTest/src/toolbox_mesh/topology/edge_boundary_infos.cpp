#include "toolbox_mesh/topology/edge_boundary_infos.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

void Edge_boundary_infos::compute(
        const std::vector<Edge>& edge_list,
        const std::vector<bool>& is_vert_on_side)
{
    int nb_edges = (int)edge_list.size();
    _is_side_edge.resize(nb_edges, false);
    _on_side_edges.reserve( nb_edges );
    for(int i = 0; i < nb_edges; i++)
    {
        const Edge edge = edge_list[i];
        // Store edges on sides and tag them
        if( is_vert_on_side[edge.a] && is_vert_on_side[edge.b] )
        {
            _on_side_edges.push_back( i );
            _is_side_edge[i] = true;
        }
    }
}


}// END tbx_mesh NAMESPACE =====================================================
