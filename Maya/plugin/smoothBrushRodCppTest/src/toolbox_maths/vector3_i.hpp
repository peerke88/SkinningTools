#pragma once

#include <cstdlib>
#include "toolbox_maths/math_typedefs.hpp"
#include "toolbox_config/tbx_assert.hpp"
#include "toolbox_config/meta_headers/meta_math_cu.hpp"
#include "toolbox_maths/vector3.hpp"

// Dev note: Please try to maintain the other vector versions (Vec2, Vec3 etc.)
// when making changes

// =============================================================================
namespace tbx {
// =============================================================================

/** @brief Vector type compatible GCC and NVCC

  Vec3_i can be used at your convenience with either NVCC or GCC.

  @note: the overloading operator '*' between vectors is the component wise
  multiplication. You may use dot() to do a scalar product, cross() for cross
  product and possibly mult() for component wise multiplication.

  @note We forbid implicit conversion to other vector types. This ensure a
  stronger type check. For instance it will avoid converting floats to integers
  by mistake.

  @see Vec2 Vec2_i Vec3 Vec4 Vec4_i
*/
struct Vector3_i {

    int x, y, z;

    // -------------------------------------------------------------------------
    /// @name Constructors
    // -------------------------------------------------------------------------

    
    Vector3_i() { x = 0; y = 0; z = 0; }

    
    Vector3_i(int x_, int y_, int z_) { x = x_; y = y_; z = z_; }

    
    explicit Vector3_i(int v) { x = v; y = v; z = v; }

    /// @note implemented in Vec2.hpp because of cross definitions
     inline
    Vector3_i(const Vec2& v2, float z_);

    /// @note implemented in Vec2.hpp because of cross definitions
     inline
    Vector3_i(const Vec2_d& v2, double z_);

    /// @note implemented in Vector2_i.hpp because of cross definitions
     inline
    Vector3_i(const Vec2_i& v2, int z_);

    /// Drop last component
    


    /// Drop last component
    
    explicit Vector3_i(const Vec4& v4) { x = (int)v4.x; y = (int)v4.y; z = (int)v4.z; }

    /// @note explicit constructor to avoid unwanted automatic conversions
    
    template <class In_real> inline
    explicit Vector3_i(const Vector3<In_real>& v3) { x = int(v3.x); y = int(v3.y); z = int(v3.z); }

     static inline Vector3_i unit_x()    { return Vector3_i(1, 0, 0); }
     static inline Vector3_i unit_y()    { return Vector3_i(0, 1, 0); }
     static inline Vector3_i unit_z()    { return Vector3_i(0, 0, 1); }
     static inline Vector3_i zero()      { return Vector3_i(0, 0, 0); }
     static inline Vector3_i unit_scale(){ return Vector3_i(1, 1, 1); }

    
    inline void set(int x_, int y_, int z_) { x = x_; y = y_; z = z_; }

    #ifdef __CUDACC__
    __device__ __host__
    int4 to_int4() const {
        return make_int4(x, y, z, 0);
    }
    #endif

    /// @return random vector between [-range range]
    static Vector3_i random(int range){
        float r2 = (float)(range * 2);
        return (Vector3_i( Vec3((float)rand(), (float)rand(), (float)rand()) * r2 / (float)RAND_MAX )) - range;
    }

    /// @return random vector with
    /// @li x in [-range.x range.x]
    /// @li y in [-range.y range.y]
    /// @li etc.
    static Vector3_i random(const Vector3_i& range){
        Vector3_i r2 = (range * 2);
        return (Vector3_i( Vec3((float)rand(), (float)rand(), (float)rand()) * Vec3(r2) / (float)RAND_MAX )) - range;
    }


private:
    /// @warning Implicit conversion to floating point vector is forbidden
    /// use the constructor "Vec3( Vector3_i vec )" to explicitly cast to floats
     operator Vec3(){ return Vec3((float)x, (float)y, (float)z); }
public:

    // -------------------------------------------------------------------------
    /// @name Overload operators
    // -------------------------------------------------------------------------

    // ----------
    // Additions
    // ----------

    
    Vector3_i operator+(const Vector3_i &v_) const { return Vector3_i(x+v_.x, y+v_.y, z+v_.z); }

    
    Vector3_i& operator+= (const Vector3_i &v_) {
        x += v_.x;
        y += v_.y;
        z += v_.z;
        return *this;
    }

    
    Vector3_i operator+(int f_) const { return Vector3_i(x+f_, y+f_, z+f_); }

    /// lhs scalar cwise addition
     inline friend
    Vector3_i operator+(const int d_, const Vector3_i& vec) { return Vector3_i(d_+vec.x, d_+vec.y, d_+vec.z); }

    
    Vector3_i& operator+= (int f_) {
        x += f_;
        y += f_;
        z += f_;
        return *this;
    }

    // -------------
    // Substractions
    // -------------

    
    Vector3_i& operator-= (const Vector3_i& v_) {
        x -= v_.x;
        y -= v_.y;
        z -= v_.z;
        return *this;
    }

    /// substraction
    
    Vector3_i operator-(const Vector3_i &v_) const {
        return Vector3_i(x-v_.x, y-v_.y, z-v_.z);
    }

    /// opposite vector
    
    Vector3_i operator-() const {
        return Vector3_i(-x, -y, -z);
    }

    
    Vector3_i operator-(int f_) const { return Vector3_i(x-f_, y-f_, z-f_); }

     inline friend
    Vector3_i operator-(const int d_, const Vector3_i& vec) { return Vector3_i(d_-vec.x, d_-vec.y, d_-vec.z); }

    
    Vector3_i& operator-= (int f_) {
        x -= f_;
        y -= f_;
        z -= f_;
        return *this;
    }

    // -------------
    // Comparisons
    // -------------

    
    bool operator!= (const Vector3_i &v_) const {
        return (x != v_.x) |  (y != v_.y) | (z != v_.z);
    }

    
    bool operator==(const Vector3_i& d_) const {
        return (x == d_.x) && (y == d_.y) && (z == d_.z);
    }

    /// @note no mathematical meaning but useful to use vectors in std::map
    
    bool operator< (const Vector3_i& v_) const
    {
        if( x != v_.x)
            return x < v_.x;
        else if( y != v_.y )
            return y < v_.y;
        else
            return z < v_.z;
    }

    // -------------
    // Divisions
    // -------------

    
    Vector3_i operator/(const int d_) const {
        return Vector3_i(x/d_, y/d_, z/d_);
    }

    
    Vector3_i& operator/=(const int d_) {
        x /= d_;
        y /= d_;
        z /= d_;
        return *this;
    }

    
    Vector3_i operator/(const Vector3_i &v_) const {
        return Vector3_i(x/v_.x, y/v_.y, z/v_.z);
    }

    
    Vector3_i& operator/=(const Vector3_i& d_) {
        x /= d_.x;
        y /= d_.y;
        z /= d_.z;
        return *this;
    }

    // ----------------
    // Multiplication
    // ----------------

    /// rhs scalar multiplication
    
    Vector3_i operator*(const int d_) const { return Vector3_i(x*d_, y*d_, z*d_); }

    /// lhs scalar multiplication
     inline friend
    Vector3_i operator* (const int d_, const Vector3_i& vec) { return Vector3_i(d_*vec.x, d_*vec.y, d_*vec.z); }

    
    Vector3_i& operator*=(const int d_) {
        x *= d_;
        y *= d_;
        z *= d_;
        return *this;
    }

    
    Vector3_i operator*(const Vector3_i &v_) const {
        return Vector3_i(x*v_.x, y*v_.y, z*v_.z);
    }

    
    Vector3_i& operator*=(const Vector3_i& d_) {
        x *= d_.x;
        y *= d_.y;
        z *= d_.z;
        return *this;
    }

    // -------------------------------------------------------------------------
    /// @name Operators on vector
    // -------------------------------------------------------------------------

    /// product of all components
    
    int product() const { return x*y*z; }

    /// sum of all components
    
    int sum() const { return x+y+z; }

    /// Average all components
    
    float average() const { return (float)(x+y+z)/3.f; }

    /// semi dot product
    
    Vector3_i mult(const Vector3_i& v) const {
        return Vector3_i(x*v.x, y*v.y, z*v.z);
    }

    /// component wise division
    
    Vector3_i div(const Vector3_i& v) const {
        return Vector3_i(x/v.x, y/v.y, z/v.z);
    }

    /// cross product
    
    Vector3_i cross(const Vector3_i& v_) const {
        return Vector3_i(y*v_.z-z*v_.y, z*v_.x-x*v_.z, x*v_.y-y*v_.x);
    }

    /// dot product
    
    int dot(const Vector3_i& v_) const {
        return x*v_.x+y*v_.y+z*v_.z;
    }

    /// Compute the cotangente (i.e. 1./tan) between 'this' and v_
    
    float cotan(const Vector3_i& v_) const {
        // cot(alpha ) = dot(v1, v2) / ||cross(v1, v2)||
        // = ||v1||*||v2||*cos( angle(v1, v2) ) / ||v1||*||v2|| * sin( angle(v1, v2) )
        // = cos( angle(v1, v2) ) / sin( angle(v1, v2) )
        // = 1 / tan( angle(v1, v2) )
        // = cot( angle(v1, v2) ) = cot( alpha )
        return  (float)(this->dot(v_)) / (this->cross(v_)).norm();
    }

    /// Signed angle between 'v1' and 'v2'. Vector 'this' is the reference plane
    /// normal. Vectors 'v1' and 'v2' are projected to the reference plane
    /// in order to determine the sign of the angle. Now that we are in the
    /// reference plane if the shortest rotation <b>from</b> v1 <b>to</b> v2
    /// is counter clock wise the angle is positive.
    /// Clockwise rotation is negative
    /// @return signed angle between [-PI; PI] starting from v1 to v2
    
    float signed_angle(const Vector3_i& v1, const Vector3_i& v2) const {
        return atan2(  (float)this->dot( v1.cross(v2) ), (float)v1.dot(v2) );
    }

    /// absolute value of the dot product
    
    int abs_dot(const Vector3_i& v_) const {
        return abs(x * v_.x + y * v_.y + z * v_.z);
    }

    /// norm squared
    
    int norm_squared() const {
        return dot(*this);
    }

    /// norm
    
    float norm() const {
        return sqrtf( (float)norm_squared() );
    }

    /// value of the min coordinate
    
    int get_min() const {
        return min(min(x,y),z);
    }

    /// value of the max coordinate
    
    int get_max() const {
        return max(max(x,y),z);
    }

    /// get min between each component of this and 'v'
    
    Vector3_i get_min( const Vector3_i& v ) const {
        return Vector3_i(min(x, v.x), min(y, v.y), min(z, v.z));
    }

    /// get max between each component of this and 'v'
    
    Vector3_i get_max( const Vector3_i& v ) const {
        return Vector3_i(max(x, v.x), max(y, v.y), max(z, v.z));
    }

    /// @return if every components are within ]'min'; 'max'[
    
    bool check_range(float min, float max) const {
        return x > min && y > min && z > min &&
               x < max && y < max && z < max;
    }

    /// @return if every components are within ]'min'; 'max'[
    
    bool check_range(const Vector3_i& min, const Vector3_i& max) const {
        return x > min.x && y > min.y && z > min.z &&
               x < max.x && y < max.y && z < max.z;
    }

    /// @return if v is stricly equal to (this)
    
    bool equals(const Vector3_i& v) const {
        return x == (v.x) && y == (v.y) && z == (v.z);
    }

    /// clamp each vector values
    
    Vector3_i clamp(int min_v, int max_v) const {
        return Vector3_i( min( max(x, min_v), max_v),
                      min( max(y, min_v), max_v),
                      min( max(z, min_v), max_v));
    }

    /// clamp each vector values
    
    Vector3_i clamp(const Vector3_i& min_v, const Vector3_i& max_v) const {
        return Vector3_i( min( max(x, min_v.x), max_v.x),
                      min( max(y, min_v.y), max_v.y),
                      min( max(z, min_v.z), max_v.z));
    }

    /// absolute value of each component
    
    Vector3_i get_abs() const {
        return Vector3_i( abs(x), abs(y), abs(z) );
    }

    // -------------------------------------------------------------------------
    /// @name Accessors
    // -------------------------------------------------------------------------

    /// rotate of 0 step to the left (present for symmetry)
    
    Vector3_i perm_x() const {
        return Vector3_i(x, y, z);
    }

    /// rotate of 1 step to the left (so that y is the first coordinate)
    
    Vector3_i perm_y() const {
        return Vector3_i(y, z, x);
    }

    /// rotate of 2 steps to the left (so that z is the first coordinate)
    
    Vector3_i perm_z() const {
        return Vector3_i(z, x, y);
    }

    // -------------------------------------------------------------------------
    /// @name Accessors
    // -------------------------------------------------------------------------

    
    inline const int& operator[](int i) const{
        tbx_assert( i < 3);
        return ((const int*)this)[i];
    }

    
    inline int& operator[](int i){
        tbx_assert( i < 3);
        return ((int*)this)[i];
    }

    /// Conversion returns the memory address of the vector.
    /// Very convenient to pass a Vec pointer as a parameter to OpenGL:
    /// @code
    /// Vec3_i pos, normal;
    /// glNormal3iv(normal);
    /// glVertex3iv(pos);
    /// @endcode
     operator const int*() const = delete; //{ return &x; }
    /// Conversion returns the memory address of the vector. (Non const version)
     operator int*() = delete; // { return &x; }

     const int* data() const { return &x; }
    /// Conversion returns the memory address of the vector. (Non const version)
     int* data() { return &x; }


    /// @name subVec2_i access sub Vec2_i components
    // Implemented in Vec2_i because of cross definitions
    /// @{
     inline Vec2_i xy() const;
     inline Vec2_i yx() const;
     inline Vec2_i xz() const;
     inline Vec2_i zx() const;
     inline Vec2_i yz() const;
     inline Vec2_i zy() const;
    /// @}
private:
    template <typename T> static inline T max(T a, T b){ return ((a > b) ? a : b); }
    template <typename T> static inline T min(T a, T b){ return ((a < b) ? a : b); }
};
// =============================================================================

// -----------------------------------------------------------------------------
// Some implem of Vector3<Real>
// -----------------------------------------------------------------------------


template<class Real> inline
Vector3<Real>::Vector3(const Vec3_i& v3) {
    x = static_cast<Real>(v3.x);
    y = static_cast<Real>(v3.y);
    z = static_cast<Real>(v3.z);
}

// -----------------------------------------------------------------------------
// Some implems of Vector4<Real>
// -----------------------------------------------------------------------------


template <class Real> inline
Vector4<Real>::Vector4(const Vec3_i& v3, int w_) {
    x = static_cast<Real>(v3.x);
    y = static_cast<Real>(v3.y);
    z = static_cast<Real>(v3.z);
    w = Real(w_);
}
}// END tbx NAMESPACE ==========================================================

#include "toolbox_maths/settings_end.hpp"

