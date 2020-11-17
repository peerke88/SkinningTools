#ifndef TOOLBOX_MAYA_MESH_ATTRIBUTES_HPP
#define TOOLBOX_MAYA_MESH_ATTRIBUTES_HPP

#include <vector>
#include <toolbox_maths/vector3.hpp>

namespace tbx_mesh {
    class Mesh_geometry;
    class Mesh_topology;
}

// =============================================================================
namespace tbx_maya {
// =============================================================================

class Mesh_attributes {
private:

    /// Geometry and topology we based our computation of the attributes:
    const tbx_mesh::Mesh_geometry* _geom;
    const tbx_mesh::Mesh_topology* _topo;

    //--------------------------------------------------------------------------
    /// @name Attributes
    //--------------------------------------------------------------------------

    /// @note: mutable members are computed on demand (in their get accessor)
    /// They should be copied in the copy constructor only if they were
    /// previously initialized.

    mutable std::vector< std::vector<float> > _per_edge_weights;
    mutable std::vector<float> _sum_edge_weights;
    mutable std::vector< std::vector<tbx::Vec3> > _vert_output_edges;
    /// Normal at each vertex.
    std::vector<tbx::Vec3> _normals;

    bool is_per_edge_weights_ready()  const { return _per_edge_weights.size()  != 0; }
    bool is_sum_edge_weights_ready()  const { return _sum_edge_weights.size()  != 0; }
    bool is_vert_output_edges_ready() const { return _vert_output_edges.size() != 0; }

    inline unsigned nb_vertices() const;
public:

    Mesh_attributes();

    // -------------------------------------------------------------------------

    void reset_pointers(const tbx_mesh::Mesh_geometry& geom,
                        const tbx_mesh::Mesh_topology& topo);

    // -------------------------------------------------------------------------

    Mesh_attributes(const Mesh_attributes& mesh_attrs);

    void clear();

    /// Usually cotan weights:
    const std::vector<std::vector<float> >& get_per_edge_weights() const;
    const std::vector<float>& get_sum_edge_weights() const;
    const std::vector< std::vector<tbx::Vec3> >& get_vert_output_edges() const;

    void recompute_normals();
    const std::vector<tbx::Vec3>& get_normals() const { return _normals; }
    std::vector<tbx::Vec3>& normals() { return _normals; }
};


}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_MESH_ATTRIBUTES_HPP
