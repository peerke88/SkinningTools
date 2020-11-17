#include "toolbox_maya/data/maya_skeleton_utils.hpp"

#include <toolbox_maths/skel/bone.hpp>
#include <toolbox_stl/map.hpp>

#include <toolbox_maya/utils/maya_attributes.hpp>
#include <toolbox_maya/utils/maya_dependency_nodes.hpp>
#include <toolbox_maya/utils/maya_dag_nodes.hpp>
#include <toolbox_maya/utils/maya_transform.hpp>
#include <toolbox_maya/utils/maya_utils.hpp>


// =============================================================================
namespace tbx_maya {
// =============================================================================

bool is_locked_joints(const Maya_skeleton& skel, tbx::bone::Id joint_id)
{
    MString joint_name = get_name( skel.get_dag_path( joint_id ) );
    MString cmd = "";
    cmd += ("skinCluster ");
    cmd += (" -influence ") + joint_name;
    cmd += (" -query -lockWeights ");
    cmd += get_name(skel.skin_cluster());
    int result = -1;
    MGlobal::executeCommand(cmd, result, g_debug_mode);
    return (result == 1);
}

// -----------------------------------------------------------------------------

std::vector<bool> get_locked_joints(const Maya_skeleton& skel)
{
    std::vector<bool> locked_joints( skel.get_max_size_bones(), false);
    for( tbx::Bone joint : skel)
        locked_joints[joint.id()] = is_locked_joints(skel, joint.id());

    return locked_joints;
}

// -----------------------------------------------------------------------------

std::vector<tbx::bone::Id> get_bone_without_influence(
        const Maya_skeleton& skel,
        float eps_threshold)
{
    std::vector<tbx::bone::Id> no_influence_list;
    for(const tbx::Bone& bone : skel){
        bool no_influence = true;
        for(unsigned vert_idx = 0; vert_idx < skel._weights.size(); ++vert_idx){
            if( tbx::find(skel._weights[vert_idx], bone.id(), 0.0f) > eps_threshold ){
                no_influence = false;
                break;
            }
        }
        if(no_influence)
            no_influence_list.push_back( bone.id() );
    }

    return no_influence_list;
}

// -----------------------------------------------------------------------------

void restore_initial_pose(const tbx_maya::Maya_skeleton& skel)
{
    for(const tbx::Bone& bone : skel)
    {
        int id = bone.id();
        set_MTransformationMatrix( get_MObject(skel.get_dag_path(id)), skel.get_initial_pose(id) );
    }
}

// -----------------------------------------------------------------------------

MDagPath get_kjoint_root(const MDagPath& joint)
{
    mayaAssert( joint.hasFn( MFn::kJoint ) );

    std::vector<MDagPath> parents = get_parents(joint);
    if( parents.size() == 0)
        return joint;
    else
    {
        if( parents.size() > 1 ){
            mayaWarning(MString("More than one parent for: ")+get_name(joint));
        }

        for(const MDagPath& parent : parents)
            if( parent.hasFn( MFn::kJoint ) )
                return get_kjoint_root( parent );

        return joint;
    }
}

// -----------------------------------------------------------------------------

std::vector<int> get_selected_joints(const Maya_skeleton& skel)
{
    std::vector<tbx::bone::Id>  res;
    for( const MDagPath& joint_path : get_selected(MFn::kJoint))
    {
        int id = skel.to_bone_id(joint_path);
        if( id > -1 )
            res.push_back( id );
    }
    return  res;
}

}// END tbx_maya Namespace =====================================================
