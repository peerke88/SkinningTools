#pragma once

#include <cstdlib>
#include "toolbox_maths/math_typedefs.hpp"
#include "toolbox_config/tbx_assert.hpp"
#include "toolbox_config/meta_headers/meta_math_cu.hpp"

// Dev note: Please try to maintain the other vector versions (Vec2, Vec3 etc.)
// when making changes

// =============================================================================
namespace tbx {
// =============================================================================

/** @brief Vector type compatible GCC and NVCC

  Vec4 can be used at your convenience with either NVCC or GCC.

  @note: the overloading operator '*' between vectors is the component wise
  multiplication. You may use dot() to do a scalar product, cross() for cross
  product and possibly mult() for component wise multiplication.

  @note We forbid implicit conversion to other vector types. This ensure a
  stronger type check. For instance it will avoid converting floats to integers
  by mistake.

  @see Vec2 Vec2_i Vec3 Vec3_i Vec4_i

*/

template <class Real>
struct Vector4 {

    Real x, y, z, w;

    // -------------------------------------------------------------------------
    /// @name Constructors
    // -------------------------------------------------------------------------


    Vector4() { x = Real(0); y = Real(0); z = Real(0); w = Real(0); }


    Vector4(Real x_, Real y_, Real z_, Real w_) { x = x_; y = y_; z = z_; w = w_; }


    template <class In_real> inline
    explicit Vector4(const Vector4<In_real>& v) { x = Real(v.x); y = Real(v.y); z = Real(v.z); w = Real(v.w); }


    explicit Vector4(Real v) { x = v; y = v; z = v; w = v; }

    /// @note implemented in Vec2.hpp because of cross definitions
     inline
    Vector4(const Vec2& v2, float z_, float w_);

    /// @note implemented in Vec2.hpp because of cross definitions
     inline
    Vector4(const Vec2_d& v2, double z_, double w_);

    /// @note implemented in Vec2_i.hpp because of cross definitions
     inline
    Vector4(const Vec2_i& v2, int z_, int w_);

    /// @note implemented in Vec3.hpp because of cross definitions
     inline
    Vector4(const Vec3& v3, float w_);

    /// @note implemented in Vec3.hpp because of cross definitions
     inline
    Vector4(const Vec3_d& v3, double w_);

    /// @note implemented in Vec3_i.hpp because of cross definitions
     inline
    Vector4(const Vec3_i& v3, int w_);

    /// @note implemented in point3.hpp because of cross definitions
     inline
    Vector4(const Point3& p3, float w_);

    /// @note implemented in point3.hpp because of cross definitions
     inline
    Vector4(const Point3_d& p3, double w_);

     static inline Vector4 unit_x()    { return Vector4(Real(1), Real(0), Real(0), Real(0)); }
     static inline Vector4 unit_y()    { return Vector4(Real(0), Real(1), Real(0), Real(0)); }
     static inline Vector4 unit_z()    { return Vector4(Real(0), Real(0), Real(1), Real(0)); }
     static inline Vector4 unit_w()    { return Vector4(Real(0), Real(0), Real(0), Real(1)); }
     static inline Vector4 zero()      { return Vector4(Real(0), Real(0), Real(0), Real(0)); }
     static inline Vector4 unit_scale(){ return Vector4(Real(1), Real(1), Real(1), Real(1)); }


    inline void set(Real x_, Real y_, Real z_, Real w_) { x = x_; y = y_; z = z_; w = w_; }

    #ifdef __CUDACC__
    __device__ __host__
    float4 to_float4() const{
        return make_float4(float(x), float(y), float(z), float(w));
    }
    #endif

    /// @return random vector between [-range range]
    static Vector4<Real> random(Real range){
        Real r2 = range * Real(2);
        return (Vector4<Real>((Real)rand(), (Real)rand(), (Real)rand(), (Real)rand()) * r2 / Real(RAND_MAX)) - range;
    }

    /// @return random vector with
    /// @li x in [-range.x range.x]
    /// @li y in [-range.y range.y]
    /// @li etc.
    static Vector4 random(const Vector4& range){
        Vector4 r2 = range * Real(2);
        return (Vector4((Real)rand(), (Real)rand(), (Real)rand(), (Real)rand()) * r2 / Real(RAND_MAX)) - range;
    }

    // -------------------------------------------------------------------------
    /// @name Overload operators
    // -------------------------------------------------------------------------

    // ----------
    // Additions
    // ----------


    Vector4 operator+(const Vector4& v_) const { return Vector4(x+v_.x, y+v_.y, z+v_.z, w+v_.w); }


    Vector4& operator+= (const Vector4& v_) {
        x += v_.x;
        y += v_.y;
        z += v_.z;
        w += v_.w;
        return *this;
    }


    Vector4 operator+(Real f_) const { return Vector4(x+f_, y+f_, z+f_, w+f_); }

    /// lhs scalar cwise addition
     inline friend
    Vector4 operator+(const Real d_, const Vector4& vec) { return Vector4(d_+vec.x, d_+vec.y, d_+vec.z, d_+vec.w); }


    Vector4& operator+= (Real f_) {
        x += f_;
        y += f_;
        z += f_;
        w += f_;
        return *this;
    }

    // -------------
    // Substractions
    // -------------


    Vector4 operator-(const Vector4 &v_) const {
        return Vector4(x-v_.x, y-v_.y, z-v_.z, w-v_.w);
    }


    Vector4& operator-= (const Vector4& v_) {
        x -= v_.x;
        y -= v_.y;
        z -= v_.z;
        w -= v_.w;
        return *this;
    }

    /// opposite vector

    Vector4 operator-() const {
        return Vector4(-x, -y, -z, -w);
    }


    Vector4 operator-(Real f_) const { return Vector4(x-f_, y-f_, z-f_, w-f_); }

    /// lhs scalar cwise substraction
     inline friend
    Vector4 operator-(const Real d_, const Vector4& vec) { return Vector4(d_-vec.x, d_-vec.y, d_-vec.z, d_-vec.w); }


    Vector4& operator-= (Real f_) {
        x -= f_;
        y -= f_;
        z -= f_;
        w -= f_;
        return *this;
    }

    // -------------
    // Comparisons
    // -------------


    bool operator!= (const Vector4 &v_) const {
        return (x != v_.x) |  (y != v_.y) | (z != v_.z) | (w != v_.w);
    }


    bool operator==(const Vector4& d_) const {
        return (x == d_.x) && (y == d_.y) && (z == d_.z) && (w == d_.w);
    }

    /// @note no mathematical meaning but useful to use vectors in std::map

    bool operator< (const Vector4& v_) const
    {
        if( x != v_.x)
            return x < v_.x;
        else if( y != v_.y )
            return y < v_.y;
        else if( z != v_.z )
            return z < v_.z;
        else
            return w < v_.w;
    }

    // -------------
    // Divisions
    // -------------


    Vector4 operator/(const Real d_) const {
        return Vector4(x/d_, y/d_, z/d_, w/d_);
    }


    Vector4& operator/=(const Real d_) {
        x /= d_;
        y /= d_;
        z /= d_;
        w /= d_;
        return *this;
    }


    Vector4 operator/(const Vector4 &v_) const {
        return Vector4(x/v_.x, y/v_.y, z/v_.z, w/v_.w);
    }

    // Should not be defined

    Vector4& operator/=(const Vector4& d_) {
        x /= d_.x;
        y /= d_.y;
        z /= d_.z;
        w /= d_.w;
        return *this;
    }

    // ----------------
    // Multiplication
    // ----------------

    /// rhs scalar multiplication

    Vector4 operator*(const Real d_) const { return Vector4(x*d_, y*d_, z*d_, w*d_); }

    /// lhs scalar multiplication
     inline friend
    Vector4 operator*(const Real d_, const Vector4& vec) { return Vector4(d_*vec.x, d_*vec.y, d_*vec.z, d_*vec.w); }


    Vector4& operator*=(const Real d_) {
        x *= d_;
        y *= d_;
        z *= d_;
        w *= d_;
        return *this;
    }


    Vector4 operator*(const Vector4 &v_) const {
        return Vector4(x*v_.x, y*v_.y, z*v_.z, w*v_.w);
    }

    // Should not be defined

    Vector4& operator*=(const Vector4& d_) {
        x *= d_.x;
        y *= d_.y;
        z *= d_.z;
        w *= d_.w;
        return *this;
    }

    // -------------------------------------------------------------------------
    /// @name Operators on vector
    // -------------------------------------------------------------------------

    /// product of all components

    Real product() const { return x*y*z*w; }

    /// sum of all components

    Real sum() const { return x+y+z+w; }

    /// Average all components

    Real average() const { return (x+y+z+w) * 0.25f; }

    /// semi dot product (component wise multiplication)

    Vector4 mult(const Vector4& v) const {
        return Vector4(x*v.x, y*v.y, z*v.z, w*v.w);
    }

    /// component wise division

    Vector4 div(const Vector4& v) const { return Vector4(x/v.x, y/v.y, z/v.z, w/v.w); }

    /// dot product

    Real dot(const Vector4& v_) const {
        return x * v_.x + y * v_.y + z * v_.z + w * v_.w;
    }

    /// absolute value of the dot product

    Real abs_dot(const Vector4& v_) const {
        return std::abs(x * v_.x + y * v_.y + z * v_.z + w * v_.w);
    }

    /// norm squared

    Real norm_squared() const { return dot(*this); }

    /// normalization

    Vector4 normalized() const {
        return (*this) * (Real(1)/std::sqrt(norm_squared()));
    }

    /// normalization

    Real normalize() {
        Real l = std::sqrt(norm_squared());
        Real f = Real(1) / l;
        x *= f;
        y *= f;
        z *= f;
        w *= f;
        return l;
    }

    /// normalization

    Real safe_normalize(const Real eps = 1e-10) {
        Real l = std::sqrt(norm_squared());
        if(l > eps){
            Real f = Real(1) / l;
            x *= f;
            y *= f;
            z *= f;
            w *= f;
            return l;
        } else {
            x = Real(1);
            y = Real(0);
            z = Real(0);
            w = Real(0);
            return Real(0);
        }
    }

    /// norm
     Real norm() const { return std::sqrt(norm_squared()); }

    /// value of the min coordinate
     Real get_min() const { return min(min(min(x,y),z), w); }

    /// value of the max coordinate
     Real get_max() const { return max(max(max(x,y),z), w); }

    /// get min between each component of this and 'v'

    Vector4 get_min( const Vector4& v ) const {
        return Vector4(min(x, v.x), min(y, v.y), min(z, v.z), min(w, v.w));
    }

    /// get max between each component of this and 'v'

    Vector4 get_max( const Vector4& v ) const {
        return Vector4(max(x, v.x), max(y, v.y), max(z, v.z), max(w, v.w));
    }

    /// @return if every components are within ]'min'; 'max'[

    bool check_range(Real min, Real max) const {
        return x > min && y > min && z > min && w > min &&
               x < max && y < max && z < max && w < max;
    }

    /// @return if every components are within ]'min'; 'max'[

    bool check_range(const Vector4& min, const Vector4& max) const {
        return x > min.x && y > min.y && z > min.z && w > min.w &&
               x < max.x && y < max.y && z < max.z && w < max.w;
    }

    /// @return if v is stricly equal to (this)
    /// @warning this is usually dangerous with floats.

    bool equals(const Vector4& v) const {
        return x == (v.x) && y == (v.y) && z == (v.z) && w == (v.w);
    }

    /// @return if v is equal to (this) within the 'eps' threshold

    bool safe_equals(const Vector4& v, Real eps) const {
        return std::abs(x - v.x) < eps &&
               std::abs(y - v.y) < eps &&
               std::abs(z - v.z) < eps &&
               std::abs(w - v.w) < eps;
    }

    /// clamp each vector values

    Vector4 clamp(Real min_v, Real max_v) const {
        return Vector4( min( max(x, min_v), max_v),
                        min( max(y, min_v), max_v),
                        min( max(z, min_v), max_v),
                        min( max(w, min_v), max_v));
    }

    /// clamp each vector values

    Vector4 clamp(const Vector4& min_v, const Vector4& max_v) const {
        return Vector4( min( max(x, min_v.x), max_v.x),
                        min( max(y, min_v.y), max_v.y),
                        min( max(z, min_v.z), max_v.z),
                        min( max(w, min_v.w), max_v.w));
    }

    /// absolute value of each component

    Vector4 get_abs() const {
        return Vector4( std::abs(x), std::abs(y), std::abs(z), std::abs(w) );
    }

    /// floor every components

    Vector4 floor() const {
        return Vector4( std::floor(x), std::floor(y), std::floor(z), std::floor(w) );
    }

    /// rotate of 0 step to the left (present for symmetry)
     Vector4 perm_x() const { return Vector4(x, y, z, w); }

    /// rotate of 1 step to the left (so that y is the first coordinate)
     Vector4 perm_y() const { return Vector4(y, z, w, x); }

    /// rotate of 2 steps to the left (so that z is the first coordinate)
     Vector4 perm_z() const { return Vector4(z, w, x, y); }

    // -------------------------------------------------------------------------
    /// @name Accessors
    // -------------------------------------------------------------------------


    inline const Real& operator[](int i) const{
        tbx_assert( i < 4);
        return ((const Real*)this)[i];
    }


    inline Real& operator[](int i){
        tbx_assert( i < 4);
        return ((Real*)this)[i];
    }

    /// Conversion returns the memory address of the vector.
    /// Very convenient to pass a Vec pointer as a parameter to OpenGL:
    /// @code
    /// Vec4 pos, normal;
    /// glNormal4fv(normal);
    /// glVertex4fv(pos);
    /// @endcode
     operator const Real*() const = delete; // { return &x; }

    /// Conversion returns the memory address of the vector. (Non const version)
     operator Real*() = delete; //{ return &x; }

     const Real* data() const { return &x; }

    /// Conversion returns the memory address of the vector. (Non const version)
     Real* data() { return &x; }

    /// @name Access sub Vec3 components
    // Implemented in Vec3 because of cross definitions
    /// @{
     inline Vector3<Real> xyz() const;
     inline Vector3<Real> xzy() const;
     inline Vector3<Real> yxz() const;
     inline Vector3<Real> yzx() const;
     inline Vector3<Real> zxy() const;
     inline Vector3<Real> zyx() const;

     inline Vector3<Real> wyz() const;
     inline Vector3<Real> wzy() const;
     inline Vector3<Real> ywz() const;
     inline Vector3<Real> yzw() const;
     inline Vector3<Real> zwy() const;
     inline Vector3<Real> zyw() const;

     inline Vector3<Real> xwz() const;
     inline Vector3<Real> xzw() const;
     inline Vector3<Real> wxz() const;
     inline Vector3<Real> wzx() const;
     inline Vector3<Real> zxw() const;
     inline Vector3<Real> zwx() const;

     inline Vector3<Real> xyw() const;
     inline Vector3<Real> xwy() const;
     inline Vector3<Real> yxw() const;
     inline Vector3<Real> ywx() const;
     inline Vector3<Real> wxy() const;
     inline Vector3<Real> wyx() const;
    /// @}

    /// @name Access sub Vec2 components
    // Implemented in Vec2 because of cross definitions
    /// @{
     inline Vector2<Real> xy() const;
     inline Vector2<Real> xz() const;
     inline Vector2<Real> xw() const;
     inline Vector2<Real> yx() const;
     inline Vector2<Real> yz() const;
     inline Vector2<Real> yw() const;
     inline Vector2<Real> zx() const;
     inline Vector2<Real> zy() const;
     inline Vector2<Real> zw() const;
     inline Vector2<Real> wx() const;
     inline Vector2<Real> wy() const;
     inline Vector2<Real> wz() const;
    /// @}
private:
    template <typename T> static inline T max(T a, T b){ return ((a > b) ? a : b); }
    template <typename T> static inline T min(T a, T b){ return ((a < b) ? a : b); }
};

}// END tbx NAMESPACE ==========================================================

#if defined(TBX_USE_SIMD) && !defined(__CUDACC__)
    #include "toolbox_algos/vector4_smid4f.inl"
#endif

#include "toolbox_maths/settings_end.hpp"
