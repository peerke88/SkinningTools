#include "operations/smoothing.hpp"

#include <toolbox_stl/map.hpp>
#include <toolbox_mesh/mesh_utils.hpp>
#include <toolbox_mesh/iterators/first_ring_it.hpp>
#include <toolbox_maya/utils/progress_window.hpp>
#include <animation/skinning/skinning_utils.hpp>

#include <toolbox_maya/utils/sub_mesh.hpp>

#include "data/rig.hpp"
#include "sbr_utils.hpp"
#include "sbr_settings.hpp"

// =============================================================================
namespace skin_brush {
// =============================================================================

static bool is_fixed_value(const std::vector<tbx::Vec2>& constraints, float v)
{
    for(Vec2 range : constraints) {
        if(v >= range.x && v <= range.y)
            return true;
    }
    return false;
}

// -----------------------------------------------------------------------------

void init_per_edge_weights(
        std::vector< std::vector<float> >& per_edge_weights,
        Smoothing_type type,
        const Rig& rig,
        const Sub_mesh& sub_mesh
        )
{
    per_edge_weights.resize( sub_mesh.size() );
    const tbx_mesh::Mesh_topology& topo = rig.topo();

    switch(type){
    case(eEDGE_LENGTH):
    {
        int sub_index = 0;
        for(unsigned vertex_i : sub_mesh)
        {
            Vec3 pos_i = rig.vertex(vertex_i);

            unsigned nb_neigh = topo.nb_neighbors(vertex_i);
            per_edge_weights[sub_index].resize(nb_neigh);

            float total_length = 0.0f;
            for(unsigned edge_j = 0; edge_j < nb_neigh; edge_j++)
            {
                int vertex_j = topo.neighbor_to(vertex_i, edge_j);
                Vec3 pos_j = rig.vertex(vertex_j);

                float len = (pos_i - pos_j).norm();
                total_length += len;
                per_edge_weights[sub_index][edge_j] = len;
            }

            for(unsigned edge_j = 0; edge_j < nb_neigh; edge_j++)
            {
                per_edge_weights[sub_index][edge_j] = total_length/per_edge_weights[sub_index][edge_j];
            }
            ++sub_index;
        }
    }break;
    case(eCOTAN):
    {
        int sub_index = 0;
        for(unsigned vertex_i : sub_mesh)
        {
            unsigned nb_neigh = topo.nb_neighbors(vertex_i);
            per_edge_weights[sub_index].resize(nb_neigh);
            float total_weights = 0.0f;
            for(unsigned edge_j = 0; edge_j < nb_neigh; edge_j++)
            {
                float wij = mesh_utils::laplacian_cotan_weight(rig.geom(), rig.topo(), vertex_i, edge_j);

                per_edge_weights[sub_index][edge_j] = wij;
                total_weights += wij;
            }

            ++sub_index;
        }
    }break;
    case(eMIXED_LINK):
    {
        First_ring_it augmented_ring( rig.get_augmented_first_ring() );

        int sub_index = 0;
        for(unsigned vertex_i : sub_mesh)
        {
            unsigned nb_neigh = augmented_ring.nb_neighbors(vertex_i);
            per_edge_weights[sub_index].resize(nb_neigh);

            if( rig.get_extra_vertex_links()[vertex_i].size() > 0)
            {
                Vec3 pos_i = rig.vertex(vertex_i);

                float total_length = 0.0f;
                for(unsigned edge_j = 0; edge_j < nb_neigh; edge_j++)
                {
                    int vertex_j = augmented_ring.neighbor_to(vertex_i, edge_j);
                    Vec3 pos_j = rig.vertex(vertex_j);

                    float len = (pos_i - pos_j).norm();

                    if(len < 1e-6f ){
                        len = 1e-6f;
                        //mayaWarning(MString("Warning: very short edge length at vertex: ")+vertex_i+" you should weld that vertices for best results");
                    }

                    total_length += len;
                    per_edge_weights[sub_index][edge_j] = len;

                }

                for(unsigned edge_j = 0; edge_j < nb_neigh; edge_j++)
                {
                    float len = per_edge_weights[sub_index][edge_j];
                    per_edge_weights[sub_index][edge_j] = (total_length/len);
                }
            }
            else
            {
                // Use cotan
                for(unsigned edge_j = 0; edge_j < nb_neigh; edge_j++)
                {
                    float wij = mesh_utils::laplacian_cotan_weight(rig.geom(), rig.topo(), vertex_i, edge_j);
                    per_edge_weights[sub_index][edge_j] = wij;
                }

            }
            ++sub_index;
        }
    }break;
    case(eUNIFORM):
    default:
    {
        int sub_index = 0;
        for(unsigned vertex_i : sub_mesh)
        {
            unsigned nb_neigh = topo.nb_neighbors(vertex_i);
            per_edge_weights[sub_index].resize(nb_neigh);
            for(unsigned edge_j = 0; edge_j < nb_neigh; edge_j++)
                per_edge_weights[sub_index][edge_j] = 1.0f;

            ++sub_index;
        }
    }break;
    }
}


// -----------------------------------------------------------------------------

/// @param[in,out] weights: skinning weights to be smoothed.
void smooth_skin_weights_all_joints(std::vector<std::map<int, float> >& weights,
                                    const Rig& rig,
                                    int nb_bones,                                    
                                    const std::vector<tbx::Vec2>& constraints,
                                    int max_influences,
                                    const std::vector<bool>& locked_joints,
                                    const Sub_mesh& sub_mesh,
                                    Smoothing_type type)
{
    Progress_window window("Smoothing", 3+1);

    //type = eEDGE_LENGTH;

    float t = 1.0f;
    if( type == eCOTAN || type == eMIXED_LINK)
        t = t*0.9f; //< otherwise the convergence is not stable for cotan weights

    //TODO instead of using the neighboors from the triangulated mesh use directly maya api to get neighboors from quads or other polys.

    std::vector< std::vector<float> > per_edge_weights;
    init_per_edge_weights(per_edge_weights, type, rig, sub_mesh);
    window.add_progess();
    First_ring_it first_ring( type == eMIXED_LINK ? rig.get_augmented_first_ring() : rig.topo().first_ring());

    // ---------------------------------
    // Diffuse weights:
    // ---------------------------------

    std::vector<std::map<int, float> > new_weights( sub_mesh.size() );
    std::vector<float> per_bone_weight_sum(nb_bones, 0.0f);

    for(int iter = 0; iter < 3; iter++)
    {
        if( window.is_canceled() )
            break;
        // For all vertices
        int sub_index = 0;
        for(unsigned vertex_i : sub_mesh)
        {
            tbx::fill(per_bone_weight_sum, 0.0f);

            // For all vertices' neighborhoods sum the weight of each bone
            unsigned nb_neigh = first_ring.nb_neighbors(vertex_i);
            float sum_wij = 0.0f;
            for(unsigned edge_j = 0; edge_j < nb_neigh; edge_j++)
            {
                int vertex_j = first_ring.neighbor_to(vertex_i, edge_j);

                float wij = per_edge_weights[sub_index][edge_j];
                sum_wij += wij;
                for(const auto& elt : weights[vertex_j])
                {
                    per_bone_weight_sum[elt.first] += elt.second * wij;
                }
            }

            const std::vector<bool>& is_joint_locked = locked_joints;

            for(int j = 0; j < (int)per_bone_weight_sum.size(); j++)
            {
                float skin_weight = tbx::find(weights[vertex_i], j, 0.f);

                if( !is_fixed_value(constraints, skin_weight) && !is_joint_locked[j])
                {
                    float new_weight = (per_bone_weight_sum[j] / sum_wij);
                    skin_weight = skin_weight * (1.0f - t) + new_weight * t;
                }

                if(skin_weight > g_prune_threshold)
                    new_weights[sub_index][j] = skin_weight;
            }

            if( max_influences >= 1 )
            {
                // Enforce max influence:
                //size_t previous_size = weights[vertex_i].size();
                size_t current_size  = new_weights[sub_index].size();
                if( /*previous_size != current_size && */ current_size > max_influences)
                    // Reset smoothing process because we reached max influences
                    new_weights[sub_index] = weights[vertex_i];
            }

            ++sub_index;
        }// END nb_vert

        sub_index = 0;
        for(unsigned v_idx : sub_mesh)
        {

            weights[v_idx].swap(new_weights[sub_index]);

            new_weights[sub_index].clear();
            ++sub_index;
        }

        window.add_progess();

    }// END nb_iter

    normalize_sub(weights, locked_joints, sub_mesh);
}

// -----------------------------------------------------------------------------

void smooth_skin_weights_all_joints(std::vector<std::map<int, float> >& weights,
                                    const Rig& rig,                                    
                                    const std::vector<tbx::Vec2>& constraints,
                                    int max_influences,
                                    const std::vector<bool>& locked_joints,
                                    const Sub_mesh& sub_mesh,
                                    Smoothing_type type)
{
    //Timer time1;
    //time1.start();
    smooth_skin_weights_all_joints(weights,
                                   rig,
                                   unsigned(rig.skel().get_max_size_bones()),                                   
                                   constraints,
                                   max_influences,
                                   locked_joints,
                                   sub_mesh,
                                   type);
}

}// END skin_brush Namespace ========================================
