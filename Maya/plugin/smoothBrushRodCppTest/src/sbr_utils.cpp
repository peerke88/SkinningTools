#include "sbr_utils.hpp"

#include <toolbox_maya/utils/maya_attributes.hpp>
#include <toolbox_maya/utils/maya_error.hpp>
#include <toolbox_maya/utils/sub_mesh.hpp>
#include <toolbox_maya/utils/find_node.hpp>
#include <toolbox_maya/utils/maya_transform.hpp>
#include <toolbox_maya/utils/maya_mfnmesh_utils.hpp>
#include <toolbox_maya/utils/maya_dependency_nodes.hpp>
#include <toolbox_maya/utils/maya_dag_nodes.hpp>
#include <toolbox_maya/data/maya_mesh.hpp>
#include <toolbox_maya/data/maya_skin_weights.hpp>

#include <toolbox_stl/time_tracker.hpp>
#include <toolbox_stl/vector.hpp>
#include <toolbox_mesh/iterators/first_ring_it.hpp>
#include <toolbox_mesh/mesh_geometry.hpp>
#include <toolbox_mesh/mesh_topology.hpp>
// ---
#include "maya_nodes/node_swe_cache.hpp"
#include "sbr_settings.hpp"
#include "data/rig.hpp"
// ---
#include <maya/MObject.h>

// =============================================================================
namespace skin_brush {
// =============================================================================

// TODO: delete this unoptimal function.
void normalize(std::vector<std::map<int, float> >& weights,
               std::vector<std::map<int, float> >& buffer_weights,
               const Sub_mesh& sub_mesh)
{
    std::map<int, float>::iterator it;
    // Eliminate near zero weigths and normalize :
    for(unsigned v_idx : sub_mesh)
    {
        std::map<int, float>& map = weights[v_idx];
        float sum = 0.f;
        for(it = map.begin(); it != map.end(); ++it)
        {
            float w = it->second;
            if(w > g_prune_threshold)
            {
                buffer_weights[v_idx][it->first] = w;
                sum += w;
            }
        }

        weights[v_idx].clear();

        std::map<int, float>& n_map = buffer_weights[v_idx];
        for(it = n_map.begin(); it != n_map.end(); ++it)
        {
            float w = it->second / sum;
            if(w > g_prune_threshold)
                weights[v_idx][it->first] = w;
        }

    }
}

//TODO: use this instead:
void normalize_sub(std::vector<std::map<int, float> >& weights,
                   std::vector<std::map<int, float> >& sub_buffer_weights,
                   const Sub_mesh& sub_mesh)
{
    std::map<int, float>::iterator it;
    // Eliminate near zero weigths and normalize :
    int sub_idx = 0;
    for(unsigned v_idx : sub_mesh)
    {
        std::map<int, float>& map = weights[v_idx];
        float sum = 0.f;
        for(it = map.begin(); it != map.end(); ++it)
        {
            float w = it->second;
            if(w > g_prune_threshold)
            {
                sub_buffer_weights[sub_idx][it->first] = w;
                sum += w;
            }
        }

        weights[v_idx].clear();

        std::map<int, float>& n_map = sub_buffer_weights[sub_idx];
        for(it = n_map.begin(); it != n_map.end(); ++it)
        {
            float w = it->second / sum;
            if(w > g_prune_threshold)
                weights[v_idx][it->first] = w;
        }

        ++sub_idx;
    }
}

// -----------------------------------------------------------------------------

void normalize_sub(std::vector<std::map<int, float> >& weights,
                   const std::vector<bool>& locked_joints,
                   const Sub_mesh& sub_mesh)
{
    std::vector< std::pair<int,float> > vertex_weight;
    vertex_weight.reserve(100);
    // Eliminate near zero weigths and normalize :
    for(unsigned v_idx : sub_mesh)
    {
        vertex_weight.clear();
        float sum = 0.f;
        float sum_locked = 0.f;

        const std::vector<bool>& locked_bones = locked_joints;

        for(const auto& elt : weights[v_idx])
        {
            float w = elt.second;
            vertex_weight.push_back( std::make_pair(elt.first, w) );

            if( locked_bones[elt.first] )
                sum_locked += w;
            else
                sum += w;
        }

        weights[v_idx].clear();

        for(const auto& elt : vertex_weight)
        {
            if( locked_bones[elt.first] )
            {
                weights[v_idx][elt.first] = elt.second;
            }
            else
            {
                float w = (elt.second / sum) * (1.0f - sum_locked);
                if(w > g_prune_threshold)
                    weights[v_idx][elt.first] = w;
            }
        }
    }
}

// -----------------------------------------------------------------------------

std::vector<int> grow_selection(const std::vector<int>& selection,
                                const tbx_mesh::First_ring_it& connectivity,
                                int level)
{
    std::vector<int> new_selection = selection;
    std::vector<int> new_vertices;

    for(int l = 0; l < level; ++l){
        new_vertices.clear();
        for (unsigned i = 0; i < new_selection.size(); ++i)
        {
            unsigned v_idx = new_selection[i];
            for(int index_neigh : connectivity.first_ring_at(v_idx))
            {
                if( !tbx::exists(new_vertices, index_neigh) &&
                    !tbx::exists(new_selection, index_neigh) )
                {
                    new_vertices.push_back( index_neigh );
                }
            }
        }

        for( int idx : new_vertices)
            new_selection.push_back( idx );
    }

    tbx_assert( !has_duplicates(new_selection) );
    return new_selection;
}

// -----------------------------------------------------------------------------

void get_maya_selection(std::vector<int>& vertex_list,
                        MObject skin_cluster)
{
    MObject mesh_shape;
    if( !find_dfm_output_deformed_mesh(skin_cluster, mesh_shape) ){
        mayaAbort("Can't find output mesh");
    }

    if(true)
    {

        vertex_list.clear();
        get_selection_and_convert_to_vertex(vertex_list, mesh_shape);

    }
    else
        tbx_maya::get_selected_vertices(vertex_list, mesh_shape);    
}

// -----------------------------------------------------------------------------

void build_selection(
        std::vector<int>& vertex_list,
        MObject skin_cluster,
        const std::vector<Brush>& brush_mask)
{
    //NOTE: for now we ignore brush weight values

    vertex_list.clear();
    vertex_list.reserve( brush_mask.size() );
    for(const Brush& b : brush_mask)
        vertex_list.push_back(b._v_idx);


    if( vertex_list.size() <= 0)
    {
        get_maya_selection(vertex_list, skin_cluster);
    }

    tbx_assert( !has_duplicates(vertex_list) );

    Node_swe_cache* cache = nullptr;
    if( (cache = find_cache(skin_cluster, false)) )
    {
        auto vert_list = grow_selection(vertex_list, cache->get_mesh()->topo().first_ring(), 30 );
        skin_weights::get_subset_through_mplug( skin_cluster, vert_list, cache->get_skeleton()->_weights);
    }

}

// -----------------------------------------------------------------------------

Node_swe_cache* find_cache(MObject& skin_cluster, bool update)
{
    Node_swe_cache* cache = nullptr;
    if( !Node_swe_cache::find_valid_cache(skin_cluster, cache) ) {
        Node_swe_cache::destroy_from_skin_cluster( skin_cluster );
        return nullptr;
    }
    else if( update ) {

            cache->update();

    }

    return cache;
}

// -----------------------------------------------------------------------------

MString get_joint_name(bone::Id id, const Node_swe_cache* cache)
{
    return get_name(cache->get_skeleton()->get_dag_path(id));
}


}// END skin_brush Namespace ========================================
