#ifndef SKIN_DEFORMER_HPP
#define SKIN_DEFORMER_HPP

#include <animation/skinning/dual_quaternion_blending.hpp>
#include <toolbox_maths/dual_quat.hpp>
#include <toolbox_maya/data/maya_skeleton.hpp>
#include <toolbox_maya/data/maya_mesh.hpp>
#include <toolbox_mesh/mesh_geometry.hpp>

// Forward declaration ---------------------------------------------------------
namespace skin_brush {
}
// Forward declaration end -----------------------------------------------------

// =============================================================================
namespace skin_brush {
// =============================================================================

/**
    @brief Simulate a skin deformer (linear blending etc.)
    for our relaxation operators
*/
class Skin_deformer {
public:
    std::vector<bone::Id> _roots;
    std::vector< std::vector<bone::Id> > _sons;
    std::vector<tbx::Transfo> _bind_pose; // B_j
    std::vector<tbx::Transfo> _bind_local; // L_j
    std::vector<tbx::Transfo> _skinning_transfos; // T_j
    std::vector<tbx::Transfo> _user_local; // U_j
    std::vector<tbx::Dual_quat> _skinning_dqs;

    /// false when _skinning_transfos is not up to date
    bool _dirty;

    /// Rest pose mesh to access rest pose vertices.
    const Maya_mesh& _mesh;
public:

    unsigned nb_roots() const { return (unsigned)_roots.size(); }
    bone::Id root(int n) const { return _roots[n]; }
    const std::vector<bone::Id>& sons(bone::Id id) const { return _sons[id]; }

    // -------------------------------------------------------------------------

    Skin_deformer(const Maya_skeleton& skel, const Maya_mesh& mesh)
        : _dirty(true)
        , _mesh( mesh )
    {
        _skinning_transfos.resize( skel.get_max_size_bones() );
        _skinning_dqs.     resize( skel.get_max_size_bones() );
        _bind_pose.        resize( skel.get_max_size_bones() );
        _bind_local.       resize( skel.get_max_size_bones() );
        _user_local.       resize( skel.get_max_size_bones() );
        _sons.             resize( skel.get_max_size_bones() );

        for( const tbx::Bone& bone : skel)
        {
            bone::Id bone_id = bone.id();
            bone::Id parent_id = skel.parent(bone_id);

            tbx::Transfo bind_local = skel.get_bind_local(bone_id);
            _bind_local[bone_id] = bind_local;

            // Check linear blending cheat sheet:
            // Ulj = (W_p(j) . L_j)^-1 . W_j
            // http://rodolphe-vaillant.fr/?e=77
            _user_local[bone_id] = tbx::Transfo::identity();
            if( parent_id != -1)
                _user_local[bone_id] = (skel.get_joint_transfo(parent_id) * bind_local).fast_inverse() * skel.get_joint_transfo(bone_id);
            else
                _user_local[bone_id] = bind_local.fast_inverse() * skel.get_joint_transfo(bone_id);

            _bind_pose[bone_id] = skel.get_bind_global(bone_id);
            _sons[bone_id] = skel.children(bone_id);
        }
        _roots = skel.compute_root_joints();
        //compute your skinning transfo here and compare with the above.
        compute_skinning_transfo(_skinning_transfos);
    }

    // -------------------------------------------------------------------------

    inline tbx::Vec3 deform(int vertex_id, const std::map<int, float>& bones) const
    {
        mayaAssertMsg(!_dirty, "You forgot to call: Skin_deformer::update_kinematic()");

        if(false)
        {
            tbx::Vec3 in = _mesh.geom().vertex( vertex_id );
            Transfo blend_matrix = tbx::Transfo::null();
            for( std::pair<int, float> pair : bones) {
                blend_matrix += _skinning_transfos[ pair.first ] * pair.second;
            }
            return Vec3( blend_matrix * Point3(in) );
        }
        else
        {
            tbx::Vec3 pos(0.0f);
            for( std::pair<int, float> pair : bones) {
                pos += Vec3( _skinning_transfos[ pair.first ] * Point3(_mesh.geom().vertex( vertex_id )) ) * pair.second;
            }
            return pos;
        }
    }

    // -------------------------------------------------------------------------

    /// Retreive vertex position of vert_id according to the current skin weights
    inline Vec3 vert_anim_pos(const std::vector<std::map<int, float> >& weights,
                              int vert_id) const
    {
        const std::map<int, float>& weight_map = weights[vert_id];
        return deform(vert_id, weight_map);
    }

    // -------------------------------------------------------------------------

    inline tbx::Mat3 get_rotation(const std::map<int, float>& weights) const
    {
        return anim::dual_quaternion_blending(weights, _skinning_dqs).get_non_dual_part().to_matrix3();
    }

    // -------------------------------------------------------------------------

    inline tbx::Mat3 get_rotation(int bone_id) const {
        return _skinning_dqs[bone_id].get_non_dual_part().to_matrix3();
    }

    // -------------------------------------------------------------------------

    // nabla S_i
    /// Differentiate the skinning function s(weights) -> vec3 according to the ith weight (bone_id)
    tbx::Vec3 gradient_deformer(int vertex_id, int bone_id, const std::vector<std::map<int, float> >& weights) const
    {
        mayaAssertMsg(!_dirty, "You forgot to call: Skin_deformer::update_kinematic()");

        if(true)
        {
            // Analytical version of linear blending:
            tbx::Vec3 in = _mesh.geom().vertex( vertex_id );
            return Vec3(Transfo_d(_skinning_transfos[bone_id]) * Point3_d(in));
        }
        else
        {
            // finite difference version (slower than analatical)
            // Could possibly work with more general deformers.
            float h = 0.0001f;
            std::map<int, float> weight_map = weights[vertex_id];
            float w = weight_map[bone_id];
            weight_map[bone_id] = w + h;
            tbx::Vec3 f_x_plus_h = deform(vertex_id, weight_map);
            weight_map[bone_id] = w - h;
            tbx::Vec3 f_x_minus_h = deform(vertex_id, weight_map);
            tbx::Vec3 res_fd= (f_x_plus_h - f_x_minus_h) / (2.0f * h);
            return res_fd;
        }
    }

    // -------------------------------------------------------------------------

    // S_i
    tbx::Vec3 skin_matrix(int vertex_id, int bone_id) const{
        tbx::Vec3 in = _mesh.geom().vertex( vertex_id );
        return Vec3( Transfo(_skinning_transfos[bone_id]) * Point3(in) );
    }

    // -------------------------------------------------------------------------

    const tbx::Transfo user_local(bone::Id id_joint) const {
        return _user_local[id_joint];
    }

    // U_j
    /// @warning you need to call update_kinematic()
    void set_user_local(bone::Id id_joint, const tbx::Transfo& tr)
    {
        _dirty = true;
        _user_local[id_joint] = tr;
    }

    // -------------------------------------------------------------------------

    void update_kinematic()
    {
        if(_dirty)
        {
            compute_skinning_transfo(_skinning_transfos);
        }
    }

    // -------------------------------------------------------------------------

private:
    void compute_skinning_transfo( std::vector<tbx::Transfo>& tr)
    {
        for(bone::Id root : _roots)
            rec_skinning_transfo( tr, root, tbx::Transfo::identity() );

        _dirty = false;
    }

    // -------------------------------------------------------------------------

    void rec_skinning_transfo(std::vector<tbx::Transfo>& transfos,
                              bone::Id id,
                              const tbx::Transfo& parent)
    {
        Transfo w_j = parent * _bind_local[id] * _user_local[id];

        Transfo t_j = w_j * _bind_pose[id].fast_inverse();
        _skinning_dqs[id] = Dual_quat(t_j);
        transfos[id] = t_j;

        for(unsigned i = 0; i < _sons[id].size(); i++)
            rec_skinning_transfo(transfos, _sons[id][i], w_j);
    }
};

}// END skin_brush Namespace ========================================

#endif // SKIN_DEFORMER_HPP
