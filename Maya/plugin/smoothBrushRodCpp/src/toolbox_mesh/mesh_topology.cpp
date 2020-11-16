
#include "toolbox_mesh/mesh_topology.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================


void Mesh_topology_lvl_1::clear_data()
{
    _geom = nullptr;
    _vertex_to_face.clear();
    _1st_ring_verts.clear();
}

// -----------------------------------------------------------------------------

void Mesh_topology_lvl_1::update(const Mesh_geometry& mesh)
{
    clear_data();
    _geom = &mesh;

    _vertex_to_face.compute( mesh );
    _1st_ring_verts.compute( mesh, _vertex_to_face);
}

// -----------------------------------------------------------------------------

void Mesh_topology::clear_data()
{
    _topo_lvl_1.clear_data();
    _edges.clear();
    _2nd_ring_verts.clear();
    _edge_to_tri.clear();
    _edge_boundary.clear();
    _triangles_edges.clear();
    _islands.clear();
}

// -----------------------------------------------------------------------------

void Mesh_topology::update(const Mesh_geometry& mesh)
{
    clear_data();
    _topo_lvl_1.update( mesh );

    _2nd_ring_verts.compute( first_ring() );
    _edges.compute( first_ring() );
    _edge_to_tri.compute(mesh, first_ring_tris(), _edges._edge_list, is_vert_on_side());
    _edge_boundary.compute( _edges._edge_list, is_vert_on_side());
    _triangles_edges.compute(mesh, _edges._edge_list, _edge_to_tri._tri_list_per_edge);
    _islands.compute( first_ring() );
}

// -----------------------------------------------------------------------------

void Mesh_topology_lvl_1::check_integrity()
{
    // TODO transfer those checks in the struct computing the first ring neighbors.
    const int nb_vertices = (int)_1st_ring_verts._rings_per_vertex.size();
    for(int vert_i = 0; vert_i < nb_vertices; ++vert_i)
    {
        int nb_neighs = (int)_1st_ring_verts._rings_per_vertex[vert_i].size();

        if( is_vert_disconnected(vert_i) )
            tbx_assert( nb_neighs == 0 && "Lonely vertices should not have edges");

        for(int j = 0; j < nb_neighs; ++j)
        {
            int edge_id = _1st_ring_verts._rings_per_vertex[vert_i][j];
            if(edge_id == vert_i){
                tbx_assert(false && "Self edge detected, an edge should be made out of two distinct vertices");
            }

            // Check edge ids;
            if(edge_id >= 0 && edge_id >= nb_vertices){
                tbx_assert(false && "Corrupted vertex Index");
            }

            // Check edge loop integrity
            // (every edge must point to a unique vertex)
            // FIXME: quad pairs are bugged and this condition will fail
/*
            for(int n=dep; n< (dep+off); ++n ) {
                if(n == j) continue;
                int nedge_id = get_1st_ring(n);
                tbx_assert(nedge_id != edge_id);
            }
*/
        }
    }
}

// -----------------------------------------------------------------------------

}// END tbx_mesh NAMESPACE =====================================================
