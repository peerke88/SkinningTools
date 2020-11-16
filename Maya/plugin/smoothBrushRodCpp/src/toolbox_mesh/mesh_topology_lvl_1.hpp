#ifndef TBX_MESH_TOPOLOGY_LVL_1_HPP
#define TBX_MESH_TOPOLOGY_LVL_1_HPP

#include <vector>
#include "toolbox_mesh/mesh_geometry.hpp"
#include "toolbox_mesh/topology/vertex_to_face.hpp"
#include "toolbox_mesh/iterators/first_ring_it.hpp"
#include "toolbox_mesh/topology/vertex_to_1st_ring_vertices.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

/**
 * @brief First level of topology information from a list of triangles
 *
 * This class takes in input a simple triangular mesh (Mesh_geometry)
 * and builds the 1st ring neighborhood.
 *
 * @note this is a lighter version of Mesh_topology faster to compute
*/
class Mesh_topology_lvl_1 {
public:

    Mesh_topology_lvl_1()
        : _geom(nullptr)
    {
    }

    Mesh_topology_lvl_1(const Mesh_geometry& mesh)
        : _geom(&mesh)
    {
        update( mesh );
    }

    ~Mesh_topology_lvl_1(){ clear_data(); }

    /// Clear all attributes
    void clear_data();

    /// Updates every connectivity datas according to "mesh"
    void update(const Mesh_geometry& mesh);

    const Mesh_geometry& geom() const { return *_geom; }

    /// Set the geometry pointer (this won't update the topology the new pointer
    /// must point to a geometry that matches the current topology, otherwise
    /// you should use Mesh_topology_lvl_1::update()
    void reset_geometry_pointer(const Mesh_geometry* mesh) {
        tbx_assert( first_ring().size() == mesh->_vertices.size());
        _geom = mesh;
    }

    void check_integrity();

    // -------------------------------------------------------------------------
    /// @name Accessors
    // -------------------------------------------------------------------------

    /// @return false if the mesh have boundaries or true if it's watertight
    bool is_closed() const { return _1st_ring_verts._is_mesh_closed; }

    /// @return true if no deffects are detected (like edge shared by more than
    /// 2 triangles and such)
    bool is_manifold() const { return _1st_ring_verts._is_mesh_manifold; }

    // -------------------------------------------------------------------------
    /// @name Vertices accessors
    // -------------------------------------------------------------------------

    /// @return false if the ith vertex belongs to at least one primitive
    /// i.e triangle or quad
    bool is_vert_disconnected(tbx_mesh::Vert_idx i) const { return !_vertex_to_face._is_vertex_connected[i]; }

    /// @return true if the vertex is connected to a face
    bool is_vert_connected(tbx_mesh::Vert_idx i) const { return _vertex_to_face._is_vertex_connected[i]; }

    /// Is the ith vertex on the mesh boundary
    bool is_vert_on_side(tbx_mesh::Vert_idx i) const { return _1st_ring_verts._is_vert_on_side[i]; }

    /// Is the ith vertex on the mesh boundary
    const std::vector<bool>& is_vert_on_side() const { return _1st_ring_verts._is_vert_on_side; }

    /// List of vertex indices which are connected to not manifold triangles
    const std::vector<tbx_mesh::Vert_idx>& none_manifold_vert_list() const { return _1st_ring_verts._not_manifold_verts; }

    /// List of vertices on a side of the mesh
    const std::vector<tbx_mesh::Vert_idx>& vert_on_side_list() const { return _1st_ring_verts._on_side_verts; }

    //  ------------------------------------------------------------------------
    /// @name 1st ring neighborhood accessors
    //  ------------------------------------------------------------------------

    operator First_ring_it() { return First_ring_it(first_ring()); }

    unsigned nb_neighbors(tbx_mesh::Vert_idx idx) const {
        return (unsigned)first_ring()[idx].size();
    }

    tbx_mesh::Vert_idx neighbor_to(tbx_mesh::Vert_idx idx, int n) const {
        return first_ring_at(idx)[n];
    }

    const std::vector< std::vector< tbx_mesh::Vert_idx > >& first_ring() const {
        return _1st_ring_verts._rings_per_vertex;
    }

    const std::vector< tbx_mesh::Vert_idx >& first_ring_at(tbx_mesh::Vert_idx vert_i) const {
        return _1st_ring_verts._rings_per_vertex[vert_i];
    }

    /// Get triangle list at the first ring neighborhood of the ith vertex.
    /// @warning !! this list is unordered unlike the other 1st ring list !!
    // FIXME: add a post-process that re-order this list c.f compute_face_index()
    const std::vector<std::vector<Tri_idx> >& first_ring_tris() const {
        return _vertex_to_face._1st_ring_tris;
    }

    int get_nb_vertices() const { return (int)_1st_ring_verts._rings_per_vertex.size(); }

private:

    //  ------------------------------------------------------------------------
    /// @name Attributes
    //  ------------------------------------------------------------------------

    const Mesh_geometry* _geom;

    Vertex_to_face _vertex_to_face;
    Vertex_to_1st_ring_vertices _1st_ring_verts;
};

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_MESH_TOPOLOGY_LVL_1_HPP
