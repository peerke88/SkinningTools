#ifndef TOOL_BOX_STD_UTILS_SET_HPP
#define TOOL_BOX_STD_UTILS_SET_HPP

#include <set>

// =============================================================================
namespace tbx {
// =============================================================================

/// Test if an element is in the set.
/// @param elt : the element to be found
/// @return if we found the element
// third template parameter is here to avoid ambiguities
template<class Elt, class PElt>
static bool exists(const std::set<Elt>& set, const PElt& elt)
{
    return set.find( elt ) != set.end();
}

}// END tbx NAMESPACE ==========================================================

#include "toolbox_stl/settings_end.hpp"

#endif // TOOL_BOX_STD_UTILS_SET_HPP
