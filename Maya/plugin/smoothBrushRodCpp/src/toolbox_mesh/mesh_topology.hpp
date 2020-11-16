#ifndef TBX_MESH_TOPOLOGY_HPP
#define TBX_MESH_TOPOLOGY_HPP

#include <vector>
#include "toolbox_mesh/mesh_topology_lvl_1.hpp"
#include "toolbox_mesh/topology/vertex_to_2nd_ring_vertices.hpp"
#include "toolbox_mesh/topology/edge_builder.hpp"
#include "toolbox_mesh/topology/edge_to_triangle.hpp"
#include "toolbox_mesh/topology/edge_boundary_infos.hpp"
#include "toolbox_mesh/topology/triangle_to_edge.hpp"
#include "toolbox_mesh/topology/island_builder.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

/**
 * @brief Static and rich topology information from a list of triangles
 *
 * This class takes in input a simple triangular mesh (Mesh_geometry)
 * and builds more advance topological information, such as list of edges,
 * map vertex to triangles, 1st ring of directly adjacent vertex to another etc.
*/
class Mesh_topology {
public:

    Mesh_topology() { }

    Mesh_topology(const Mesh_geometry& mesh)
    {
        update( mesh );
    }

    ~Mesh_topology(){ clear_data(); }

    /// Clear all attributes
    void clear_data();

    /// Updates every connectivity datas according to "mesh"
    void update(const Mesh_geometry& mesh);

    //  ------------------------------------------------------------------------
    /// @name Topology level 1 (shortcuts)
    //  ------------------------------------------------------------------------

    inline int get_nb_vertices() const { return _topo_lvl_1.get_nb_vertices(); }

    inline const Mesh_geometry& geom() const                      { return _topo_lvl_1.geom(); }
    inline void reset_geometry_pointer(const Mesh_geometry* mesh) { _topo_lvl_1.reset_geometry_pointer(mesh); }
    inline void check_integrity()                                 { _topo_lvl_1.check_integrity(); }
    inline bool is_closed() const                                 { return _topo_lvl_1.is_closed(); }
    inline bool is_manifold() const                               { return _topo_lvl_1.is_manifold(); }
    inline bool is_vert_disconnected(tbx_mesh::Vert_idx i) const  { return _topo_lvl_1.is_vert_disconnected(i); }
    inline bool is_vert_connected(tbx_mesh::Vert_idx i) const     { return _topo_lvl_1.is_vert_connected(i); }
    inline bool is_vert_on_side(tbx_mesh::Vert_idx i) const       { return _topo_lvl_1.is_vert_on_side(i); }
    inline const std::vector<bool>& is_vert_on_side() const       { return _topo_lvl_1.is_vert_on_side(); }
    inline const std::vector<tbx_mesh::Vert_idx>& none_manifold_vert_list() const { return _topo_lvl_1.none_manifold_vert_list(); }
    inline const std::vector<tbx_mesh::Vert_idx>& vert_on_side_list() const       { return _topo_lvl_1.vert_on_side_list(); }
    inline unsigned nb_neighbors(tbx_mesh::Vert_idx idx) const { return _topo_lvl_1.nb_neighbors( idx ); }
    inline tbx_mesh::Vert_idx neighbor_to(tbx_mesh::Vert_idx idx, int n) const        { return _topo_lvl_1.neighbor_to(idx, n); }
    inline const std::vector< std::vector< tbx_mesh::Vert_idx > >& first_ring() const { return _topo_lvl_1.first_ring(); }
    inline const std::vector< tbx_mesh::Vert_idx >& first_ring_at(tbx_mesh::Vert_idx vert_i) const { return _topo_lvl_1.first_ring_at(vert_i); }
    inline const std::vector<std::vector<Tri_idx> >& first_ring_tris() const                       { return _topo_lvl_1.first_ring_tris(); }

    inline operator First_ring_it() { return First_ring_it(first_ring()); }
    inline operator const Mesh_topology_lvl_1& () const { return _topo_lvl_1; }
    inline operator       Mesh_topology_lvl_1& ()       { return _topo_lvl_1; }

    //  ------------------------------------------------------------------------
    /// @name Faces accessors
    //  ------------------------------------------------------------------------

    /// Get a triangle described by a list of three edge indices.
    /// You can then retreive the edge with #get_edge()
    Tri_edges tris_edges(Tri_idx tri_index) const {
        return _triangles_edges._tri_edges[tri_index];
    }

    //  ------------------------------------------------------------------------
    /// @name 1st ring neighborhood accessors
    //  ------------------------------------------------------------------------


    /// Get edge indices at the first ring neighborhood of the ith vertex.
    /// @note same order as with first ring of vertices (first_ring())
    const std::vector<Edge_idx>& first_ring_edges(tbx_mesh::Vert_idx i) const {
        return _edges._1st_ring_edges[i];
    }

    //  ------------------------------------------------------------------------
    /// @name 2nd ring neighborhood accessors
    //  ------------------------------------------------------------------------

    const std::vector<tbx_mesh::Vert_idx>& second_ring_verts(tbx_mesh::Vert_idx i) const{
        tbx_assert( i >= 0 && i < get_nb_vertices() );
        return _2nd_ring_verts._2nd_ring_verts[i];
    }

    const std::vector< std::vector<tbx_mesh::Vert_idx> >& second_ring_verts() const{
        return _2nd_ring_verts._2nd_ring_verts;
    }

    //  ------------------------------------------------------------------------
    /// @name Edges accessors
    //  ------------------------------------------------------------------------

    Edge edge(Edge_idx i) const { return _edges._edge_list[i]; }

    const std::vector<Edge>& edge_list() const { return _edges._edge_list; }

    int nb_edges() const { return (int)_edges._edge_list.size(); }

    /// List of triangles shared by the edge 'i'. It can be one for edges at
    /// boundaries two for closed objects or another number if the mesh
    /// is not 2-manifold
    const std::vector<Tri_idx>& edge_shared_tris(Edge_idx i) const { return _edge_to_tri._tri_list_per_edge[i]; }

    bool is_side_edge(Edge_idx i) const { return _edge_boundary._is_side_edge[i]; }

    //  ------------------------------------------------------------------------
    /// @name Islands accessors
    //  ------------------------------------------------------------------------

    const std::vector<std::vector<tbx_mesh::Vert_idx> >& island_lists() const { return _islands._island_idx_to_vertices_list; }

    const std::vector<tbx_mesh::Vert_idx>& island(Island_idx idx) const { return _islands._island_idx_to_vertices_list[idx]; }

    unsigned nb_islands() const { return unsigned(_islands._island_idx_to_vertices_list.size()); }

    Island_idx island_index(tbx_mesh::Vert_idx vidx) const { return _islands._vertex_to_island_index[vidx]; }

    //  ------------------------------------------------------------------------
    /// @name Attributes
    //  ------------------------------------------------------------------------
    Mesh_topology_lvl_1 _topo_lvl_1;

    Vertex_to_2nd_ring_vertices _2nd_ring_verts;
    Edge_builder _edges;
    Edge_to_triangle _edge_to_tri;
    Edge_boundary_infos _edge_boundary;
    Triangle_to_edge _triangles_edges;
    Island_builder _islands;
};

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_MESH_TOPOLOGY_HPP
