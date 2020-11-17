#ifndef RELAX_GRAD_DESCENT_OPTIM_HPP
#define RELAX_GRAD_DESCENT_OPTIM_HPP

#include <toolbox_maya/data/maya_skeleton.hpp>
#include <toolbox_mesh/iterators/first_ring_it.hpp>

#include "maya_nodes/node_swe_cache.hpp"
#include "data/rig.hpp"
#include "data/build_examples.hpp"
#include "data/skin_deformer.hpp"
#include "data/user_data.hpp"


// Forward declaration ---------------------------------------------------------
namespace tbx_maya {
class Sub_mesh;
}
// Forward declaration end -----------------------------------------------------

// =============================================================================
namespace skin_brush {
// =============================================================================

/**
    Gradient descent (GD) of the original ARAP,
    the gradient is projected to preserve skin weights normalization
    (we march along directional derivatives that preserve the norm when used in
    GD)

    Gradient is computed with the analytical formula.

    We optimize for several poses (c.f Build_examples)

    Note: Slower than a single pose, (SVD rotations must be computed
    for each pose).

    Note: this version cache some computations at the initialization stage
    to accelerate the computation of the gradient (this minimize slow down
    related to the number of pose examples)

    We use the matrix representation Ax = b to compute the gradient
    grad_i = line_i(Ax - b)
    Because A can be precomputed the computation of Ax is independant to
    the number of poses and the SVD matrices.
    b is still dependant on the number of poses and needs SVD to be recomputed.
    (but lighter to compute than A)
*/
void relax_grad_descent_optim(
        Node_swe_cache* cache,
        std::vector<std::map<int, float> >& weights,
        const Rig& rig,        
        const std::vector<tbx::Vec2>& constraints,
        bool extra_links,
        const Sub_mesh& sub_mesh);

// =============================================================================
// =============================================================================
// =============================================================================

class Relax_grad_descent : public User_data::Data {
public:

    static User_data::Data_id _s_cache_id;

private:
    bool _is_init; // true when init() was called;
    bool _use_extra_links; // when true we relax using the augmented topology and mixed edge weights.

    const Maya_skeleton& _skel;
    const Maya_mesh& _mesh;
    const Rig& _rig;
    const First_ring_it _augmented_ring_iterator;
    const Sub_mesh* _sub_mesh;

    float _step_size; /// < current step size of the gradient descent;

    /// Fixed skin weights (we don't optimize those they stay as is)
    std::vector<bool> _fixed;

    const Sub_mesh& sub_mesh() const { return *_sub_mesh; }
    /// _sub_mesh plus direct neighbors
    /** @code
                    +-------+
                    |\     /|
        +---+       | +---+ |
        |\ /|       | |\ /| |
        | + | ==>   | | + | |
        |/ \|       | |/ \| |
        +---+       | +---+ |
                    |/     \|
                    +-------+
        @endcode
    */
    Sub_mesh _sub_mesh_plus_neighbors;

    Sub_mesh _whole_mesh;

    // ---------------------
    // Cache
    //-----------------------

    /// Gradient value of the skin weights. (flat layout)
    /// Array index:     [0]    [1]     [2]     [3]     [4]          [5]           [6]    ...
    /// Skin weights: {{w_0_0, w_0_1, w_0_2}, {w_1_5, w_1_8}, {w_(vertId)_(boneId), ...}, ... }
    std::vector<float> _gradient_buffer;

    /// Stores a set of skin weights for a single vertex
    /// _gradient_elt_buff.size() == maximum number of bones.
    std::vector<float> _gradient_elt_buff;

    std::vector<std::map<int, float> > _previous_weight_buff;
    std::vector<std::map<int, float> > _current_layout;

    /// store intermediate results of _b for each pose
    /// _b_buffer[pose_i][vertex_idx][ith_weith] = value of b for a single pose
    std::vector< std::vector< std::vector<double> > > _b_buffer;

    /// List of svd rotation for each pose and each vertex.
    /// _svd_rotations[pose_i][vertex_i]
    std::vector<std::vector<tbx::Mat3>> _svd_rotations;

    // ---------------------------------------------------------------
    /// Matrix data A.x = b <=> M_i.x - M_ij.x - ... - M_ij.x - b_i.
    /// Sparse representation of A.
    // ---------------------------------------------------------------

    /// Right hand side of Ax = b
    std::vector< std::vector<double> > _b; // [vertex_idx][ith_weight]
    std::vector< std::vector< std::vector<double> > > _M_i; // [vertex_idx][ith_weight_row][ith_weight_column]
    std::vector< std::vector< std::vector< std::vector<double> > > > _M_ij; // [vertex_idx][jth_neighbor][ith_weight_row][jth_weight_column]

    // ---------------------------------------------------------------

    Build_examples _ex;

    // -----------------------------
    // Externally precomputed data
    // -----------------------------

    const std::vector< std::vector<float> >& _augmented_per_edge_weights;
    //
    const std::vector< std::vector<float> >& _per_edge_cotan_weights;
    const std::vector<float>& _sum_cotan_weights;
    const std::vector< std::vector<tbx::Vec3> >& _vert_output_edges;
    //

    First_ring_it ring_iterator() const {
        if(_use_extra_links)
            return _augmented_ring_iterator;
        else
            return First_ring_it( _rig.topo() );
    }

    const std::vector< std::vector<float> >& get_per_edge_weights() const {
        if( _use_extra_links )
            return _augmented_per_edge_weights;
        else
            return _per_edge_cotan_weights;
    }

    tbx::Vec3 get_output_edge(tbx_mesh::Vert_idx vert_i, tbx_mesh::Vert_idx vert_j, int edge_j) const {
        if(_use_extra_links){
            return _mesh.vertex(vert_i) - _mesh.vertex( vert_j );
        }else{
            return _vert_output_edges[vert_i][edge_j];
        }

    }

    float get_sum_edge_weights(tbx_mesh::Vert_idx id) const
    {
        if(_use_extra_links)
        {
            float sum = 0.0f;
            for(unsigned j = 0; j < get_per_edge_weights()[id].size(); ++j)  {
                sum += get_per_edge_weights()[id][j];
            }
            return sum;
        }
        else
            return _sum_cotan_weights[id];
    }

    //--------------------------------------------------------------------------

    unsigned nb_examples(){ return _ex.nb_examples(); }
    const Skin_deformer& get_pose(int pose_index) const { return _ex.get_deformer(pose_index); }

    // =========================================================================

public:

    bool is_init() const { return _is_init; }

    /// Fetch a unique (singleton) instance from the cache,
    /// User must take care of initialization if not initialized
    /// - (Arap_relax_grad_descent::init())
    /// - (Arap_relax_grad_descent::is_init())
    static Relax_grad_descent* fetch_from_cache(Node_swe_cache* cache, const Rig& rig);

    /// Allocate and sample skeleton poses
    Relax_grad_descent(const Rig &rig);

    /// Precompute various data based on the skin weight layout and sampled poses
    /// Typically called once after constructor. Once init() is called the skin
    /// weight layout is saved and relaxation operates only on the current layout.
    /// Even if skin weights area of influences decreases during relaxation we
    /// still operate on the same influence area.
    ///
    /// If you call init() again in between a few relaxation steps this might
    /// accelerate the process in the case that skin weights influence area
    /// gets smaller.
    ///
    /// (Note that init() is called automatically from update() when skin weight
    /// layout area grows)
    ///
    /// @note this is a quite heavy pre-computation involving quite a few memory
    /// allocation.
    void init(const std::vector<std::map<int, float> >& weights);

    /// update() is typically called before gradient descent steps
    /// (and possibly in-between)
    ///
    /// Note that if the skin weight layout changes
    /// (only when the area of influence grows) it will trigger heavy
    /// computation overhead
    ///
    /// You can prune "weights" to avoid skin weights with null values
    /// to be mistaken with a growth of the influence area.
    void update(const std::vector<std::map<int, float> >& weights,
                const Sub_mesh& sub_mesh);

    void set_use_extra_links(bool state);

    inline void gradient_energy(
            unsigned vert_idx,
            const std::vector<std::map<int, float> >& weights,
            std::vector<float>& grad);


    float one_step_relax(const std::vector<tbx::Vec2>& constraints);


    /// Apply one step of gradient descent using the barsilai borwein method
    /// (helps to march along big gradient steps while being somewhat stable)
    float one_step_relax_barsilai_borwein(
            const std::vector<tbx::Vec2>& constraints);


    void fetch_skin_weights(std::vector<std::map<int, float> >& weights){
        for(unsigned v_idx : sub_mesh())
            weights[v_idx] = _current_layout[v_idx];
    }

    /// Use those weights as the current layout of skin weights
    const std::vector<std::map<int, float> >& current_layout() const {
        return _current_layout;
    }

private:
    /// @param[out] gradient : this vector is the flat version of the skin weights
    /// i.e. instead of having gradient[vert_idx][bone_id] the layout look like:
    /// { w_0_0, w_0_1, w_0_2, w_1_5, w_1_8, w_(vertId)_(boneId), ... }
    /// @param[out] delta : squared norm of the gradient.
    /// @return the maximum value in 'gradient'
    float arap_gradient(std::vector<float>& gradient,
                        float& delta,
                        const std::vector<std::map<int, float> >& weights);


    /// @param[out] gradient : this vector is the flat version of the skin weights
    /// i.e. instead of having gradient[vert_idx][bone_id] the layout look like:
    /// { w_0_0, w_0_1, w_0_2, w_1_5, w_1_8, w_(vertId)_(boneId), ... }
    /// @param[out] delta : squared norm of the gradient.
    float arap_gradient_barsilai_borwein(
            std::vector<float>& gradient,
            float& delta,
            const std::vector<std::map<int, float> >& weights);

    inline const std::map<int, float>& current_layout(unsigned vert_idx) const
    {
        return _current_layout[vert_idx];
    }

    void update_sub_meshes(const Sub_mesh& sub_mesh);

    void update_gradient_b(const std::vector<std::map<int, float> >& weights);

    void init_example_poses();

    void update_SVD_rotations(const std::vector<std::map<int, float> >& weights);

    void init_gradient_matrices(const std::vector<std::map<int, float> >& weights);

    inline Mat3 get_arap_rotation(int vert_idx, int example_id);

};

// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------




}// END skin_brush Namespace ========================================


#endif // RELAX_GRAD_DESCENT_OPTIM_HPP
