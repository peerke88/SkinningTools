#include "toolbox_mesh/topology/edge_builder.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

/// Seek edge 'e' in 'edge_idx_list' if found return the index of the edge in
/// 'edge_list'
static int seek_edge(const Edge& e,
                     const std::vector<int>& edge_idx_list,
                     const std::vector<Edge>& edge_list)
{
    int edge_idx = -1;
    std::vector<int>::const_iterator it = edge_idx_list.begin();
    for(;it != edge_idx_list.end(); ++it)
    {
        if( edge_list[ (*it) ] == e )
        {
            edge_idx = (*it);
            break;
        }
    }

    // assert if edge not found:
    // it means there is serious corruption in the data
    tbx_assert( edge_idx < (int)edge_list.size() );
    tbx_assert( edge_idx > -1                    );

    return edge_idx;
}

// -----------------------------------------------------------------------------

/// @return the number of edges according to the half edge representation in
/// fst_ring_verts[vert_id][ith_neighbor] == id_neighbor
static int compute_nb_edges(const std::vector<std::vector<tbx_mesh::Vert_idx> >& fst_ring_verts)
{
    // Stores wether a vertex has been treated, it's a mean to check wether we
    // have already see an edge or not
    std::vector<bool> done( fst_ring_verts.size(), false );

    // Look up every vertices and compute exact number of edges
    int nb_edges = 0;
    for(unsigned i = 0; i < fst_ring_verts.size(); i++)
    {
        for(unsigned n = 0; n < fst_ring_verts[i].size(); n++)
        {
            int neigh = fst_ring_verts[i][n];
            if( !done[neigh] /*never seen the edge*/)
                nb_edges++;
        }
        done[i] = true;
    }

    return nb_edges;
}

// -----------------------------------------------------------------------------

void Edge_builder::compute(
        const std::vector<std::vector<tbx_mesh::Vert_idx> >& fst_ring_verts)
{
    int nb_edges = compute_nb_edges( fst_ring_verts );

    int nb_verts = (int)fst_ring_verts.size();
    // Reset vertex flags to false
    std::vector<bool> done(nb_verts, false);
    _edge_list.resize( nb_edges );
    _1st_ring_edges.resize( nb_verts );

    // Building the list of mesh's edges as well as
    // the list of 1st ring neighbors of edges.
    int idx_edge = 0;
    for(int i = 0; i < nb_verts; i++)
    {
        int nb_neigh = (int)fst_ring_verts[i].size();
        _1st_ring_edges[i].reserve( nb_neigh );
        // look up 1st ring and add edges to the respective lists
        // if not already done
        for(int n = 0; n < nb_neigh; n++)
        {
            int neigh = fst_ring_verts[i][n];
            const Edge e(i, neigh);

            if( !done[neigh] )
            {
                // Edge seen for the first time
                _edge_list[idx_edge] = e;
                _1st_ring_edges[i].push_back( idx_edge );
                idx_edge++;
            }
            else
            {
                // Edge already created we have to
                // seek for its index
                int found_edge_idx = seek_edge(e, _1st_ring_edges[neigh], _edge_list);
                _1st_ring_edges[i].push_back( found_edge_idx );
            }
        }
        // Must be as much neighbors than edges per vertex
        tbx_assert( (int)_1st_ring_edges[i].size() == nb_neigh );
        done[i] = true;
    }
}


}// END tbx_mesh NAMESPACE =====================================================
