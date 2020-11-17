#ifndef TOOLBOX_BONE_TYPE_HPP
#define TOOLBOX_BONE_TYPE_HPP

// =============================================================================
namespace tbx {
// =============================================================================

/**
 *  @namespace ::anim::bone
 *  @brief holds enum fields and other types related to the Bone class
 *  @see Bone
*/
// =============================================================================
namespace bone {
// =============================================================================

/// A bone identifier
typedef int Id;

enum class Role {
    eLEAF,     ///< Leaf node (no children)
    eROOT,     ///< Root node (no parent)
    eINTERNAL, ///< Internal (parent and children exists)
    eUNDEF     ///< Unknown position in the hierarchy

};

} // END bone NAMESPACE ========================================================

} // END tbx NAMESPACE =========================================================

#include "toolbox_config/settings_end.hpp"

#endif // TOOLBOX_BONE_TYPE_HPP
