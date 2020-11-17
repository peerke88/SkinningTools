#include "data/build_examples.hpp"

#include <deque>
#include <set>
#include <toolbox_maths/calculus.hpp>
#include <toolbox_stl/vector.hpp>
#include <toolbox_maya/data/maya_skeleton_utils.hpp>
#include "sbr_settings.hpp"

// =============================================================================
namespace skin_brush {
// =============================================================================

enum Transformation_increment {
    eRot_x_plus = 0,
    eRot_x_minus,
    eRot_y_plus,
    eRot_y_minus,
    eRot_z_plus,
    eRot_z_minus,
    eIdentity,
    eEnd,
};

// -----------------------------------------------------------------------------
// Note: we have to take into account some kynematic constraints we extract
// from maya. Otherwise there is no way to know which is the correct axis
// For bend and twist :/ The user must informed us on what pose he whishes
// to optimize.

const std::vector<std::vector<Transfo> >& Build_examples::get_list_examples() const
{
    return _list_examples;
}

// -----------------------------------------------------------------------------

void Build_examples::add_random_pose_all_joints(
                                 int nb_max_samples,
                                 float degree_angle,
                                 const std::vector<tbx::bone::Id>& ignore_list)
{
    mayaAssert( _skel != nullptr);

    float rad_angle = tbx::to_radian(degree_angle);
    // This list must be in the same order as in "Transformation_increment"
    std::vector<tbx::Transfo> motions = {
        // Assume x is a twist
        Transfo::rotate(Vec3::unit_x(),  rad_angle),
        Transfo::rotate(Vec3::unit_x(), -rad_angle),
        // Assume y is a bend
        Transfo::rotate(Vec3::unit_y(),  rad_angle),
        Transfo::rotate(Vec3::unit_y(), -rad_angle),
        // Assume z is a bend
        Transfo::rotate(Vec3::unit_z(),  rad_angle),
        Transfo::rotate(Vec3::unit_z(), -rad_angle),
        Transfo::identity()
    };

    mayaAssert( motions.size() == eEnd);

    std::deque<Transformation_increment> init_increments;
    init_increments.push_back(eRot_x_plus);
    init_increments.push_back(eRot_x_minus);
    init_increments.push_back(eRot_y_plus);
    init_increments.push_back(eRot_y_minus);
    init_increments.push_back(eRot_z_plus);
    init_increments.push_back(eRot_z_minus);

    // set_examples[pose_id][bone_id] = transformation type rot(x/y/z)(-20°/+20°)
    std::set< std::vector<Transformation_increment> > set_examples;

    // We keep track of used increments
    // to be sure all possible increments (for a single joint) were used
    // available_increments[bone_id][number of available Transfo_increment] = Transfo_increment value
    std::vector< std::deque<Transformation_increment> > available_increments(_skel->get_max_size_bones());
    for(auto& increment_list : available_increments){
        increment_list = init_increments;
    }

    int iter = 0;
    do {
        std::vector<Transformation_increment> transfos(_skel->get_max_size_bones(), eIdentity);

        for(const tbx::Bone& bone : *_skel)
        {
            // We ignore the root joint (i.e. skel.compute_parent(bone.id()) == -1))
            // except if it's also a leaf (skel.compute_children(bone.id()).size() == 0)
            if( (_skel->parent(bone.id()) == -1 && _skel->children(bone.id()).size() > 0) ||
                tbx::exists(ignore_list, bone.id()) )
            {
                continue;
            }

            auto& increment_list = available_increments[bone.id()];

            int res = 0;
            int nb_options = int(increment_list.size());
            if( nb_options > 1){
                res = std::rand() % int(nb_options);
            }

            transfos[bone.id()] = increment_list[res];

            if( nb_options > 1 )
                increment_list.erase( increment_list.begin() + res  ); // Erase the increment we just used
            else
                increment_list = init_increments; // Used everything for this bone we reset
        }

        set_examples.insert( transfos );

    }while(set_examples.size() < nb_max_samples && ++iter < nb_max_samples*20);

    // Convert to real valued transformations
    for( auto list_transfos : set_examples)
    {
        std::vector<tbx::Transfo> transfos(_skel->get_max_size_bones(), Transfo::identity());
        for(const tbx::Bone& bone : *_skel) {
            Transformation_increment type = list_transfos[bone.id()];
            transfos[bone.id()] = motions[int(type)];
        }
        _list_examples.push_back( transfos );
    }
}

// -----------------------------------------------------------------------------

void Build_examples::add_rest_pose()
{
    mayaAssert( _skel != nullptr);
    //  Kind of hacky: will enforce rest pose arap match lbs rest pose and therefore skin weight normalization
    std::vector<tbx::Transfo> transfos(_skel->get_max_size_bones(), Transfo::identity());
    for( unsigned i = 0; i < 1; ++i)
        _list_examples.push_back( transfos ); // Include rest pose
}

// -----------------------------------------------------------------------------

void Build_examples::build_ex_for_arap_optimization(Build_examples& ex)
{
    ex.clear();
    ex.add_rest_pose();
    std::vector<bone::Id> ignore_list = get_bone_without_influence(*(ex._skel), g_prune_threshold);
    ex.add_random_pose_all_joints(15, 22.0f, ignore_list);
    ex.build_deformers();
}

// -----------------------------------------------------------------------------

void Build_examples::add_isolated_joints_motions(
        float degree_angle,
        const std::vector<tbx::bone::Id>& ignore_list)
{

    float rad_angle = tbx::to_radian(degree_angle);
    // FIXME: if we don't extract the kynematic information somehow, then
    // we can't know what's a bend or a twist...

    // We could possibly infer the global axis of a twist
    // (looking at joint position and hierachies: that's what we do to build the tbx::Bone segment actually)
    // and then convert it back to a local axis to compute the local rotation ...
    // (we're still left undecided for bending and other kynematic constraints)

    // Move joints in isolation:
    std::vector<tbx::Transfo> amotions = {
        Transfo::rotate(Vec3::unit_x(),  rad_angle*0.8f),
        Transfo::rotate(Vec3::unit_x(), -rad_angle*0.8f),
        Transfo::rotate(Vec3::unit_y(),  rad_angle*0.8f),
        Transfo::rotate(Vec3::unit_y(), -rad_angle*0.8f),
        Transfo::rotate(Vec3::unit_z(),  rad_angle*0.8f),
        Transfo::rotate(Vec3::unit_z(), -rad_angle*0.8f)
    };

    std::vector<tbx::Transfo> bmotions = {
        Transfo::rotate(Vec3::unit_x(),  rad_angle*0.3f),
        Transfo::rotate(Vec3::unit_x(), -rad_angle*0.3f),
        Transfo::rotate(Vec3::unit_y(),  rad_angle*0.3f),
        Transfo::rotate(Vec3::unit_y(), -rad_angle*0.3f),
        Transfo::rotate(Vec3::unit_z(),  rad_angle*0.3f),
        Transfo::rotate(Vec3::unit_z(), -rad_angle*0.3f)
    };

    for(const tbx::Bone& bone : *_skel)
    {
        if( _skel->parent(bone.id()) == -1 )
            continue; // skip root joints

        if( tbx::exists(ignore_list, bone.id() ) )
            continue;

        std::vector<tbx::Transfo> transfos(_skel->get_max_size_bones(), tbx::Transfo::identity());

        for(const tbx::Transfo& tr : amotions)
        {
            // Set only one joint angle:
            transfos[bone.id()] = tr;
            // And make it an example:
            _list_examples.push_back( transfos );
        }

        for(const tbx::Transfo& tr : bmotions)
        {
            // Set only one joint angle:
            transfos[bone.id()] = tr;
            // And make it an example:
            _list_examples.push_back( transfos );
        }
    }

}

// -----------------------------------------------------------------------------

void Build_examples::add_quartering_pose()
{
    std::vector<tbx::Transfo> transfos(_skel->get_max_size_bones(), tbx::Transfo::identity());
    for(const tbx::Bone& bone : *_skel)
    {
        int id = bone.id();
        int id_parent = _skel->parent(id);
        if( id_parent >= 0 )
        {
            Vec3 local_dir = _skel->get_bind_global(id_parent).fast_inverse() * bone.dir();
            local_dir.normalize();
            transfos[id] = Transfo::translate(local_dir * 3.0f);
        }
    }
    _list_examples.push_back( transfos );
}

// -----------------------------------------------------------------------------

void Build_examples::build_deformers(const Maya_mesh* mesh)
{
    mayaAssert( _skel != nullptr);

    if(mesh != nullptr)
        _mesh = mesh;

    mayaAssert( _mesh != nullptr);

    {
        // init as much skin deformers as examples.
        _list_deformers_per_example.resize( _list_examples.size() );
        for(unsigned i = 0; i < _list_examples.size(); ++i)
        {
            Uptr<Skin_deformer> dfm( new Skin_deformer(*_skel, *_mesh) );
            const std::vector<tbx::Transfo>& local_pose = _list_examples[i];
            for(const tbx::Bone& bone : *_skel)
            {
                const int id = bone.id();
                dfm->set_user_local(id, local_pose[id] );
            }
            dfm->update_kinematic();
            _list_deformers_per_example[i].swap(dfm);
        }
        _is_deformer_init = true;
    }
}

}// END skin_brush Namespace ========================================
