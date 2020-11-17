#ifndef TOOL_BOX_STD_UTILS_MAP_HPP
#define TOOL_BOX_STD_UTILS_MAP_HPP

#include <map>
#include "toolbox_config/tbx_assert.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

/// Read a value from a map, returning a default value if there's no entry.
template <template<class, class, class...> class C, typename K, typename V, typename... Args>
static V find(const C<K, V, Args...>& map, K const& key, const V& defval)
{
    typename C<K, V, Args...>::const_iterator it = map.find( key );
    if (it == map.end())
        return defval;
    return it->second;
}

// -----------------------------------------------------------------------------

/// Find and retreive an element from the map. If not found an assertion is
/// triggered
/// @param elt : the element to be found
/// @return what is associated with 'k' in 'map'.
// third template parameter is here to avoid ambiguities
template<class Key, class Elt, class PKey>
static const Elt& find(const std::map<Key, Elt>& map, const PKey& key)
{
    typename std::map<Key, Elt>::const_iterator it = map.find( key );
    if( it != map.end() )
        return it->second;
    else
    {
        tbx_assert( false );
        return map.begin()->second;
    }
}

// -----------------------------------------------------------------------------

/// Find and retreive an element from the map. If not found an assertion is
/// triggered
/// @param elt : the element to be found
/// @return what is associated with 'k' in 'map'.
// third template parameter is here to avoid ambiguities
template<class Key, class Elt, class PKey>
static Elt& find(std::map<Key, Elt>& map, const PKey& key)
{
    typename std::map<Key, Elt>::iterator it = map.find( key );
    if( it != map.end() )
        return it->second;
    else
    {
        tbx_assert( false );
        return map.begin()->second;
    }
}

// -----------------------------------------------------------------------------

/// @brief Find and retreive an element from the map.
///
/** @code
    const T* value;
    if( tbx::find(map, key, value) ) {
        T var = *value;
    }
    @endcode
*/
/// @param elt : the key element to found
/// @param res : what is associated with 'elt' in 'map'.
/// @return if we found the element
// third/fourth templates parameters are there to avoid ambiguities
template<class Key, class Elt, class PKey, class PElt>
static bool find(const std::map<Key, Elt>& map, const PKey& elt, PElt const * & res)
{
    typename std::map<Key, Elt>::const_iterator it = map.find( elt );
    if( it != map.end() )
    {
        res = &(it->second);
        return true;
    }
    else
    {
        res = nullptr;
        return false;
    }
}

// -----------------------------------------------------------------------------

/// Find and retreive an element from the map.
/** @code
    T* value;
    if( tbx::find(map, key, value) ) {
        T var = *value;
    }
    @endcode
*/
/// @param elt : the key element to found
/// @param res : what is associated with 'elt' in 'map'.
/// @return if we found the element
// third/fourth templates parameters are there to avoid ambiguities
template<class Key, class Elt, class PKey, class PElt>
static bool find(std::map<Key, Elt>& map, const PKey& elt, PElt*& res)
{
    typename std::map<Key, Elt>::iterator it = map.find( elt );
    if( it != map.end() )
    {
        res = &(it->second);
        return true;
    }
    else
    {
        res = nullptr;
        return false;
    }
}

// -----------------------------------------------------------------------------

/// Test if an element is in the map.
/// @param elt : the key element to found
/// @return if we found the element
// third template parameter is here to avoid ambiguities
template<class Key, class Elt, class PKey>
static bool exists(const std::map<Key, Elt>& map, const PKey& elt)
{
    return map.find( elt ) != map.end();
}

}// END tbx NAMESPACE ==========================================================

#include "toolbox_stl/settings_end.hpp"

#endif // TOOL_BOX_STD_UTILS_MAP_HPP
