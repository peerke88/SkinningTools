#ifndef TBX_MESH_HPP
#define TBX_MESH_HPP

#include "toolbox_maths/vector3.hpp"
#include "toolbox_mesh/mesh_type.hpp"
#include <vector>


// =============================================================================
namespace tbx_mesh {
// =============================================================================

template<class T>
inline T Invalid(){ return (T)(-1); }

/**
 * @brief This structure holds the basic geometry of a mesh
 * Holds a list of vertices and a list of faces (which can be triangles or quads).
 * All the lists are std vectors which are public and can be accessed and
 * iterated.
*/
class Mesh_geometry {
public:

    /// Default constructor. Creates an empty geometry.
    Mesh_geometry(){}

    /// Destructor.
    ~Mesh_geometry() {}

    /// Clears all vertex, triangle and quads, making the mesh empty.
    void clear_data();

    /// Appends all vertices and faces from the given geometry to this one.
    inline void append_mesh( const Mesh_geometry& other );

    // -------------------------------------------------------------------------
    /// @name Const accessors
    // -------------------------------------------------------------------------
    inline const tbx::Vec3& vertex(tbx_mesh::Vert_idx idx) const { return _vertices[idx]; }
    inline int nb_vertices() const { return (int)_vertices.size(); }

    const Tri_face& triangle(Tri_idx t) const { return _triangles[t]; }
    int nb_triangles() const { return (int)_triangles.size(); }

    const Quad_face& quad(Tri_idx t) const { return _quads[t]; }
    int nb_quads() const { return (int)_quads.size(); }

    // -------------------------------------------------------------------------
    /// @name Attributes
    // -------------------------------------------------------------------------
public:
    /// List of vertices
    std::vector<tbx::Vec3> _vertices;
    /// List of triangles
    std::vector<Tri_face> _triangles;
    /// List of quads
    std::vector<Quad_face> _quads;

};
}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/mesh_geometry.inl"

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_MESH_HPP
