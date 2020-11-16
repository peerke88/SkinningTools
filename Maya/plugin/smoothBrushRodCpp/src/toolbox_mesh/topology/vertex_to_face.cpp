#include "toolbox_mesh/topology/vertex_to_face.hpp"

#include "toolbox_stl/vector.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

void Vertex_to_face::compute(const Mesh_geometry& mesh)
{
    clear();
    _1st_ring_tris. resize( mesh.nb_vertices() );
    _1st_ring_quads.resize( mesh.nb_vertices() );
    _is_vertex_connected.resize( mesh.nb_vertices() );
    tbx::fill( _is_vertex_connected, false );

    for(int i = 0; i < mesh.nb_triangles(); i++)
    {
        Tri_face tri = mesh.triangle( i );
        for(int j = 0; j < 3; j++){
            int v = tri[ j ];
            tbx_assert(v >= 0);
            _1st_ring_tris[v].push_back(i);
            _is_vertex_connected[v] = true;
        }
    }

    for(int i = 0; i < mesh.nb_quads(); i++){
        Quad_face quad = mesh.quad( i );
        for(int j = 0; j < 4; j++){
            int v = quad[ j ];
            _1st_ring_quads[v].push_back(i);
            _is_vertex_connected[v] = true;
        }
    }

    // FIXME: look up the list _tri_list_per_vert and re-order in order to ensure
    // triangles touching each other are next in the list.
}


}// END tbx_mesh NAMESPACE =====================================================
