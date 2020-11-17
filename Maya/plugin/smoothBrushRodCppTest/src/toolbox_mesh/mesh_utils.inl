#include "toolbox_mesh/mesh_utils.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================


// =============================================================================
namespace mesh_utils {
// =============================================================================

inline float tri_area(const Mesh_geometry& m, Tri_idx t_idx)
{
    std::vector<tbx::Vec3> v;
    get_triangle_vertices(m, t_idx, v);
    return tri_area(v[0], v[1], v[2]);
}

// -----------------------------------------------------------------------------

inline float sum_tri_area(const Mesh_topology& topo, tbx_mesh::Vert_idx v_idx)
{
    float sum = 0.0f;
    for(Tri_idx tri : topo.first_ring_tris()[v_idx]){
        sum += tri_area(topo.geom(), tri);
    }
    return sum;
}

// -----------------------------------------------------------------------------

inline tbx::Vec3 tri_normal(const Mesh_geometry& m, Tri_idx t_idx)
{
    std::vector<tbx::Vec3> v;
    get_triangle_vertices(m, t_idx, v);

    const tbx::Vec3 edge0 = v[1] - v[0];
    const tbx::Vec3 edge1 = v[2] - v[0];
    return edge0.cross(edge1).normalized();
}


// -----------------------------------------------------------------------------

inline tbx::Bbox3 bounding_box(const Mesh_geometry& m)
{
    tbx::Bbox3 bbox;
    for( unsigned i = 0; i < m._vertices.size(); ++i )
    {
        bbox.add_point( m._vertices[i] );
    }
    return bbox;
}

// -----------------------------------------------------------------------------

inline void get_triangle_vertices(const Mesh_geometry& mesh,
                                  Tri_idx t_idx,
                                  std::vector< tbx::Vec3>& vertices_out)
{
    vertices_out.resize(3);
    const Tri_face& tri = mesh._triangles[t_idx];
    for ( int i = 0; i < 3; ++i )
    {
        vertices_out[i] = mesh._vertices[ tri[i] ];
    }
}

// -----------------------------------------------------------------------------

inline void get_quad_vertices(const Mesh_geometry& mesh,
                              Quad_idx q_idx,
                              std::vector<tbx::Vec3>& vertices_out)
{
    vertices_out.resize(4);
    const Quad_face& quad = mesh._quads[q_idx];
    for ( int i = 0; i < 4; ++i )
    {
        vertices_out[i] = mesh._vertices[ quad[i] ];
    }
}

// -----------------------------------------------------------------------------

inline float edge_dihedral_angle(const Mesh_topology& m, int edge_idx)
{
    const std::vector<int>& tris = m.edge_shared_tris( edge_idx );
    if( tris.size() != 2)
        return (float)M_PI*2.f + 1.f;

    tbx::Vec3 n0 = tri_normal(m.geom(), tris[0]);
    tbx::Vec3 n1 = tri_normal(m.geom(), tris[1]);

    tbx::Vec3 ref = edge_dir(m.geom(), m.edge(edge_idx));
    return ref.signed_angle( n0, n1 );
}

}// END mesh_utils NAMESPACE ===================================================

}// END tbx_mesh NAMESPACE =====================================================
