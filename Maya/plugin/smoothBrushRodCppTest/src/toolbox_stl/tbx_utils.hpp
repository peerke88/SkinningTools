#ifndef TOOL_BOX_TBX_UTILS_HPP
#define TOOL_BOX_TBX_UTILS_HPP

#include "toolbox_config/tbx_assert.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

/**
    @namespace ::tbx::utils
    @brief Utilities for the c++ programmer's everyday life (lib independent)
*/
// =============================================================================
namespace utils {
// =============================================================================

/// Function macro to generically swap datas or pointers in a single line
/// @note In pure host functions you can use std::swap() instead
/// (in header <algorithm>)
template<class T>
 static inline
void swap(T& src, T& dst){
    T tmp = src;
    src = dst;
    dst = tmp;
}

// -----------------------------------------------------------------------------

/// Simple recopy of two arrays of arbitrary type.
template<class T>
 static inline
void copy(T* dst, const T* src, int nb_elt)
{
    for (int i = 0; i < nb_elt; ++i)
        dst[i] = src[i];
}

// -----------------------------------------------------------------------------

/*
template<class T> static inline
void copy(std::list<T>& dst, const std::vector<T>& src)
{
    for(const T& elt : src)
        dst.push_back( elt );
}
*/

}// End Namespace utils ========================================================

// =============================================================================
namespace flag {
// =============================================================================

/// test a flag inside the bit field Obj_flags
/// flag::test(bit_field, bit_mask) == true if the bit of bit_mask set to 1
template<typename E>

static inline bool test(int flags, E a_flag){ return (flags & a_flag) != 0; }

/// enable flag
template<typename E>

static inline int set_on(int flags, E f){ return (flags | f); }

/// disable flag
template<typename E>

static inline int set_off(int flags, E f){ return (flags & (~f)); }

}// END Flag NAMESPACE =========================================================

}// END tbx NAMESPACE ==========================================================

#include "toolbox_stl/settings_end.hpp"

#endif // TOOL_BOX_TBX_UTILS_HPP
