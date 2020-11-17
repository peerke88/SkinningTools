#ifndef TOOL_BOX_STD_UTILS_STACK_HPP
#define TOOL_BOX_STD_UTILS_STACK_HPP

#include "toolbox_config/tbx_assert.hpp"
#include <stack>

// =============================================================================
namespace tbx {
// =============================================================================

/// Pop and return the element from a stack
/// @return the element on top of the stack
template<class Elt>
static Elt pop(std::stack<Elt>& stack)
{
    tbx_assert(stack.size() > 0);
    Elt e = stack.top();
    stack.pop();
    return e;
}

}// END tbx NAMESPACE ==========================================================

#include "toolbox_stl/settings_end.hpp"

#endif // TOOL_BOX_STD_UTILS_STACK_HPP
