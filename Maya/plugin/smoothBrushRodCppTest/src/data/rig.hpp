#pragma once

#include <maya/MGlobal.h>
#include <toolbox_stl/memory.hpp>
#include <toolbox_mesh/mesh_type.hpp>
#include <toolbox_maya/data/maya_mesh.hpp>
#include <toolbox_maya/data/maya_skeleton.hpp>
#include <vector>

// Forward defs ----------------------------------------------------------------
namespace tbx {
    template<class T>
    class Grid_partition;
}
// -----------------------------------------------------------------------------

// =============================================================================
namespace skin_brush {
// =============================================================================

///@brief a rig gather skeleton, Mesh and some extra informations linked to both
class Rig {
public:

    ~Rig();

    void clear();

    Rig(const Maya_mesh& mesh, const Maya_skeleton& skel);
    Rig(const Rig& copy);

    /// @warning Heavy computation
    void precompute_extra_links(float radius){

        if(radius == _user_radius_extra_links )
            return;

        MGlobal::displayInfo( "Update volume radius" );
        compute_extra_links( _extra_vertex_links,
                             _augmented_first_ring,
                             _weld_source_vertex,
                             _weld_list,
                             radius);

        if( is_augmented_per_edge_weights_ready() )
            compute_augmented_weights(_augmented_first_ring);

        _user_radius_extra_links = radius;
    }

    // -------------------------------------------------------------------------
    /// @name Accessors
    // -------------------------------------------------------------------------

    const tbx::Grid_partition<tbx_mesh::Vert_idx>& get_grid_partition() const;

    /// Extra vertex links added by looking up vertices nearest neighbors
    /// within a user defined radius, user can manually add links as well.
    const std::vector< std::vector<tbx_mesh::Vert_idx> >& get_extra_vertex_links() const;
    /// Original mesh first ring neighbors + extra vertex links
    const std::vector< std::vector<tbx_mesh::Vert_idx> >& get_augmented_first_ring() const;
    /// A mix of cotan weights and edge length for extra links
    const std::vector<std::vector<float> >& get_augmented_per_edge_weights() const;
    /// Tag vertices too close to each other to establish a link.
    /// Instead we merge the vertices topology into each other and mark them
    /// as welded.
    /// _weld_source_vertex[destination] = source
    /// if source == -1 nothing to do.
    const std::vector<tbx_mesh::Vert_idx>& get_weld_source_vertex() const;
    const std::vector <std::vector<int> >& get_weld_list() const;

    float get_user_radius_extra_links() const;

    // -------------------------------------------------------------------------
    /// @name Shortcuts
    // -------------------------------------------------------------------------

    const tbx_maya::Maya_mesh&     mesh() const;
    const tbx_maya::Maya_skeleton& skel() const;

    const tbx_mesh::Mesh_topology& topo() const { return mesh().topo(); }
    const tbx_mesh::Mesh_geometry& geom() const { return mesh().geom(); }

    unsigned nb_vertices() const;
    tbx::Vec3 vertex(tbx_mesh::Vert_idx idx) const;

    const std::vector<std::vector<float> >& get_per_edge_weights() const { return mesh().attrs().get_per_edge_weights(); }
    const std::vector<float>& get_sum_edge_weights() const { return mesh().attrs().get_sum_edge_weights(); }
    const std::vector< std::vector<tbx::Vec3> >& get_vert_output_edges() const { return mesh().attrs().get_vert_output_edges(); }


private:
    // -------------------------------------------------------------------------
    /// @name Attributes
    // Note: don't forget to update code of the copy constructor and the clear()
    // method when necessary
    // -------------------------------------------------------------------------
    const tbx_maya::Maya_mesh& _mesh;
    const tbx_maya::Maya_skeleton& _skel;

    mutable tbx::Uptr< tbx::Grid_partition<tbx_mesh::Vert_idx> > _grid;

    float _user_radius_extra_links;
    /// Additional neighbors to a vertex
    /// _extra_vertex_link[vertex_id][ith_link] = linked_vertex_id
    mutable std::vector< std::vector<tbx_mesh::Vert_idx> > _extra_vertex_links;

    ///@brief extra links prescribed by the user
    /// _extra_vertex_link[vertex_id][ith_link] = linked_vertex_id
    std::vector< std::vector<tbx_mesh::Vert_idx> > _user_extra_vertex_links;

    /// Original mesh connectivity + extra vertex links
    mutable std::vector< std::vector<tbx_mesh::Vert_idx> > _augmented_first_ring;
    /// A mix of cotan weights and edge length for extra links
    mutable std::vector<std::vector<float> > _augmented_per_edge_weights;

    /// _weld_source_vertex[destination] = source
    /// if source == -1 nothing to do.
    /// In other words:
    /// _weld_source_vertex[welded vertex id ] = vertex idx to copy values from.
    mutable std::vector<tbx_mesh::Vert_idx> _weld_source_vertex;

    mutable std::vector <std::vector<int> > _weld_list;

    // -------------------------------------------------------------------------
    /// @name Accessors
    // -------------------------------------------------------------------------
    bool is_grid_ready() const;
    bool is_extra_vertex_links_ready() const { return _extra_vertex_links.size() != 0; }
    bool is_augmented_first_ring_ready() const { return _augmented_first_ring.size() != 0; }
    bool is_augmented_per_edge_weights_ready() const { return _augmented_per_edge_weights.size() != 0; }
    bool is_weld_source_vertex_ready() const { return _weld_source_vertex.size() != 0; }
    bool is_weld_list_ready() const { return _weld_list.size() != 0; }

    // -------------------------------------------------------------------------
    /// @name Utilities
    // -------------------------------------------------------------------------

    ///@param radius: length of the search when trying to link vertices of
    /// separate mesh islands.
    void compute_extra_links(std::vector<std::vector<tbx_mesh::Vert_idx> >& extra_vertex_links,
            std::vector<std::vector<tbx_mesh::Vert_idx> >& augmented_first_ring,
            std::vector<tbx_mesh::Vert_idx>& weld_vertices,
            std::vector<std::vector<tbx_mesh::Vert_idx> >& weld_list,
            float radius) const;

    void compute_augmented_weights(
            const std::vector< std::vector<tbx_mesh::Vert_idx> >& augmented_first_ring) const;

    ///  @return true when vert_i vert_j belongs to the same skin weight
    /// partition or partitions neighbors to each other.
    bool is_within_same_cluster(const std::vector<bone::Id>& rigid_partitions,
                             tbx_mesh::Vert_idx vert_i,
                             tbx_mesh::Vert_idx vert_j) const;

};


}// END skin_brush Namespace ===================================================

