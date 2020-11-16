#include "operations/relax_grad_descent_optim.hpp"

#include <animation/skinning/skinning_utils.hpp>

#include <toolbox_stl/time_tracker.hpp>
#include <toolbox_maya/utils/progress_window.hpp>
#include <toolbox_maya/utils/sub_mesh.hpp>

#include "operations/arap_svd.hpp"
#include "data/user_data_enum.hpp"
#include "sbr_utils.hpp"
#include "sbr_settings.hpp"

// =============================================================================
namespace skin_brush {
// =============================================================================


// Work in progress, trying to evaluate gradient and the energy for multiple poses.
// When the bone influence w_ij is null at a certain vertex p_i:
// The gradient grad s_i is null so you can possibly optimize this...
// However, the energy E_i is not null though and the value is the same so you have
// to add the value of another existing pose somehow...

// Same for svd rotations, there might be a way to factorize comptuation between
// poses.

// You can also clusterize and then smooth SVD rotations...

User_data::Data_id Relax_grad_descent::_s_cache_id = eRelaxGradDesc;

// =============================================================================

Relax_grad_descent* Relax_grad_descent::fetch_from_cache(Node_swe_cache* cache, const Rig& rig)
{
    typedef Relax_grad_descent Relax;
    Relax* relax = nullptr;
    {
        User_data* user_data = cache->get_user_data();
        relax = user_data->get_data<Relax>(Relax::_s_cache_id);

        if( !relax )
        {
            relax = new Relax(rig);
            user_data->push_data( std::move(tbx::Uptr<Relax>(relax)), Relax::_s_cache_id );
        }
    }

    return relax;
}

// -----------------------------------------------------------------------------

Relax_grad_descent::Relax_grad_descent(const Rig& rig)
    : _is_init(false)
    , _use_extra_links(true)
    , _skel(rig.skel())
    , _mesh(rig.mesh())
    , _rig(rig )
    , _ex(&rig.skel(), &rig.mesh())
    , _augmented_ring_iterator( rig.get_augmented_first_ring() )
    , _augmented_per_edge_weights( rig.get_augmented_per_edge_weights() )
    , _per_edge_cotan_weights( rig.get_per_edge_weights() )
    , _sum_cotan_weights( rig.get_sum_edge_weights() )
    , _vert_output_edges( rig.get_vert_output_edges() )
    , _fixed(rig.nb_vertices())
    , _gradient_elt_buff( rig.skel().get_max_size_bones() )
    , _whole_mesh( _mesh.nb_vertices() )
{
    _step_size = 0.001f;

    init_example_poses();

    // ---------------
    // Allocate memory
    // ---------------
    _M_i.resize( _mesh.nb_vertices() );
    _M_ij.resize( _mesh.nb_vertices() );
    _fixed.resize( _mesh.nb_vertices() );
    _b.resize( _mesh.nb_vertices() );
}

// -----------------------------------------------------------------------------

void Relax_grad_descent::init_example_poses()
{
    Build_examples::build_ex_for_arap_optimization( _ex );

    // Init the number of svd rotation sets according to the number of
    // examples, init _b_buffer for each example as well.
    int nb_verts = _mesh.nb_vertices();
    _svd_rotations.resize( _ex.nb_examples() );
    _b_buffer.resize( _ex.nb_examples() );
    for(unsigned i = 0; i < _ex.nb_examples(); ++i)
    {
        _svd_rotations[i].resize(nb_verts, tbx::Mat3::identity());
        _b_buffer[i].resize(nb_verts);
    }
}

// -----------------------------------------------------------------------------

void Relax_grad_descent::set_use_extra_links(bool state)
{
    if( _use_extra_links == state )
        return;

    _use_extra_links = state;
    _is_init = false;
}

// -----------------------------------------------------------------------------

static
float sparcisity_factor(const std::vector<std::map<int, float> >& weights)
{
    int sparcisity_factor = 0;
    for(unsigned i = 0; i < weights.size(); ++i) {
        sparcisity_factor += int(weights[i].size());
    }
    return float(sparcisity_factor) / float(weights.size());
}

// -----------------------------------------------------------------------------

static int number_of_non_null_weights(const std::map<int, float>& map)
{
    int acc = 0;
    for(const auto& elt : map) {
        if(elt.second > g_prune_threshold)
            acc++;
    }
    return acc;
}

// -----------------------------------------------------------------------------

void Relax_grad_descent::init(const std::vector<std::map<int, float> >& weights)
{
    _current_layout = weights;
    _previous_weight_buff = weights;
    update_sub_meshes(_whole_mesh);
    // Only initialize according to skin weight sizes (and not actual values)
    init_gradient_matrices(weights);
    _is_init = true;
}

// -----------------------------------------------------------------------------

void Relax_grad_descent::update(
        const std::vector<std::map<int, float> >& weights,
        const Sub_mesh& sub_mesh)
{
    mayaAssert(sub_mesh.size() <= _mesh.nb_vertices());
    
    {
        update_sub_meshes(sub_mesh);

        
        update_SVD_rotations(weights);
        

        
        update_gradient_b(weights);
        

    }
    
}

// -----------------------------------------------------------------------------



void Relax_grad_descent::update_gradient_b(const std::vector<std::map<int, float> >& weights)
{
    // Detect if the skin weight layout changed.
    // Input weights must be a subset of our current layout.
    // it's best if input weights were previously pruned so that entries
    // near zero influence do not trigger a layout change.
    bool dirty = false;
    for(unsigned vert_idx : _sub_mesh_plus_neighbors)
    {
        // Copy current skin weights without altering the current layout.
        for( auto& elt : _current_layout[vert_idx]) {
            elt.second = find( weights[vert_idx], elt.first, 0.0f);
        }

        // Check we captured all existing skin weights
        for( const auto& elt : weights[vert_idx])
        {
            if( !exists(current_layout(vert_idx), elt.first) ){
                dirty = true;
            }
        }

        if( ring_iterator().nb_neighbors(vert_idx) != _M_ij[vert_idx].size() )
            dirty = true; // Change in topology
    }

    if(dirty || !_is_init)
    {
        _is_init = false;
        // The input skin weights structure as changed
        // (maybe the user spread some of the influences)
        // We re-compute the data according to the new dimensions.
        _previous_weight_buff = weights;
        _current_layout = weights;
        init_gradient_matrices(weights);
        _is_init = true;
    }

    
    for( unsigned pose_i = 0; pose_i < nb_examples(); ++pose_i )
    {
        //int pose_i = thread_i;
        auto& deformer = get_pose(pose_i);

        for(unsigned vert_idx : sub_mesh())
        {
            Mat3_d rot_i( get_arap_rotation(vert_idx, pose_i) );
            Vec3_d vec_sum_b(0.0);
            for(unsigned n = 0; n < ring_iterator().nb_neighbors(vert_idx); ++n)
            {
                int vert_j = ring_iterator().neighbor_to(vert_idx, n);
                double w = get_per_edge_weights()[vert_idx][n];
                Vec3_d rest_edge( get_output_edge(vert_idx, vert_j, n) );
                Mat3_d rot_j( get_arap_rotation(vert_j, pose_i) );
                vec_sum_b += 2.0 * w * (rot_i+rot_j) * rest_edge;
            }

            int acc = 0;
            for( const auto& elt : current_layout(vert_idx) )
            {
                Vec3_d gradient_dfm( deformer.gradient_deformer(vert_idx, elt.first, weights) );
                _b_buffer[pose_i][vert_idx][acc] = gradient_dfm.dot(vec_sum_b);
                acc++;
            }
        }
    }

    for(unsigned vert_idx : sub_mesh()) {
        size_t nb_weights = current_layout(vert_idx).size();
        _b[vert_idx].clear();
        _b[vert_idx].resize(nb_weights, 0.0);
        for( unsigned pose_i = 0; pose_i < nb_examples(); ++pose_i ) {
            for( unsigned weight_i = 0; weight_i < nb_weights; ++weight_i) {
                _b[vert_idx][weight_i] += _b_buffer[pose_i][vert_idx][weight_i];
            }
        }
    }

    
}

// -----------------------------------------------------------------------------

void Relax_grad_descent::update_sub_meshes(const Sub_mesh& sub_mesh) {
    _sub_mesh = &sub_mesh;
    if(sub_mesh.size() < _mesh.nb_vertices())
        _sub_mesh_plus_neighbors = Sub_mesh(grow_selection(sub_mesh.vertex_list(),
                                                           /*_mesh.topo()*/ring_iterator())); // <- not sure  which topology I should use...
    else
        _sub_mesh_plus_neighbors = sub_mesh;
}

// -----------------------------------------------------------------------------

void Relax_grad_descent::update_SVD_rotations(const std::vector<std::map<int, float> >& weights)
{
    if(true)
    {
        mayaAssert(nb_examples() == _svd_rotations.size());

        for( unsigned i = 0; i < nb_examples(); ++i )
        {
            auto& deformer = get_pose(i);
            compute_SVD_rotations(_svd_rotations[i],
                                  weights,
                                  ring_iterator(),
                                  _mesh.geom()._vertices,
                                  _sub_mesh_plus_neighbors,
                                  get_per_edge_weights(),
                                  deformer);
        }
    }
}

// -----------------------------------------------------------------------------

void Relax_grad_descent::init_gradient_matrices(const std::vector<std::map<int, float> >& weights)
{
    Progress_window window("Brush initialization in progress (Matrix building)", 1+nb_examples(), false /*can't cancel*/);

    


    // --------------------------------
    //  Allocate and Intialize to zero:

    size_t total_number_of_weights = 0;
    //for(unsigned vert_idx : _sub_mesh_plus_neighbors)
    for(unsigned vert_idx = 0; vert_idx < _mesh.nb_vertices(); ++vert_idx)
    {
        // Only optimize when we have at least two influences.
        size_t nb_weights = weights[vert_idx].size();
        total_number_of_weights += nb_weights;
        _fixed[vert_idx]= (number_of_non_null_weights(weights[vert_idx]) < 2);

        for( unsigned pose_i = 0; pose_i < nb_examples(); ++pose_i )
            _b_buffer[pose_i][vert_idx].resize( nb_weights );

        // -------
        _M_i[vert_idx].resize( nb_weights );
        for( unsigned i = 0; i < nb_weights; ++i){
            _M_i[vert_idx][i].clear();
            _M_i[vert_idx][i].resize(nb_weights, 0.0);
        }

        _M_ij[vert_idx].resize(ring_iterator().nb_neighbors(vert_idx));
        for(unsigned n = 0; n < ring_iterator().nb_neighbors(vert_idx); n++)
        {
            int vert_j = ring_iterator().neighbor_to(vert_idx, n);
            _M_ij[vert_idx][n].resize( nb_weights );
            for( unsigned i = 0; i < nb_weights; ++i) {
                _M_ij[vert_idx][n][i].clear();
                _M_ij[vert_idx][n][i].resize(weights[vert_j].size(), 0.0);
            }
        }
    }
    window.add_progess(1);
    _gradient_buffer.resize(total_number_of_weights);

    // -------------------------------
    // Accumulate values for each pose
    for( unsigned i = 0; i < nb_examples(); ++i )
    {
        window.add_progess(1);
        auto& deformer = get_pose(i);

        //for(unsigned vert_idx : sub_mesh())
        for(unsigned vert_idx = 0; vert_idx < _mesh.nb_vertices(); ++vert_idx)
        {
            double sum_cotan_4 = 4.0 * get_sum_edge_weights(vert_idx);
            // Central element:
            int w_i = 0;
            for( const auto& elt_i : weights[vert_idx])
            {
                int w_j = 0;
                Vec3_d gradient_dfm ( deformer.gradient_deformer(vert_idx, elt_i.first, weights) );
                for( const auto& elt_j : weights[vert_idx])
                {
                    Vec3_d s_ij ( deformer.skin_matrix(vert_idx, elt_j.first) );
                    _M_i[vert_idx][w_i][w_j] += gradient_dfm.dot(s_ij) * sum_cotan_4;
                    w_j++;
                }
                w_i++;
            }

            // Neighbors
            for(unsigned n = 0; n < ring_iterator().nb_neighbors(vert_idx); n++)
            {
                int vert_j = ring_iterator().neighbor_to(vert_idx, n);
                double w = get_per_edge_weights()[vert_idx][n];
                int w_i = 0;
                for( const auto& elt_i : weights[vert_idx])
                {
                    int w_j = 0;
                    Vec3_d gradient_dfm ( deformer.gradient_deformer(vert_idx, elt_i.first, weights) );
                    for( const auto& elt_j : weights[vert_j])
                    {
                        Vec3_d s_ij ( deformer.skin_matrix(vert_j, elt_j.first) );
                        _M_ij[vert_idx][n][w_i][w_j] += gradient_dfm.dot(s_ij) * w * 4.0;
                        w_j++;
                    }
                    w_i++;
                }
            }

        } // Per vert_idx
    }// Per pose
    
    window.stop();
}

// -----------------------------------------------------------------------------

Mat3 Relax_grad_descent::get_arap_rotation(int vert_idx, int example_id)
{
    mayaAssert(nb_examples() == _svd_rotations.size());

    if( false )
    {
        // Rotations based on the blending of dual quaternions with current skin weights:
        const std::map<int, float>& weight_map = _skel._weights[vert_idx];

        return get_pose(example_id).get_rotation( anim::find_max_index(weight_map) );
    }
    else
    {
        return _svd_rotations[example_id][vert_idx];
    }
}

// -----------------------------------------------------------------------------

static
double dot_prod(const std::vector<double>& row, const std::map<int, float>& w )
{
    //mayaAssert(row.size() == w.size());
    double res = 0.0;
    int acc = 0;
    for( auto& elt : w){
        res += row[acc] * elt.second;
        acc++;
    }
    return res;
}

// -----------------------------------------------------------------------------

void Relax_grad_descent::gradient_energy(
        unsigned vert_idx,
        const std::vector<std::map<int, float> >& weights,
        std::vector<float>& grad)
{
    // Compute the gradient from the matrix representation:
    // grad_i = line_i(A.x - b) = Mi.x - Mj.x - ... - Mj.x - bi
    for(unsigned w_i = 0; w_i < weights[vert_idx].size(); w_i++)
    {
        double value = dot_prod(_M_i[vert_idx][w_i], weights[vert_idx]);
        for(unsigned n = 0; n < ring_iterator().nb_neighbors(vert_idx); n++)
        {
            int vert_j = ring_iterator().neighbor_to(vert_idx, n);
            value -= dot_prod(_M_ij[vert_idx][n][w_i], weights[vert_j]);
        }

        value -= _b[vert_idx][w_i];

        grad[w_i] = float(value);
    }
}

// -----------------------------------------------------------------------------

float Relax_grad_descent::arap_gradient(
        std::vector<float>& gradient,
        float& delta,
        const std::vector<std::map<int, float> >& weights)
{
    int i = 0;
    float max_norm = 0.0f;
    delta = 0.0f;
    for(unsigned v_idx : sub_mesh())
    {
        if( _fixed[v_idx] ){
            i += int(current_layout(v_idx).size());
            continue;
        }

        gradient_energy(v_idx, weights, _gradient_elt_buff);

        // Here the gradient is actually the directional derivatives along:
        // grad(wi) . v0 = grad(wi) . ( h              , -h/(nb_joints-1), -h/(nb_joints-1), ..., -h/(nb_joints-1) )
        // grad(wi) . v1 = grad(wi) . (-h/(nb_joints-1),  h              , -h/(nb_joints-1), ..., -h/(nb_joints-1) )
        // grad(wi) . v2 = grad(wi) . (-h/(nb_joints-1), -h/(nb_joints-1),  h              , ..., -h/(nb_joints-1) )
        //  ...
        // grad(wi) . v3 = grad(wi) . (-h/(nb_joints-1), -h/(nb_joints-1), -h/(nb_joints-1), ..., h                )

        unsigned nb_weights = unsigned(weights[v_idx].size());
        const float h = 1.0f;
        float mh = (-h/float(nb_weights-1));
        for(unsigned w_i = 0; w_i < nb_weights; w_i++)
        {
            float sum = 0.0f;
            for(unsigned w_j = 0; w_j < nb_weights; w_j++)
            {
                sum += _gradient_elt_buff[w_j] * ((w_i != w_j) ? mh : h);
            }
            gradient[i++] = sum;
            delta += sum*sum;
            max_norm = std::max(std::abs(sum), max_norm);
        }
    }
    delta /= float(sub_mesh().size());
    return max_norm;
}

// -----------------------------------------------------------------------------

float Relax_grad_descent::one_step_relax(const std::vector<Vec2>& constraints)
{
    int i = 0;
    float grad_norm = 0.0f;
    float max_norm = arap_gradient(_gradient_buffer, grad_norm, _current_layout);
    for(unsigned v_idx : sub_mesh())
    {
        // No need to optimize when there is only one or zero influence.
        if( _fixed[v_idx] ){
            i += int(_current_layout[v_idx].size());
            continue;
        }

        for( auto& elt : _current_layout[v_idx] ){
            elt.second = elt.second - (_gradient_buffer[i++]/max_norm) * 0.001f * 0.5f;
            //elt.second = elt.second - (_gradient_buffer[i++]) * 0.000001f;
        }

        anim::clamp(_current_layout[v_idx], 0.0f, 1.0f);
        anim::normalize(_current_layout[v_idx]);
    }
    return grad_norm;
}

// -----------------------------------------------------------------------------

float Relax_grad_descent::arap_gradient_barsilai_borwein(
        std::vector<float>& gradient,
        float& delta,
        const std::vector<std::map<int, float> >& weights)
{
    float bb_step = 0.0f;
    int i = 0;
    delta = 0.0f;
    float grad_norm = 0.0f;
    for(unsigned v_idx : sub_mesh())
    {
        if( _fixed[v_idx] ){
            i += int(weights[v_idx].size());
            continue;
        }

        gradient_energy(v_idx, weights, _gradient_elt_buff);

        unsigned nb_weights = unsigned(weights[v_idx].size());
        const float h = 1.0f;
        float mh = (-h/float(nb_weights-1));

        unsigned w_i = 0;
        //for(unsigned w_i = 0; w_i < nb_weights; w_i++)
        for(const auto& elt : weights[v_idx])
        {
            float sum = 0.0f;
            for(unsigned w_j = 0; w_j < nb_weights; w_j++)
            {
                sum += _gradient_elt_buff[w_j] * ((w_i != w_j) ? mh : h);
            }

            float grad_diff = sum - gradient[i]; // nabla f(x) - nabla f(x_{-1})
            gradient[i] = sum;

            float x_diff = elt.second - _previous_weight_buff[v_idx][elt.first]; // f(x) - f(x_{-1})
            delta += sum*sum;
            bb_step += x_diff * grad_diff;
            grad_norm += grad_diff * grad_diff; // || nabla f(x) - nabla f(x_{-1}) ||^2
            i++;
            w_i++;
        }
    }
    delta /= float(sub_mesh().size());
    return bb_step / grad_norm;
}

// -----------------------------------------------------------------------------

float Relax_grad_descent::one_step_relax_barsilai_borwein(
        const std::vector<Vec2>& constraints)
{
    int i = 0;
    float grad_norm;
    float step_size = arap_gradient_barsilai_borwein(_gradient_buffer, grad_norm, _current_layout);
    //MGlobal::displayInfo(MString("Step_size: ")+step_size);
    for(unsigned v_idx : sub_mesh())
    {
        // No need to optimize when there is only one or zero influence.
        if( _fixed[v_idx] ){
            i += int(_current_layout[v_idx].size());
            continue;
        }

        for( auto& elt : _current_layout[v_idx] ){
            _previous_weight_buff[v_idx][elt.first] = elt.second;
            elt.second = elt.second - _gradient_buffer[i++] * step_size;
        }

        anim::clamp(_current_layout[v_idx], 0.0f, 1.0f);
        anim::normalize(_current_layout[v_idx]);
    }
    return grad_norm;
}

// -----------------------------------------------------------------------------

/// @param[in,out] weights: skinning weights to be smoothed.
void relax_grad_descent_optim(
        Node_swe_cache* cache,
        std::vector<std::map<int, float> >& weights,
        const Rig& rig,        
        const std::vector<tbx::Vec2>& constraints,
        bool extra_links,
        const Sub_mesh& sub_mesh)
{
#if 1

    //You might benefit from spreading the influence of everybones (even if it's only set to zero)

    int intera = 3;
    int total = intera*10*2;

    for(unsigned vert_idx = 0; vert_idx < rig.nb_vertices(); ++vert_idx) {
        anim::prune( weights[vert_idx], g_prune_threshold);
    }

    Relax_grad_descent* relax = Relax_grad_descent::fetch_from_cache(cache, rig);
    relax->set_use_extra_links(extra_links);
    if( !relax->is_init() ) {
        relax->init(weights);
    }

    Progress_window window("Skin Weight Relaxation (GD)", total);
    window.set_delay(1.5/*seconds*/);
    
    {

        relax->update(weights, sub_mesh);

        
        relax->one_step_relax(constraints);
        

        
        //MGlobal::displayInfo(MString("Nb iters: ") + total);
        for(int iter = 0; iter < total; iter++)
        {
            if(window.is_canceled())
                break;

            float grad_norm = 1.0f;
            if(sub_mesh.size() == rig.nb_vertices())
            {
                // When optimizing for the whole mesh we can use bigger time steps: (otherwize it's unstable)
                grad_norm = relax->one_step_relax_barsilai_borwein(constraints);
            }
            else
            {
                grad_norm = relax->one_step_relax(constraints);
            }

            if(grad_norm < 0.00001f){
                //MGlobal::displayInfo("Fully converged, Nothing to relax anymore");
                break;
            }

            // TODO: slightly smoothing (without spreading) to stabilize convergence)

            window.add_progess(1);

        }// END nb_iter
        window.stop();
        relax->fetch_skin_weights( weights );

        // TODO: possibly a final skin weight filtering and then pruning...
        

    }
    

#endif
}

}// END skin_brush Namespace ===================================================

