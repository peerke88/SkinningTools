#ifndef TOOL_BOX_STD_UTILS_VECTOR_HPP
#define TOOL_BOX_STD_UTILS_VECTOR_HPP

#include <vector>
#include "toolbox_config/tbx_assert.hpp"

// Maybe create a header vector_algo.hpp for advanced operations and avoid
// including too many headers:
#include <memory>
#include <algorithm>
#include <random>

// =============================================================================
namespace tbx {
// =============================================================================

///@brief reverse the order of the elements in 'vec'
template <class T>
inline static std::vector<T> reversed(const std::vector<T>& vec)
{
    std::vector<T> rev = vec;
    std::reverse(std::begin(rev), std::end(rev));
    return rev;
}

// -----------------------------------------------------------------------------

///@brief check for duplicate values
template <class T>
inline static bool has_duplicates(const std::vector<T>& vec)
{
    if (true) {
        // Implem ver1
        std::vector<T> temp = vec;
        std::sort(temp.begin(), temp.end());
        typename std::vector<T>::iterator it = std::unique(temp.begin(), temp.end());
        bool is_unique = (it == temp.end());

        return !is_unique;
    }
    else {
        // Implem ver2
        for (std::size_t i = 0; i < vec.size(); ++i) {
            for (std::size_t j = i + 1; j < vec.size(); ++j) {
                if (vec[i] == vec[j])
                    return true;
            }
        }
        return false;
    }
}

// -----------------------------------------------------------------------------

///@brief random shuffle of the elements of 'vec'
template <class T>
inline static void shuffle(std::vector<T>& vec)
{
    auto rng = std::default_random_engine {};
    std::shuffle(std::begin(vec), std::end(vec), rng);
}

// -----------------------------------------------------------------------------

//TODO: template parameters of tbx::map<T0, T1>() should be inverted to better
// reflect the input and output of the map. We should be able to write:
//std::vector<int> vec = tbx::map<int, float>(my_floats, incr);

/// @brief map every elements such as vec[i] = f(vec[i])
/// @param f : a function pointer (e.g. int f(float f); )
///
/// @code
///     int incr(float f){ return int(f)+1;  }
///
///     std::vector<float> my_floats(10, 0.f);
///     std::vector<int> vec = tbx::map<float, int>(my_floats, incr);
/// @endcode
///
/// @note it is safer to define template parameter upon calling:
/// @li map<My_type0, My_type1>( vec, function);
template <typename T0, typename T1>
inline static std::vector<T1> map(const std::vector<T0>& vec, T1 (*f)(T0 input))
{
    std::vector<T1> res(vec.size());
    for (std::size_t i = 0; i < vec.size(); i++)
        res[i] = f(vec[i]);

    return res;
}

// -----------------------------------------------------------------------------

template <typename T0, typename T1>
inline static std::vector<T1> map(const std::vector<T0>& vec, T1 (*f)(const T0& input))
{
    std::vector<T1> res(vec.size());
    for (std::size_t i = 0; i < vec.size(); i++)
        res[i] = f(vec[i]);

    return res;
}

// -----------------------------------------------------------------------------

/// @brief map every elements such as vec[i] = f(vec[i]) (f is a lambda)
/// @param f : a function pointer (e.g. int f(float f); )
///
/// @code
///     std::vector<float> my_floats(10, 0.f);
///     std::vector<int> vec = tbx::map<float, int>(my_floats, [](float f){ return int(f)+1;  });
/// @endcode
///
/// @note it is safer to define template parameter upon calling:
/// @li map<My_type0, My_type1>( vec, function);
template <typename T0, typename T1, typename L>
inline static std::vector<T1> map(const std::vector<T0>& vec, L lambda)
{
    std::vector<T1> res;
    res.reserve(vec.size());
    std::transform(vec.begin(), vec.end(), std::back_inserter(res), lambda);
    return res;
}

// -----------------------------------------------------------------------------

// In place version
template <typename T0, typename T1, typename L>
inline static void map(const std::vector<T0>& vec, std::vector<T1>& res, L lambda)
{
    res.reserve(vec.size());
    std::transform(vec.begin(), vec.end(), std::back_inserter(res), lambda);
}


// -----------------------------------------------------------------------------

///@brief force memory deletion of a std::vector (since std::vector::clear()
/// will not delete memory in most cases)
template <class T>
inline static void force_clear(std::vector<T>& vec)
{
    std::vector<T> empty;
    vec.clear();
    vec.swap(empty);
}

// -----------------------------------------------------------------------------

/// @return the index of the element "elt" in "vec".
/// @warning
template <class T>
inline static int index_of(const std::vector<T>& vec, const T& elt)
{
    tbx_assert(vec.size() > 0);
    return int(std::addressof(elt) - std::addressof(vec[0]));
}

// -----------------------------------------------------------------------------

/// @return the index of the iterator "it" in "vec".
template <class T>
inline static int index_of(const std::vector<T>& vec, const typename std::vector<T>::const_iterator& it)
{
    return int(it - vec.begin());
}

// -----------------------------------------------------------------------------

/// @return the last element in the vector and erase it.
template <class T>
inline static T pop(std::vector<T>& vec)
{
    tbx_assert(vec.size() > 0);
    T elt = vec.back();
    vec.pop_back();
    return elt;
}

// -----------------------------------------------------------------------------

/// Pops the ith element by swapping the last element of the vector with it
/// and decrementing the size of the vector
template <class T>
inline static void erase_pop(std::vector<T>& vec, int i)
{
    tbx_assert(vec.size() > 0);
    if (i != (vec.size() - 1))
        vec[i] = vec[vec.size() - 1];
    vec.pop_back();
}

// ------

//TODO: to be tested
template <class T>
inline static void erase_pop(std::vector<T>& vec, const typename std::vector<T>::iterator& it)
{
    tbx_assert(vec.size() > 0);
    if (it != (vec.end() - 1)) {
        *it = *(vec.end() - 1);
    }
    vec.pop_back();
}

// -----------------------------------------------------------------------------

/// Concatenate v0 and v1 into v0. their types can be different as long as
/// T0 and T1 are equal in terms of byte size.
template <class T0, class T1>
static void concat(std::vector<T0>& v0, std::vector<T1>& v1)
{
    tbx_assert(sizeof(T0) == sizeof(T1));
    v0.resize(v0.size() + v1.size());
    const int off = v0.size();
    for (unsigned i = 0; i < v1.size(); i++)
        v0[off + i] = *(reinterpret_cast<T0*>(&(v1[i])));
}

// -----------------------------------------------------------------------------

/// @return true if v0 and v1 are equal in size and their elements match
template <class T0, class T1>
static bool is_equal(std::vector<T0>& v0, std::vector<T1>& v1)
{
    if (v0.size() != v1.size())
        return false;

    for (unsigned i = 0; i < v1.size(); ++i)
        if (v0[i] != v1[i])
            return false;

    return true;
}

// -----------------------------------------------------------------------------

/// Copy src into dst (dst is resized ). their types can be different as long as
/// T0 and T1 are equal in terms of byte size.
template <class T0, class T1>
static void copy(std::vector<T0>& dst, const std::vector<T1>& src)
{
    tbx_assert(sizeof(T0) == sizeof(T1));
    dst.resize(src.size());
    for (unsigned i = 0; i < src.size(); i++)
        dst[i] = *(reinterpret_cast<const T0*>(&(src[i])));
}

// -----------------------------------------------------------------------------

/// Find 'elt' in 'vec'. Search is O(n).
template <class T0, class T1>
static bool exists(const std::vector<T0>& vec, const T1& elt)
{
    for (unsigned i = 0; i < vec.size(); i++)
        if (vec[i] == elt)
            return true;

    return false;
}

// -----------------------------------------------------------------------------

/// Find 'elt' in 'vec'. Search is O(n).
/// @return the index of the first occurence of 'elt' or -1 in not found
template <class T0, class T1>
static int find(const std::vector<T0>& vec, const T1& elt)
{
    for (unsigned i = 0; i < vec.size(); i++)
        if (vec[i] == elt)
            return i;

    return -1;
}

// -----------------------------------------------------------------------------

template <class T0>
static int find_max(const std::vector<T0>& vec)
{
    auto iterator = std::max_element(vec.begin(), vec.end());
    return index_of(vec, iterator);
}

// -----------------------------------------------------------------------------

/// Erase an element at the 'ith' position.
template <class T0>
static void erase(std::vector<T0>& vec, int ith)
{
    vec.erase(vec.begin() + ith);
}

// -----------------------------------------------------------------------------

/// Push back 'elt' in 'vec' if it does not exists. Search is O(n).
/// return true if succefully inserted
template <class T0, class T1>
static bool push_unique(std::vector<T0>& vec, const T1& elt)
{
    if (!exists(vec, elt)) {
        vec.push_back(elt);
        return true;
    }
    return false;
}

// -----------------------------------------------------------------------------

/// @brief merge every elements of "src" in "dst" if the element not already
/// present in "dst".
template <class T>
void merge(std::vector<T>& dst, const std::vector<T>& src)
{
    dst.reserve(dst.size() + src.size());
    for (const T& elt : src)
        tbx::push_unique(dst, elt);
}

// -----------------------------------------------------------------------------

/// Entirely fill "vec" with "val"
template <class T0>
static void fill(std::vector<T0>& vec, const T0& val)
{
#if 1
    for (unsigned i = 0; i < vec.size(); ++i)
        vec[i] = val;
#else
    std::fill(vec.begin(), vec.end(), val);
#endif
}

// -----------------------------------------------------------------------------

/// Erase 'elt' in 'vec' if it does exist. Search is O(n).
/// return true if deletion occured
template <class T0, class T1>
static bool erase_element(std::vector<T0>& vec, const T1& elt)
{
    int idx = -1;
    if ((idx = find(vec, elt)) > -1) {
        erase(vec, idx);
        return true;
    }
    return false;
}

// -----------------------------------------------------------------------------


/**
 * flatten a two dimensionnal vector "to_flatten" by concatenating every
 * elements in a one dimensional vector "flat".
 * @param [in] to_flatten : vector to be flatten
 * @param [out] flat: the values of "to_flatten" but in a flat (1D array) layout.
 * We simply concatenate "to_flatten" elements:
 * @code
 * flat[] = {to_flatten[0] , ... , to_flatten[to_flatten.size - 1]}
 * @endcode
 * @param [out] flat_offset : a table of indirections to access values in "flat".

 * Usage: look up "flat" using "flat_offset":
 @code
   for(int i = 0; i < (flat_offset.size() / 2); i++){
      int off     = flat_offset[i*2    ]; // Offset in "flat"
      int nb_elts = flat_offset[i*2 + 1]; // Nb elements of the second dimension
      for(int n = off; n < (off+nb_elts); n++) {
          T elt = flat[ n ];
      }
  }
  @endcode

  * @li flat_offset[i*2 + 0] == offset; such as flat[offset] == to_flatten[i][0]
  * @li flat_offset[i*2 + 1] == to_flatten[i].size()
  * Otherwise said:
  * @li to_flatten[i][j] == flat[ flat_offset[i*2 + 0] + j ]
  * @li j < flat_offset[i*2 + 1]
  * @li flat_offset.size() == to_flatten.size()* 2
*/
template <class T>
static void flatten(const std::vector<std::vector<T>>& to_flatten,
                    std::vector<T>& flat,
                    std::vector<int>& flat_offset)
{
    int total = 0;
    for (unsigned i = 0; i < to_flatten.size(); ++i)
        total += to_flatten[i].size();

    flat.resize(total);
    flat_offset.resize(to_flatten.size() * 2);

    int k = 0;
    for (unsigned i = 0; i < to_flatten.size(); i++) {
        int size = (int)to_flatten[i].size();
        flat_offset[2 * i] = k;
        flat_offset[2 * i + 1] = size;
        // Concatenate values
        for (int j = 0; j < size; j++)
            flat[k++] = to_flatten[i][j];
    }
}

// -----------------------------------------------------------------------------

/**
 * flatten a two dimensional vector "to_flatten" by concatenating every
 * elements in a one dimensional vector "flat".
 * @param [in] to_flatten : vector to be flatten
 * @param [out] flat : the flatten values. It simply the concatenation of every
 * vectors: flat[] = {to_flatten[0] , ... , to_flatten[to_flatten.size - 1]}
*/
template <class T>
static void flatten(const std::vector<std::vector<T>>& to_flatten,
                    std::vector<T>& flat)
{
    int total = 0;
    for (unsigned i = 0; i < to_flatten.size(); ++i)
        total += to_flatten[i].size();

    flat.resize(total);

    int k = 0;
    for (unsigned i = 0; i < to_flatten.size(); i++) {
        int size = (int)to_flatten[i].size();
        // Concatenate values
        for (int j = 0; j < size; j++)
            flat[k++] = to_flatten[i][j];
    }
}

// -----------------------------------------------------------------------------

// Just having some fun I don't think it's a good idea to use this iterator:
//TODO: to be tested
template <class T>
class Range_it {
    const std::vector<T>& _vector_ref;

public:
    Range_it(const std::vector<T>& vec)
        : _vector_ref(vec)
    {
    }

    /* TODO:
    Range_it(const std::vector<T>& vec,
             std::vector::size_type begin,
             std::vector::size_type end) : _vector_ref( vec ) {}
             */

    class Elt {
        const int _index;
        const T& _elt;

    public:
        Elt(int idx, const T& elt)
            : _index(idx)
            , _elt(elt)
        {
        }

        int index() const
        {
            return _index;
        }
        const T& element() const
        {
            return _elt;
        }
        const T& operator*() const
        {
            return _elt;
        }
    };

    class Iterator {
    protected:
        unsigned _idx;
        const std::vector<T>& _vector;
        inline Iterator(const std::vector<T>& vector, unsigned idx)
            : _idx(idx)
            , _vector(vector)
        {
        }

    public:
        inline bool operator!=(const Iterator& oth) const
        {
            return _idx != oth._idx;
        }
        inline const Iterator& operator++()
        {
            ++_idx;
            return (*this);
        }

        inline Elt operator*() const
        {
            return Elt(_idx, _vector[_idx]);
        }
    };

    inline Iterator begin() const
    {
        return Iterator(_vector_ref, 0);
    }
    inline Iterator end() const
    {
        return Iterator(_vector_ref, _vector_ref.size());
    }
};


} // END tbx NAMESPACE ==========================================================

#include "toolbox_stl/settings_end.hpp"

#endif // TOOL_BOX_STD_UTILS_VECTOR_HPP
