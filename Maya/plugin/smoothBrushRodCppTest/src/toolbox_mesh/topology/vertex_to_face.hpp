#ifndef TBX_VERTEX_TO_FACE_HPP
#define TBX_VERTEX_TO_FACE_HPP

#include <vector>
#include "toolbox_mesh/mesh_geometry.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

/// @brief Compute associative arrays from vertex to face.
struct Vertex_to_face {
    /// list of triangle indices connected to a given vertex.
    /// _1st_ring_tris[index_vert][nb_connected_triangles] = index triangle
    /// @warning triangle list per vert are unordered
    std::vector<std::vector<Tri_idx> > _1st_ring_tris;

    /// list of quad indices connected to given vertex.
    /// _1st_ring_quads[index_vert][nb_connected_quads] = index quad in
    /// @warning quad list per vert are unordered
    std::vector<std::vector<Quad_idx> > _1st_ring_quads;

    /// Does the ith vertex belongs to a face? (triangle or a quad)
    std::vector<bool> _is_vertex_connected;

    void clear() {
        _1st_ring_quads.clear();
        _1st_ring_tris.clear();
        _is_vertex_connected.clear();
    }

    /// Allocate and compute attributes
    void compute(const Mesh_geometry& mesh);
};

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_VERTEX_TO_FACE_HPP
