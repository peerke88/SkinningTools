#ifndef TOOLBOX_MAYA_MAYA_SKELETON_UTILS_HPP
#define TOOLBOX_MAYA_MAYA_SKELETON_UTILS_HPP

#include <vector>
#include "toolbox_maya/data/maya_skeleton.hpp"
#include <toolbox_maths/vector3.hpp>

// =============================================================================
namespace tbx_maya {
// =============================================================================

// =============================================================================
/// @name Work on Maya scene nodes
// =============================================================================

///@return whether this joint skin weights are locked in Maya
bool is_locked_joints(const Maya_skeleton& skel, tbx::bone::Id joint_id);

///@return vector[joint_id] == whether the joint is locked or not.
///@note queries the lock state of nodes through MEL.
std::vector<bool> get_locked_joints(const Maya_skeleton& skel);

/// @brief restore the position of the influence objects/joints as
/// found when calling 'skel->load(skin_cluster)'
/// @note modifies Maya state
void restore_initial_pose(const tbx_maya::Maya_skeleton& skel);

///@return the lowest node of type Mfn::kJoint under "joint"
MDagPath get_kjoint_root( const MDagPath& joint);


///@return list of currently selected joints in the Maya scene
std::vector<tbx::bone::Id> get_selected_joints(const Maya_skeleton& skel);

// =============================================================================
/// @name compute data from a skeleton
// =============================================================================

///@return the list of joints without influences.
std::vector<tbx::bone::Id>
get_bone_without_influence(const tbx_maya::Maya_skeleton& skel,
                           float eps_threshold = 0.0000001f);

}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_MAYA_SKELETON_UTILS_HPP
