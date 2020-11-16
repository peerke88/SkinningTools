#include "toolbox_mesh/mesh_geometry.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

// Methods of Mesh_geometry-----------------------------------------------------

inline void Mesh_geometry::clear_data()
{
    _vertices.clear();
    _triangles.clear();
    _quads.clear();
}

// -----------------------------------------------------------------------------

inline void Mesh_geometry::append_mesh(const Mesh_geometry& other)
{
    const int vertices_before     = (int)_vertices.size();
    const int triangles_before    = (int)_triangles.size();
    const int quads_before        = (int)_quads.size();

    _vertices   .insert(_vertices.end(),    other._vertices.cbegin(),   other._vertices.cend());
    _triangles  .insert(_triangles.end(),   other._triangles.cbegin(),  other._triangles.cend());
    _quads      .insert(_quads.end(),       other._quads.cbegin(),      other._quads.cend());

    // Offset the vertex indices in the faces
    for (unsigned t = triangles_before; t < _triangles.size(); ++t)
    {
        for (int i = 0 ; i < 3 ; ++i)
        {
            _triangles[t].vert(i) += vertices_before;
        }
    }

    for (unsigned q = quads_before; q < _quads.size(); ++q)
    {
        for (int i = 0 ; i < 4 ; ++i)
        {
            _quads[q].vert(i) += vertices_before;
        }
    }

    // Remove duplicates vertices ? See mesh_utils
}

}// END tbx_mesh NAMESPACE =====================================================
