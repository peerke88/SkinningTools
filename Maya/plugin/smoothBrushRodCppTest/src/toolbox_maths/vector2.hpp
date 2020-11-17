#pragma once

#include <cstdlib>
#include "toolbox_config/tbx_assert.hpp"
#include "toolbox_maths/math_typedefs.hpp"
#include "toolbox_config/meta_headers/meta_math_cu.hpp"
#include "toolbox_maths/vector3.hpp"
#include "toolbox_maths/vector3_i.hpp"
#include "toolbox_maths/vector4.hpp"

// Dev note: Please try to maintain the other vector versions (Vec2, Vec3 etc.)
// when making changes

// =============================================================================
namespace tbx {
// =============================================================================

/** @brief 2D float vector type compatible GCC and NVCC

  Vec2 can be used at your convenience with either NVCC or GCC.

  @note: the overloading operator '*' between vectors is the component wise
  multiplication. You may use dot() to do a scalar product and possibly mult()
  for component wise multiplication.

  @note We forbid implicit conversion to other vector types. This ensure a
  stronger type check. For instance it will avoid converting floats to integers
  by mistake.

  @see Vec2_i Vec3 Vec3_i Vec4 Vec4_i
*/
template <class Real>
struct Vector2 {

    Real x, y;

    // -------------------------------------------------------------------------
    /// @name Constructors
    // -------------------------------------------------------------------------

    
    Vector2() { x = Real(0); y = Real(0); }

    
    Vector2(Real x_, Real y_) { x = x_; y = y_; }

    
    template <class In_real> inline
    explicit Vector2(const Vector2<In_real>& v) { x = Real(v.x); y = Real(v.y); }

    
    explicit Vector2(Real v) { x = v; y = v; }

    /// Drop last component
    
    explicit Vector2(const Vec3& v3) { x = v3.x; y = v3.y; }

    /// Drop last component
    
    explicit Vector2(const Vec3_i& v3) { x = Real(v3.x); y = Real(v3.y); }

    /// @note implemented in Vec2_i.hpp because of cross definitions
     inline
    explicit Vector2(const Vec2_i& v2);

    
    static inline Vector2 unit_x(){ return Vector2(Real(1), Real(0)); }

    
    static inline Vector2 unit_y(){ return Vector2(Real(0), Real(1)); }

    
    static inline Vector2 zero() { return Vector2(Real(0), Real(0)); }

    
    static inline Vector2 unit_scale(){ return Vector2(Real(1), Real(1)); }

    
    inline void set(Real x_, Real y_) { x = x_; y = y_; }

    #ifdef __CUDACC__
    __device__ __host__
    float2 to_float2() const{ return make_float2(float(x), float(y)); }
    #endif

    /// @return random vector between [-range range]
    static Vector2 random(Real range){
        Real r2 = Real(2) * range;
        return (Vector2((Real)(rand()), (Real)(rand())) * r2 / (Real)(RAND_MAX)) - range;
    }

    /// @return random vector with
    /// @li x in [-range.x range.x]
    /// @li y in [-range.y range.y]
    static Vector2 random(const Vector2& range){
        Vector2 r2 = range * Real(2);
        return (Vector2((Real)(rand()), (Real)(rand())) * r2 / (Real)(RAND_MAX)) - range;
    }

private:
    /// @warning Implicit conversion to integer vector is forbidden
    /// use the constructor "Vec2_i( Vec2 vec )" to explicitly cast to integer
     operator Vec2_i();//{ return Vec2_i((float)x, (float)y); }
public:

    // -------------------------------------------------------------------------
    /// @name Overload operators
    // -------------------------------------------------------------------------

    // ----------
    // Additions
    // ----------

    
    Vector2 operator+(const Vector2 &v_) const { return Vector2(x+v_.x, y+v_.y); }

    
    Vector2& operator+= (const Vector2 &v_) {
        x += v_.x;
        y += v_.y;
        return *this;
    }

    
    Vector2 operator+(Real f_) const { return Vector2(x+f_, y+f_); }

     inline friend
    Vector2 operator+(const Real d_, const Vector2& vec) { return Vector2(d_+vec.x, d_+vec.y); }

    
    Vector2& operator+= (Real f_) {
        x += f_;
        y += f_;
        return *this;
    }

    // -------------
    // Substractions
    // -------------

    /// substraction
    
    Vector2 operator-(const Vector2 &v_) const { return Vector2(x-v_.x, y-v_.y); }

    
    Vector2& operator-= (const Vector2& v_) {
        x -= v_.x;
        y -= v_.y;
        return *this;
    }

    /// opposite vector
    
    Vector2 operator-() const { return Vector2(-x, -y); }

    
    Vector2 operator-(Real f_) const { return Vector2(x-f_, y-f_); }

     inline friend
    Vector2 operator-(const Real d_, const Vector2& vec) { return Vector2(d_-vec.x, d_-vec.y); }

    
    Vector2& operator-= (Real f_) {
        x -= f_;
        y -= f_;
        return *this;
    }

    // -------------
    // Comparisons
    // -------------

    
    bool operator!= (const Vector2 &v_) const {
        return (x != v_.x) | (y != v_.y);
    }

    
    bool operator==(const Vector2& d_)  const {
        return (x == d_.x) && (y == d_.y);
    }

    /// @note no mathematical meaning but useful to use vectors in std::map
    
    bool operator< (const Vector2& v_) const
    {
        if( x != v_.x)
            return x < v_.x;
        else
            return y < v_.y;
    }

    // -------------
    // Divisions
    // -------------

    
    Vector2 operator/(const Real d_) const {
        return Vector2(x/d_, y/d_);
    }

    
    Vector2& operator/=(const Real d_) {
        x /= d_;
        y /= d_;
        return *this;
    }

    
    Vector2 operator/(const Vector2 &v_) const { return Vector2(x/v_.x, y/v_.y); }

    
    Vector2& operator/=(const Vector2& d_) {
        x /= d_.x;
        y /= d_.y;
        return *this;
    }

    // ----------------
    // Multiplication
    // ----------------

    /// rhs scalar multiplication
    
    Vector2 operator*(const Real d_) const { return Vector2(x*d_, y*d_); }

    /// lhs scalar multiplication
     inline friend
    Vector2 operator*(const Real d_, const Vector2& vec) { return Vector2(d_*vec.x, d_*vec.y); }


    
    Vector2& operator*=(const Real d_) {
        x *= d_;
        y *= d_;
        return *this;
    }

    
    Vector2 operator*(const Vector2 &v_) const { return Vector2(x*v_.x, y*v_.y); }

    
    Vector2& operator*=(const Vector2& d_) {
        x *= d_.x;
        y *= d_.y;
        return *this;
    }

    // -------------------------------------------------------------------------
    /// @name Operators on vector
    // -------------------------------------------------------------------------

    // TODO: rename 'ortho()'
    /// @return vector perpendicular
    
    Vector2 perp() const { return Vector2(-y, x); }

    /// product of all components
    
    Real product() const { return x*y; }

    /// sum of all components
    
    Real sum() const { return x+y; }

    /// Average all components
    
    Real average() const { return (x+y) * Real(0.5); }

    /// semi dot product
    
    Vector2 mult(const Vector2& v) const {
        return Vector2(x*v.x, y*v.y);
    }

    /// component wise division
    
    Vector2 div(const Vector2& v) const { return Vector2(x/v.x, y/v.y); }

    /// cross product return a vector orthogonal to the xy plane.
    
    Vector3<Real> cross(const Vector2& v) const {
        return Vector3<Real>(x, y, Real(0)).cross( Vec3(v.x, v.y, Real(0)) );
    }

    /// dot product
    
    Real dot(const Vector2& v_) const {
        return x * v_.x + y * v_.y;
    }

    /// @return signed angle between [-PI; PI] starting from 'this' to 'v_'
    
    Real signed_angle(const Vector2& v_) const {
        return std::atan2( x * v_.y - y * v_.x, x * v_.x + y * v_.y );
    }

    /// absolute value of the dot product
    
    Real abs_dot(const Vector2& v_) const {
        return std::abs(x * v_.x + y * v_.y);
    }

    /// norm squared
    
    Real norm_squared() const {
        return dot(*this);
    }

    /// normalization
    
    Vector2 normalized() const {
        return (*this) * (Real(1)/sqrtf(norm_squared()));
    }

    /// normalization
    
    Real normalize() {
        Real l = sqrtf(norm_squared());
        Real f = Real(1) / l;
        x *= f;
        y *= f;
        return l;
    }

    /// normalization
    
    Real safe_normalize(const Real eps = 1e-10) {
        Real l = sqrtf(norm_squared());
        if(l > eps){
            Real f = Real(1) / l;
            x *= f;
            y *= f;
            return l;
        } else {
            x = Real(1);
            y = Real(0);
            return Real(0);
        }
    }

    /// norm
    
    Real norm() const {
        return sqrtf(norm_squared());
    }

    // TODO: rename get_min in simply min()

    /// value of the min coordinate
    
    Real get_min() const {
        return min(x,y);
    }

    /// value of the max coordinate
    
    Real get_max() const {
        return max(x,y);
    }

    /// get min between each component of this and 'v'
    
    Vector2 get_min( const Vector2& v ) const {
        return Vector2(min(x, v.x), min(y, v.y));
    }

    /// get max between each component of this and 'v'
    
    Vector2 get_max( const Vector2& v ) const {
        return Vector2(max(x, v.x), max(y, v.y));
    }

    /// @return if every components are within ]'min'; 'max'[
    
    bool check_range(Real min, Real max) const {
        return x > min && y > min &&
               x < max && y < max;
    }

    /// @return if every components are within ]'min'; 'max'[
    
    bool check_range(const Vector2& min, const Vector2& max) const {
        return x > min.x && y > min.y &&
               x < max.x && y < max.y;
    }

    /// @return if v is stricly equal to (this)
    /// @warning this is usually dangerous with floats.
    
    bool equals(const Vector2& v) const {
        return x == (v.x) && y == (v.y);
    }

    /// @return if v is equal to (this) within the 'eps' threshold
    
    bool safe_equals(const Vector2& v, Real eps) const {
        return std::abs(x - v.x) < eps && std::abs(y - v.y) < eps;
    }

    /// clamp each vector values
    
    Vector2 clamp(Real min_v, Real max_v) const {
        return Vector2( min( max(x, min_v), max_v),
                        min( max(y, min_v), max_v));
    }

    /// clamp each vector values
    
    Vector2 clamp(const Vector2& min_v, const Vector2& max_v) const {
        return Vector2( min( max(x, min_v.x), max_v.x),
                        min( max(y, min_v.y), max_v.y));
    }

    /// absolute value of each component
    
    Vector2 get_abs() const {
        return Vector2( std::abs(x), std::abs(y) );
    }

    /// floor every components
    
    Vector2 floor() const {
        return Vector2( std::floor(x), std::floor(y) );
    }

    /// rotate of 0 step to the left (present for symmetry)
    
    Vector2 perm_x() const {
        return Vector2(x, y);
    }

    /// rotate of 1 step to the left (so that y is the first coordinate)
    
    Vector2 perm_y() const {
        return Vector2(y, x);
    }

    /// Get a random orthogonal vector
    
    Vector2 get_ortho() const
    {
        Vec3 ortho = Vec3(x, y, Real(0)).cross( Vec3(Real(0), Real(0), Real(1)) );
        return Vector2( ortho.x, ortho.y);
    }

    /// @return the vector to_project projected on the line defined by the
    /// direction '*this'
    /// @warning don't forget to normalize the vector before calling this !
    
    Vector2 proj_on_line(const Vector2& to_project) const {
        return (*this) * (*this).dot( to_project );
    }

    // -------------------------------------------------------------------------
    /// @name Accessors
    // -------------------------------------------------------------------------

    
    inline const Real& operator[](int i) const{
        tbx_assert( i < 2);
        return ((const Real*)this)[i];
    }

    
    inline Real& operator[](int i){
        tbx_assert( i < 2);
        return ((Real*)this)[i];
    }

    /// Conversion returns the memory address of the vector.
    /// Very convenient to pass a Vec pointer as a parameter to OpenGL:
    /// @code
    /// Vec2 pos, normal;
    /// glNormal2fv(normal);
    /// glVertex2fv(pos);
    /// @endcode
     operator const Real*() const = delete; // { return &x; }

    /// Conversion returns the memory address of the vector. (Non const version)
     operator Real*() = delete; // { return &x; }

     const Real* data() const { return &x; }

    /// Conversion returns the memory address of the vector. (Non const version)
     Real* data() { return &x; }

private:
    template <typename T> static inline T max(T a, T b){ return ((a > b) ? a : b); }
    template <typename T> static inline T min(T a, T b){ return ((a < b) ? a : b); }
};
// =============================================================================

// -----------------------------------------------------------------------------
// Some implems of Vector3<Real>
// -----------------------------------------------------------------------------


template <class Real> inline
Vector3<Real>::Vector3(const Vec2& v2, float z_) {
    x = Real(v2.x);
    y = Real(v2.y);
    z = Real(z_);
}

// -----------------------------------------------------------------------------


template <class Real> inline
Vector3<Real>::Vector3(const Vec2_d& v2, double z_) {
    x = Real(v2.x);
    y = Real(v2.y);
    z = Real(z_);
}

// -----------------------------------------------------------------------------

 template <class Real> inline Vector2<Real> Vector3<Real>::xy() const { return Vector2<Real>(x, y); }
 template <class Real> inline Vector2<Real> Vector3<Real>::yx() const { return Vector2<Real>(y, x); }
 template <class Real> inline Vector2<Real> Vector3<Real>::xz() const { return Vector2<Real>(x, z); }
 template <class Real> inline Vector2<Real> Vector3<Real>::zx() const { return Vector2<Real>(z, x); }
 template <class Real> inline Vector2<Real> Vector3<Real>::yz() const { return Vector2<Real>(y, z); }
 template <class Real> inline Vector2<Real> Vector3<Real>::zy() const { return Vector2<Real>(z, y); }

// -----------------------------------------------------------------------------
// Some implems of Vec3_i
// -----------------------------------------------------------------------------

 inline
Vec3_i::Vector3_i(const Vec2& v2, float z_){
    x = int(v2.x);
    y = int(v2.y);
    z = int(z_);
}

// -----------------------------------------------------------------------------

 inline
Vec3_i::Vector3_i(const Vec2_d& v2, double z_){
    x = int(v2.x);
    y = int(v2.y);
    z = int(z_);
}

// -----------------------------------------------------------------------------
// Some implems of Vector4<Real>
// -----------------------------------------------------------------------------


template <class Real> inline
Vector4<Real>::Vector4(const Vec2& v2, float z_, float w_) {
    x = Real(v2.x);
    y = Real(v2.y);
    z = Real(z_);
    w = Real(w_);
}

// -----------------------------------------------------------------------------


template <class Real> inline
Vector4<Real>::Vector4(const Vec2_d& v2, double z_, double w_) {
    x = Real(v2.x);
    y = Real(v2.y);
    z = Real(z_);
    w = Real(w_);
}

// -----------------------------------------------------------------------------

 template <class Real> inline Vector2<Real> Vector4<Real>::xy() const { return Vector2<Real>(x,y); }
 template <class Real> inline Vector2<Real> Vector4<Real>::xz() const { return Vector2<Real>(x,z); }
 template <class Real> inline Vector2<Real> Vector4<Real>::xw() const { return Vector2<Real>(x,w); }
 template <class Real> inline Vector2<Real> Vector4<Real>::yx() const { return Vector2<Real>(y,x); }
 template <class Real> inline Vector2<Real> Vector4<Real>::yz() const { return Vector2<Real>(y,z); }
 template <class Real> inline Vector2<Real> Vector4<Real>::yw() const { return Vector2<Real>(y,w); }
 template <class Real> inline Vector2<Real> Vector4<Real>::zx() const { return Vector2<Real>(z,x); }
 template <class Real> inline Vector2<Real> Vector4<Real>::zy() const { return Vector2<Real>(z,y); }
 template <class Real> inline Vector2<Real> Vector4<Real>::zw() const { return Vector2<Real>(z,w); }
 template <class Real> inline Vector2<Real> Vector4<Real>::wx() const { return Vector2<Real>(w,x); }
 template <class Real> inline Vector2<Real> Vector4<Real>::wy() const { return Vector2<Real>(w,y); }
 template <class Real> inline Vector2<Real> Vector4<Real>::wz() const { return Vector2<Real>(w,z); }

}// END tbx NAMESPACE ==========================================================

#include "toolbox_maths/settings_end.hpp"
