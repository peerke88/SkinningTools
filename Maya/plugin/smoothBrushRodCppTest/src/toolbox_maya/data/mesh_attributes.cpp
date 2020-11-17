#include "toolbox_maya/data/mesh_attributes.hpp"

#include <toolbox_mesh/mesh_geometry.hpp>
#include <toolbox_mesh/mesh_topology.hpp>
#include <toolbox_mesh/mesh_utils.hpp>

using namespace tbx;

// =============================================================================
namespace tbx_maya {
// =============================================================================

unsigned Mesh_attributes::nb_vertices() const { return (unsigned)_geom->nb_vertices(); }

// -----------------------------------------------------------------------------

Mesh_attributes::Mesh_attributes()
    : _geom(nullptr),
      _topo(nullptr)
{

}

// -----------------------------------------------------------------------------

void Mesh_attributes::reset_pointers(const tbx_mesh::Mesh_geometry& geom,
                                     const tbx_mesh::Mesh_topology& topo)
{
    _geom = &geom;
    _topo = &topo;
}

// -----------------------------------------------------------------------------

Mesh_attributes::Mesh_attributes(const Mesh_attributes& mesh_attrs)
{
    _geom = nullptr;
    _topo = nullptr;

    // Copy mutable (cached) attribute only if they were previously computed:
    if( mesh_attrs.is_per_edge_weights_ready() ){
        _per_edge_weights = mesh_attrs._per_edge_weights;
    }

    if( mesh_attrs.is_sum_edge_weights_ready() ){
        _sum_edge_weights = mesh_attrs._sum_edge_weights;
    }

    if( mesh_attrs.is_vert_output_edges_ready() ){
        _vert_output_edges = mesh_attrs._vert_output_edges;
    }

    _normals = mesh_attrs._normals;
}

// -----------------------------------------------------------------------------

void Mesh_attributes::clear(){
    _per_edge_weights.clear();
    _vert_output_edges.clear();
    _sum_edge_weights.clear();
    _normals.clear();
}

// -----------------------------------------------------------------------------

const std::vector<std::vector<float> >& Mesh_attributes::get_per_edge_weights() const
{
    if( !is_per_edge_weights_ready() )
    {
        tbx_mesh::mesh_utils::laplacian_positive_cotan_weights(*_topo, _per_edge_weights);

        //tbx_mesh::mesh_utils::laplacian_cotan_weights(*_geom, *_topo, _per_edge_weights);
        //tbx_mesh::mesh_utils::mean_value_coordinates_weight(*_geom, *_topo, _normals, _per_edge_weights);
        //tbx_mesh::mesh_utils::uniform_weights(*_geom, (*_topo), _per_edge_weights);
    }

    return _per_edge_weights;
}

// -----------------------------------------------------------------------------

const std::vector<float>& Mesh_attributes::get_sum_edge_weights() const
{
    if( !is_sum_edge_weights_ready() )
    {
        _sum_edge_weights.resize( nb_vertices() );
        for(unsigned vert_idx = 0; vert_idx < nb_vertices(); ++vert_idx)
        {
            double sum_cotan = 0.0;
            for(unsigned n = 0; n < _topo->nb_neighbors(vert_idx); ++n) {
                double w = get_per_edge_weights()[vert_idx][n];
                sum_cotan += w;
            }
            _sum_edge_weights[vert_idx] = float(sum_cotan);
        }
    }

    return _sum_edge_weights;
}

// -----------------------------------------------------------------------------

const std::vector<std::vector<tbx::Vec3> >& Mesh_attributes::get_vert_output_edges() const
{
    if( !is_vert_output_edges_ready() )
    {
        int nb_verts = nb_vertices();
        _vert_output_edges.resize(nb_verts);
        for(int vert_idx = 0; vert_idx < nb_verts; ++vert_idx)
        {
            tbx::Vec3 pos = _geom->vertex(vert_idx);
            int nb_neigh = (int)_topo->nb_neighbors(vert_idx);
            _vert_output_edges[vert_idx].resize(nb_neigh);
            for(int n = 0; n < nb_neigh; n++)
            {
                int curr = _topo->neighbor_to(vert_idx, n);
                tbx::Vec3 edge = pos - _geom->vertex(curr);
                _vert_output_edges[vert_idx][n] = edge;
            }
        }
    }

    return _vert_output_edges;
}

// -----------------------------------------------------------------------------

void Mesh_attributes::recompute_normals()
{
    tbx_mesh::mesh_utils::normals(*_geom, _normals);
}

}// END tbx_maya Namespace =====================================================
