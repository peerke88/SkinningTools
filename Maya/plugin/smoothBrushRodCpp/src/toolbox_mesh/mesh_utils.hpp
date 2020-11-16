#ifndef TBX_MESH_UTILS_HPP
#define TBX_MESH_UTILS_HPP

#include <vector>

#include "toolbox_mesh/mesh_geometry.hpp"
#include "toolbox_mesh/mesh_topology.hpp"
#include "toolbox_maths/bbox3.hpp"
#include "toolbox_maths/triplet.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

// TODO: delete this namespace
// =============================================================================
namespace mesh_utils {
// =============================================================================


/// Given the vertex indices 'edge.a', 'edge.b' and 'origin'.
/// Return the edge going outwards from 'origin' i.e: edge.a = origin
static inline
Edge get_outward_edge(const Mesh_topology& m,
                              Edge_idx edge_idx,
                              tbx_mesh::Vert_idx origin)
{
    const Edge edge = m.edge(edge_idx);
    if( edge.a != origin){
        tbx_assert( edge.b == origin );
        return Edge(origin, edge.a);
    }
    else
        return edge;
}

// -----------------------------------------------------------------------------

/// @return The 'edge_idx' vector direction.
/// @warning no garantee on the edge actual orientation
static inline
tbx::Vec3 edge_dir(const Mesh_geometry& m, const Edge e)
{
    return m.vertex(e.b) - m.vertex(e.a);
}

// -----------------------------------------------------------------------------

/// @return The 'edge_idx' length.
static inline
float edge_len(const Mesh_topology& m, Edge_idx edge_idx)
{
    return edge_dir( m.geom(), m.edge(edge_idx) ).norm();
}

// -----------------------------------------------------------------------------

static inline
float compute_average_edge_length( const Mesh_topology& topo )
{
    float average_edge_len = 0.0f;
    for( const Edge& edge : topo.edge_list())
    {
        average_edge_len += edge_dir(topo.geom(), edge).norm();
    }

    return average_edge_len / float(topo.nb_edges());
}

// -----------------------------------------------------------------------------

static inline
float tri_area(const tbx::Vec3& a,
               const tbx::Vec3& b,
               const tbx::Vec3& c)
{
    const tbx::Vec3 edge0 = b - a;
    const tbx::Vec3 edge1 = c - a;
    return (edge0.cross(edge1)).norm() / 2.f;
}

/// @return The 'tri_idx' triangle area.
inline float tri_area(const Mesh_geometry& mesh, Tri_idx t_idx);

/// @return sum of the triangle areas around vertex 'v_idx'
inline float sum_tri_area(const Mesh_topology& topo, tbx_mesh::Vert_idx v_idx);


/// @return normalized normal of triangle 'tri_idx'
inline tbx::Vec3 tri_normal(const Mesh_geometry& mesh,
                       Tri_idx t_idx);

/// Get the bounding box of a givben mesh
inline tbx::Bbox3 bounding_box(const Mesh_geometry& mesh);

// -----------------------------------------------------------------------------

/// @return the dihedral signed angle [-PI PI] between the 2 triangles shared
/// at the edge 'edge_idx'. If the number of shared triangles is not equal to 2
/// we return a value strictly greater than M_PI*2.f to signal it.
/// The sign of the angle is determine by the orientation of the edge
/// 'edge_idx' and the order of triangles in m.get_edge_shared_tris(edge_idx)
inline float edge_dihedral_angle(const Mesh_topology& m, int edge_idx);

// -----------------------------------------------------------------------------


/**
  Compute the barycentric coordinates of 'sample' inside a triangle (a, b, c).
  sample = (x * a + y * b + z * c) / (x + y + z)
 @code
           (b)
            +
           /|\
          / | \
         /  |  \
        /.z | .x\
       /    +    \
      /   *(s)*   \
     /  *       *  \
    / *    .y     * \
   + --------------- +
 (a)                 (c)
 @endcode

 You can use those coordinates to linearly interpolate values associated to
 (a,b,c) like colors or anything else.

 @code
 tbx::Vec3 c = barycentric_coordinates(a, b, c, sample);
 tbx::Vec3 color = (color_a * c.x + color_b * c.y +  color_c * c.z) / c.sum();
 @endcode
*/
inline static
tbx::Vec3 barycentric_coordinates(const tbx::Vec3& a,
                             const tbx::Vec3& b,
                             const tbx::Vec3& c,
                             const tbx::Vec3& sample)
{
    return tbx::Vec3(tri_area(sample, b, c),
                     tri_area(sample, a, c),
                     tri_area(sample, a, b));
}

// -----------------------------------------------------------------------------

/// Get the vertices of a given triangle from a mesh.
inline void get_triangle_vertices(const Mesh_geometry& mesh,
                                  Tri_idx t_idx,
                                  std::vector<tbx::Vec3>& vertices_out);

/// Get the vertices of a given quad from a mesh.
inline void get_quad_vertices(const Mesh_geometry& mesh,
                              Quad_idx q_idx,
                              std::vector< tbx::Vec3 >& vertices_out);

// -----------------------------------------------------------------------------

/// Compute normals of 'mesh' by averaging the faces around vertices
/// @param mesh : mesh used to compute the normals
/// @param normals : list of normals per vertex (same order as in 'mesh')
void normals(const Mesh_geometry& mesh, std::vector<tbx::Vec3>& normals_out);

//void tangents(const Mesh_geometry& mesh, std::vector<tbx::Vec3>& normals_out);

// -----------------------------------------------------------------------------

/// Apply scaling of 'scale' to 'mesh'
void scale(Mesh_geometry& mesh, const tbx::Vec3& scale);

// -----------------------------------------------------------------------------

/// Apply translation 'tr' to 'mesh'
void translate(Mesh_geometry& mesh, const tbx::Vec3& tr);

// -----------------------------------------------------------------------------

/// Compute a cotan weight (hacked to be positive)
/// at a single vertex "vertex_i" for its edge "edge_j"
/// -> m.first_ring()[vertex_i][edge_j]
float laplacian_positive_cotan_weight(const Mesh_geometry& geom,
                                      const Mesh_topology_lvl_1& m,
                                      tbx_mesh::Vert_idx vertex_i,
                                      int edge_j );

// -----------------------------------------------------------------------------

/// Compute cotangent weights for every vertices.
/// Those are hacked cotangents weights where we take the absolute value of
/// cos(alpha) and cos(beta). As a result cotan weights are always positive.
/// In certain applications these seems to perform better.
void laplacian_positive_cotan_weights(const Mesh_topology_lvl_1& m,
                                      std::vector< std::vector<float> >& per_edge_cotan_weights);

// -----------------------------------------------------------------------------

/// Compute a cotan weight at a single vertex "curr_vert" for its edge
/// "edge_curr"
/// -> m.first_ring()[curr_vert][edge_curr]
float laplacian_cotan_weight(const Mesh_geometry& geom,
                             const Mesh_topology_lvl_1 &topo,
                             tbx_mesh::Vert_idx curr_vert,
                             int edge_curr);

// -----------------------------------------------------------------------------

/// Compute cotangent weights for every vertices.
/// Cotans weights are used to compute the laplacian of a function over the
/// mesh's surface
void laplacian_cotan_weights(
        const Mesh_geometry& geom,
        const Mesh_topology_lvl_1& m,
        std::vector< std::vector<float> >& per_edge_cotan_weights);

// -----------------------------------------------------------------------------

/// Compute edge length laplacian at a single vertex
std::vector<float> laplacian_edge_length_weights(
        const Mesh_geometry& geom,
        const First_ring_it& topo,
        tbx_mesh::Vert_idx vertex_i);

// -----------------------------------------------------------------------------

///
void laplacian_edge_length_weights(
        const Mesh_geometry& geom,
        const First_ring_it& m,
        std::vector< std::vector<float> >& per_edge_length_weights);

// -----------------------------------------------------------------------------

/// Associate a weight of value == val to every vertices.
void uniform_weights(
        const Mesh_geometry& geom,
        const First_ring_it& topo,
        std::vector< std::vector<float> >& per_edge_uniform_weights,
        float val = 1.0f);

// -----------------------------------------------------------------------------

/// On meshes without volume (planar sheet) we detect vertices lying on a
/// degenerate boundary i.e a corner with just one triangle. This case makes it
/// hard to generate stable weights such as laplacian cotan so it's best to
/// slightly change the topology to gracefully handle every boundary cases.
/**
  @code
  // For a corner like this:
             +
            / \
           /   \
          +-----+
         / \   / \
        /   \ /   \
       +-----+-----+
      / \   / \   / \
     .   . .   . .   .
    .     .     .     .

   // We want to flip the edge as below because this triangulation is
   // more stable to compute things such as the laplacian:
             +
            /|\
           / | \
          +  |  +
         / \ | / \
        /   \|/   \
       +-----+-----+
      / \   / \   / \
     .   . .   . .   .
    .     .     .     .
    @endcode
*/
void flip_edge_corners(Mesh_geometry& geom);

// -----------------------------------------------------------------------------

/// @return A sparse representation of the Laplacian
/// list[ith_row][list of columns] = Triplet(ith_row, jth_column, matrix value)
std::vector<std::vector<Triplet<float>> >
get_laplacian(const Mesh_geometry& geom,
              const Mesh_topology_lvl_1& topo);

}// END mesh_utils NAMESPACE ===================================================
}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/mesh_utils.inl"

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_MESH_UTILS_HPP

