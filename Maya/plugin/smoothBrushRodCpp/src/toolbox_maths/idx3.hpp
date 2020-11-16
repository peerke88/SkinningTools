#pragma once

#include "toolbox_config/tbx_assert.hpp"
#include "toolbox_maths/vector3_i.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

class Idx3_it;

/**
 * @struct Idx3
 * @brief 3d grid index with conversion to 3d and linear storage
 *
 *
 * Use case to look up
 *
 * Use case to look up every elements of a grid of 16x16x16
   @code

   Vec3_i s(16);

   for(Idx3 idx(s   ); idx.is_in(); ++idx)
   for(Idx3 idx(s, 0); idx.is_in(); ++idx)
   for(Idx3 curr : Idx3( s ) ) // C++11 iterator
   for(const Idx3& curr : Idx3( s ) )
   {
        Vec3_i idx_3d = curr.to_3d(); // or .to_vec3i() will do the same
        int   i      = curr.to_linear();

        // i == idx_3d.x + s.x * idx_3d.y + (s.x * s.y) * idx_3d.z
        tbx_printf("linear: %i \n", curr.to_linear());
        tbx_printf("3D: %f %f %f \n", curr.to_3d().x, curr.to_3d().y, curr.to_3d().z);
   }
   @endcode
 *
 * Looking up a subgrid "B" (size:10^3) Inside a bigger grid "A" (size:128^3):
 *
   @code
   // Define the iterator of the main grid "A"
   // We start at a specific position "off"
   Idx3 offset(Vec3_i(128), offx, offy, offz);

   // We iterate on the subgrid "B".
   for(Idx3 sub_idx(Vec3_i(10)); sub_idx.is_in(); ++sub_idx)
   {
       int i = (offset + sub_idx.to_vec3i()).to_linear();
       // 'i' is in linear coordinates of the grid 128^3 but will only look up
       // a sub block of size 10^3 starting from the offset in the 128^3 grid
   }
   @endcode
 */
struct Idx3 {
    friend class Idx3_it;

    // -------------------------------------------------------------------------
    /// @name Constructors
    // -------------------------------------------------------------------------

     inline
    Idx3() :  _size(-1, -1, -1), _id(-1) { }

    /// Build an index starting from the very beginning.
     inline
    Idx3(const Vec3_i& size) : _size(size), _id(0) { }

    /// Build index from a linear index
     inline
    Idx3(const Vec3_i& size, int idx) : _size(size), _id(idx) { }

    /// Build index from a 3d index
     inline
    Idx3(const Vec3_i& size, int ix, int iy, int iz) : _size(size) {
        _id = to_linear(_size, ix, iy, iz);
    }

    /// Build index from a 3d index
     inline
    Idx3(const Vec3_i& size, const Vec3_i& pos) : _size(size) {
        /* Should I authorize invalid indices?
        tbx_assert(pos.x >= 0 && pos.x < size.x);
        tbx_assert(pos.y >= 0 && pos.y < size.y);
        tbx_assert(pos.z >= 0 && pos.z < size.z);
        */
        set_3d( pos );
    }

    // -------------------------------------------------------------------------
    /// @name Set index position
    // -------------------------------------------------------------------------

     inline
    void set_linear(int i){ _id = i; }

     inline
    void set_3d(const Vec3_i& p){ set_3d(p.x, p.y, p.z); }

     inline
    void set_3d(int x, int y, int z){ _id = to_linear(_size, x, y, z); }

     inline
    int to_linear() const { return _id; }

    // -------------------------------------------------------------------------
    /// @name Get index position
    // -------------------------------------------------------------------------

     inline
    Vec3_i to_3d() const { Vec3_i r; to_3d(r.x, r.y, r.z); return r; }

     inline
    Vec3_i to_vec3i() const { return to_3d(); }

     inline
    void to_3d(int& x, int& y, int& z) const {
        x = _id % _size.x;
        int t = _id / _size.x;
        y =  t  % _size.y;
        z =  t  / _size.y;
    }

     inline int x() const { return _id % _size.x; }
     inline int y() const { return (_id / _size.x)  % _size.y; }
     inline int z() const { return (_id / _size.x)  / _size.y; }

    // -------------------------------------------------------------------------
    /// @name Other methods
    // -------------------------------------------------------------------------

#ifdef __CUDACC__
    int4 to_int4() const { return make_int4(_size.x, _size.y, _size.z, _id); }
#endif

     inline
    int size_linear() const { return _size.product(); }

     inline
    Vec3_i size() const { return _size; }

    /// A valid index is positive as well as its size
    // TODO: I'm not sure we should implement this method
    // deleting it would allow to check with assert() index bounds at construction
     inline
    bool is_valid() const {
        return _id >= 0 && size_linear() >= 0;
    }

    /// Does the index is out of its bounds (defined at construction)
     inline bool is_out() const { return !is_in(); }

    /// Does the index is inside its bounds (defined at construction)
     inline
    bool is_in() const {
        return (_id < size_linear()) && (_id >= 0);
    }

    // -------------------------------------------------------------------------
    /// @name Iterator
    // -------------------------------------------------------------------------

     inline Idx3_it begin() const;
     inline Idx3_it end()   const;

    // -------------------------------------------------------------------------
    /// @name Operators overload
    // -------------------------------------------------------------------------

     inline
    Idx3 operator++(   ) { return Idx3(_size, ++_id); }

     inline Idx3 operator++(int)
    { return Idx3(_size, _id++); }

     inline
    Idx3 operator--(   ) { return Idx3(_size, --_id); }

     inline
    Idx3 operator--(int) { return Idx3(_size, _id--); }

     inline
    bool operator==(const Idx3& i) const {
        return _size == i._size && _id == i._id;
    }

     inline
    bool operator!=(const Idx3& i) const {
        return _size != i._size || _id != i._id;
    }

     inline
    Idx3 operator =(const Idx3& i) {
        _size = i._size; _id = i._id; return *this;
    }

     inline friend
    Idx3 operator+ (const Idx3& id, const Vec3_i& v) {
        Vec3_i this_idx = id.to_3d();
        return Idx3(id._size, this_idx + v);
    }

     inline friend
    Idx3 operator+ (const Vec3_i& v, const Idx3& id) {
        return id + v;
    }

private:

     static inline
    int to_linear(const Vec3_i& size, int x, int y, int z) {
        return x + size.x * (y + size.y * z);
    }

    Vec3_i _size; ///< 3d size of the grid the index is looking up
    int   _id;   ///< Linear index


    //--------------------------------------------------------------------------
    // WARNING: these operators should not be used/implemented since:
    // (they don't really make sense) || (are to ambigus to decypher when used)
#if 0
    bool operator<=(const Idx3& ) const { return false; }
    bool operator>=(const Idx3& ) const { return false; }
    bool operator< (const Idx3& ) const { return false; }
    bool operator> (const Idx3& ) const { return false; }

    Idx3 operator- (const Idx3& ) const { return Idx3(); }
    Idx3 operator+ (const Idx3& ) const { return Idx3(); }
    Idx3 operator+=(const Idx3& )       { return Idx3(); }
    Idx3 operator-=(const Idx3& )       { return Idx3(); }

    bool operator==(int ) const { return false; }
    bool operator!=(int ) const { return false; }
    bool operator<=(int ) const { return false; }
    bool operator>=(int ) const { return false; }
    bool operator> (int ) const { return false; }
    bool operator< (int ) const { return false; }

    Idx3 operator+ (int )  const { return Idx3(); }
    Idx3 operator- (int )  const { return Idx3(); }
    Idx3 operator+=(int )        { return Idx3(); }
    Idx3 operator-=(int )        { return Idx3(); }
#endif
};

// -----------------------------------------------------------------------------

class Idx3_it {
    friend struct Idx3;
protected:
    Idx3 _idx;
    inline Idx3_it(const Idx3& idx) : _idx(idx) { }
public:
    inline bool operator!= (const Idx3_it& oth) const { return _idx._id != oth._idx._id; }
    inline const Idx3_it& operator++(   ) { ++_idx; return (*this); }

    const Idx3& operator*() const { return _idx; }
};

// -----------------------------------------------------------------------------

 inline Idx3_it Idx3::begin() const { return Idx3_it( Idx3(_size, 0) );                  }
 inline Idx3_it Idx3::end()   const { return Idx3_it( Idx3(_size, this->size_linear())); }

}// END tbx NAMESPACE ==========================================================

#include "toolbox_maths/settings_end.hpp"

