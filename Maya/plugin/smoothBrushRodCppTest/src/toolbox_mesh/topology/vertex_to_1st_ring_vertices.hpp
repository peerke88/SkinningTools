#ifndef TBX_VERTEX_TO_1ST_RING_VERTICES_HPP
#define TBX_VERTEX_TO_1ST_RING_VERTICES_HPP

#include <vector>
#include "toolbox_mesh/mesh_geometry.hpp"
#include "toolbox_mesh/topology/vertex_to_face.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

/// @brief associative arrays <b>per vertex</b>
struct Vertex_to_1st_ring_vertices {

    Vertex_to_1st_ring_vertices()
        : _is_mesh_closed(true)
        , _is_mesh_manifold(true)
    {

    }

    void clear()
    {
        _is_vert_on_side.clear();
        _not_manifold_verts.clear();
        _on_side_verts.clear();
    }

    /// Is the mesh closed
    bool _is_mesh_closed;

    /// When "false" the mesh is not 2-manifold, however, "true" does not
    /// necessarily garantee 100% the mesh will be 2-manifold.
    /// (e.g. self intersection is not detected)
    /// In addition opened meshes are considered manifolds,
    /// Only serious topological defects are detected as non-manifold.
    bool _is_mesh_manifold;

    /// Per vertex list of the 1st ring of vertex neighbors
    /// _rings_per_vertex[id_vertex][ith_vert_neighbor] == vert_neighbor_id
    /// @note each list of ring is ordered
    std::vector< std::vector<tbx_mesh::Vert_idx> > _rings_per_vertex;

    /// Does the ith vertex belongs to a boundary of the mesh
    std::vector<bool> _is_vert_on_side;

    /// List of vertices index presenting topological defects.
    std::vector<tbx_mesh::Vert_idx> _not_manifold_verts;

    /// List of every vertices on some boundary of the mesh
    std::vector<tbx_mesh::Vert_idx> _on_side_verts;

    /// Compute and allocate topological informations
    void compute(const Mesh_geometry& mesh,
                 const Vertex_to_face& vert_to_face);
};

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_VERTEX_TO_1ST_RING_VERTICES_HPP
