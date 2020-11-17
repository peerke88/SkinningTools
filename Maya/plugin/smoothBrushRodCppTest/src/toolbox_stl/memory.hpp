#ifndef TOOL_BOX_MEMORY_HPP
#define TOOL_BOX_MEMORY_HPP

#include <memory>

// =============================================================================
namespace tbx {
// =============================================================================

// Name shortcut for lazy people:

///@brief Sptr: shared pointer
/// usage: the owner is unknown the data is used around multiple entities
/// of the program
template<class T>
using Sptr = std::shared_ptr<T>;

// -----------------------------------------------------------------------------

/// @brief: Wptr: weak pointer
/// usage: the data has
template<class T>
using Wptr = std::weak_ptr<T>;

// -----------------------------------------------------------------------------

/// @brief Uptr: unique pointer
/// usage: the owner is known, the data can be moved around.
/// scenarios:
/// - I need class polymorphism but it's the user that instanciate specialization.
template<class T>
using Uptr = std::unique_ptr<T>;


}// END tbx NAMESPACE ==========================================================

#include "toolbox_stl/settings_end.hpp"

#endif // TOOL_BOX_MEMORY_HPP
