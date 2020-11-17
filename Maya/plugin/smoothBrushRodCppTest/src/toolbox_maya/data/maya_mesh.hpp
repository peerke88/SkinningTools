#ifndef TOOLBOX_MAYA_MAYA_MESH_HPP
#define TOOLBOX_MAYA_MAYA_MESH_HPP

#include <maya/MObject.h>
#include <maya/MMatrix.h>

#include <toolbox_mesh/mesh_type.hpp>
#include <toolbox_maya/data/mesh_attributes.hpp>


namespace tbx_mesh {
    class Mesh_geometry;
    class Mesh_topology;
}

// =============================================================================
namespace tbx_maya {
// =============================================================================

/// @brief Extract a triangulated version of a maya mesh.
struct Maya_mesh {
private:

    /// List of vertices and triangles indices.
    tbx_mesh::Mesh_geometry* _geom;
    /// advanced topology info (1st ring neighbors etc.) (build from _geom)
    tbx_mesh::Mesh_topology* _topo;
    /// Various vertex attributes (lazy evaluated)
    Mesh_attributes _attributes;
public:

    // -------------------------------------------------------------------------

    Maya_mesh();

    Maya_mesh(const Maya_mesh& mesh);

    ~Maya_mesh();

    /// @param mesh_node : mesh shape you want to extract
    /// @param mesh_transformation : the extracted vertex position will be
    /// in local space you should provide the mesh's world matrix to transform
    /// them to global space.
    /// We recommand using:
    /// - tbx_maya::world_mmatrix(mesh_node); // in maya_utils.hpp
    Maya_mesh(MObject mesh_node, const MMatrix& mesh_transformation);

    // -------------------------------------------------------------------------

    void clear();

    /// @brief Loads _geom, _normals, _topo and _attributes
    /// @param mesh_transformation : the extracted vertex will be transformed
    /// by this matrix (we typically use tbx_maya::world_mmatrix(mesh_node))
    void load( MObject mesh_node,
               const MMatrix& mesh_transformation);

    /// @brief Loads geom and normals
    /// @param mesh_transformation : the extracted vertex will be transformed
    /// by this matrix (we typically use tbx_maya::world_mmatrix(mesh_node))
    static void load(MObject mesh_node,
                     const MMatrix& mesh_transformation,
                     tbx_mesh::Mesh_geometry& out_geom,
                     std::vector<tbx::Vec3>& out_normals);

    /// add into the scene a mesh dag node (created from 'mesh')
    /// @return transform if no parent_owner specified otherwise shape.
    /// @warning for some reasons quite slow prefer duplicating meshes with
    /// @code
    ///     new_mesh = copy(source_mesh);
    ///     set_points(new_mesh, this->geom->_vertices);
    ///     // Optionaly:
    ///     assign_material_to(new_mesh);
    /// @endcode
    static MObject add_maya_dag_mesh( const Maya_mesh& mesh);

    //static void assign_material_to(MObject mesh, const std::string& material_name = ("Blinn") );

    // -------------------------------------------------------------------------
    ///@name Accessors(shortcuts)
    // -------------------------------------------------------------------------

    unsigned nb_vertices() const;
    tbx::Vec3 vertex(tbx_mesh::Vert_idx idx) const;

    const Mesh_attributes& attrs() const { return _attributes; }
    const tbx_mesh::Mesh_topology& topo() const { return *_topo; }
    tbx_mesh::Mesh_topology& topo() { return *_topo; }
    const tbx_mesh::Mesh_geometry& geom() const { return *_geom; }
    const std::vector<tbx::Vec3>& normals() const { return attrs().get_normals(); }

    // -------------------------------------------------------------------------
    ///@name Advanced accessors
    // -------------------------------------------------------------------------

    void set_vertex(tbx_mesh::Vert_idx idx, tbx::Vec3& v);

    const std::vector<std::vector<float> >& get_per_edge_weights() const { return attrs().get_per_edge_weights(); }
    const std::vector<float>& get_sum_edge_weights() const { return attrs().get_sum_edge_weights(); }
    const std::vector< std::vector<tbx::Vec3> >& get_vert_output_edges() const { return attrs().get_vert_output_edges(); }
};

}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_MAYA_MESH_HPP
