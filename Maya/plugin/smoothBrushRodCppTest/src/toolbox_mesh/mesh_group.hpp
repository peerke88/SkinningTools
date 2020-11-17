#ifndef TBX_MESH_GROUP_HPP
#define TBX_MESH_GROUP_HPP

#include <string>
#include <vector>
#include "toolbox_mesh/mesh_geometry.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

/// @brief A class representing a group of vertices from a mesh.
struct Mesh_group
{
    Mesh_group(const Mesh_geometry& geom, std::string name = "")
        : _geom(geom)
        , _name(name)
    {}

    /// Append the vertices of the group to the given vector.
    void get_vertices(std::vector<tbx::Vec3>& vertices_out) const
    {
        for (auto idx : _vertices)
        {
            vertices_out.push_back(_geom._vertices[idx]);
        }
    }

    /// Returns a bitset where bits_out[i] == 1 if vertex i is in the group.
    void get_bitset(std::vector<bool>& bits_out) const
    {
        bits_out.resize(_geom._vertices.size(), false);
        // maybe 'OR' it with input ?
        for (auto idx : _vertices)
        {
            bits_out[idx] = true;
        }
    }

    // Shouldn't we keep the groups somewhere else ?
    const Mesh_geometry& _geom;

    std::vector<tbx_mesh::Vert_idx> _vertices;

    std::string _name;
};

// -----------------------------------------------------------------------------

/// @brief Check that no overlap occurs in 'groups' (assert() otherwise)
/// @param[in] groups : a list of groups of vertices which shall not overlap
void check_partition(const Mesh_geometry& geom,
                     const std::vector<Mesh_group>& groups);

// -----------------------------------------------------------------------------

/// Returns the triangles which belong to the given mesh group
/// (i.e. all vertices belong to the group).
inline void extract_triangles(const Mesh_geometry& geom,
                              const Mesh_group& group,
                              std::vector<Tri_face>& triangles_out)
{

    std::vector<bool> bits;
    group.get_bitset(bits);

    for (Tri_face tri : geom._triangles)
    {
        if ((bits[tri.a]) &&  (bits[tri.b]) && (bits[tri.c]))
        {
            triangles_out.push_back(tri);
        }
    }
}

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif// TBX_MESH_GROUP_HPP

