#pragma once

#include <cstdlib>
#include "toolbox_maths/math_typedefs.hpp"
#include "toolbox_maths/vector4.hpp"
#include "toolbox_config/tbx_assert.hpp"
#include "toolbox_config/meta_headers/meta_math_cu.hpp"

// Dev note: Please try to maintain the other vector versions (Vec2, Vec3 etc.)
// when making changes

// =============================================================================
namespace tbx {
// =============================================================================

/** @brief Vector type compatible GCC and NVCC

  Vec3 can be used at your convenience with either NVCC or GCC.

  @note: the overloading operator '*' between vectors is the component wise
  multiplication. You may use dot() to do a scalar product, cross() for cross
  product and possibly mult() for component wise multiplication.

  @note We forbid implicit conversion to other vector types. This ensure a
  stronger type check. For instance it will avoid converting floats to integers
  by mistake.

  @see Vec2 Vec2_i Vec3_i Vec4 Vec4_i

*/
template<class Real>
struct Vector3 {

    Real x, y, z;

    // -------------------------------------------------------------------------
    /// @name Constructors
    // -------------------------------------------------------------------------

     inline
    Vector3() { x = Real(0); y = Real(0); z = Real(0); }

     inline
    Vector3(Real x_, Real y_, Real z_) { x = x_; y = y_; z = z_; }

     inline
    explicit Vector3(Real v) { x = v; y = v; z = v; }

    
    template <class In_real> inline
    explicit Vector3(const Vector3<In_real>& v) { x = Real(v.x); y = Real(v.y); z = Real(v.z); }

    /// @note implemented in Vec2.hpp because of cross definitions
     inline
    Vector3(const Vec2& v2, float z_);

    /// @note implemented in Vec2.hpp because of cross definitions
     inline
    Vector3(const Vec2_d& v2, double z_);

    /// @note implemented in Vec2_i.hpp because of cross definitions
     inline
    Vector3(const Vec2_i& v2, int z_);

    /// Drop last component
     inline
    explicit Vector3(const Vec4& v4) { x = Real(v4.x); y = Real(v4.y); z = Real(v4.z); }

    /// Drop last component
     inline
    explicit Vector3(const Vec4_d& v4) { x = Real(v4.x); y = Real(v4.y); z = Real(v4.z); }

    /// @note implemented in Vec3_i.hpp because of cross definitions
    /// @note explicit constructor to avoid unwanted automatic conversions
     inline
    explicit Vector3(const Vec3_i& v3);

    /// @note implemented in point3.hpp because of cross definitions
    /// @note explicit constructor to avoid unwanted automatic conversions
     inline
    explicit Vector3(const Point3& p3);

    /// @note implemented in point3.hpp because of cross definitions
    /// @note explicit constructor to avoid unwanted automatic conversions
     inline
    explicit Vector3(const Point3_d& p3);

     static inline Vector3 unit_x()    { return Vector3(Real(1), Real(0), Real(0)); }
     static inline Vector3 unit_y()    { return Vector3(Real(0), Real(1), Real(0)); }
     static inline Vector3 unit_z()    { return Vector3(Real(0), Real(0), Real(1)); }
     static inline Vector3 zero()      { return Vector3(Real(0), Real(0), Real(0)); }
     static inline Vector3 unit_scale(){ return Vector3(Real(1), Real(1), Real(1)); }

    
    inline void set(Real x_, Real y_, Real z_) { x = x_; y = y_; z = z_; }

    #ifdef __CUDACC__
    __device__ __host__  inline
    float4 to_float4() const{
        return make_float4(float(x), float(y), float(z), 0.f);
    }
    #endif

    /// @return random vector between [-range range]
    static inline Vector3 random(Real range){
        Real r2 = Real(2) * range;
        return (Vector3<Real>((Real)(rand()), (Real)(rand()), (Real)(rand())) * r2 / Real(RAND_MAX)) - range;
    }

    /// @return random vector with
    /// @li x in [-range.x range.x]
    /// @li y in [-range.y range.y]
    /// @li etc.
    static inline Vector3 random(const Vector3& range){
        Vector3 r2 = range * Real(2);
        return (Vector3<Real>((Real)(rand()), (Real)(rand()), (Real)(rand())) * r2 / Real(RAND_MAX)) - range;
    }

private:
    /// @warning Implicit conversion to integer vector is forbidden
    /// use the constructor "Vec3_i( Vector3 vec )" to explicitly cast to integers
     operator Vec3_i();//{ return Vec3_i((int)x, (int)y, (int)z); }
public:

    // -------------------------------------------------------------------------
    /// @name Overload operators
    // -------------------------------------------------------------------------

    // ----------
    // Additions
    // ----------

     inline
    Vector3 operator+(const Vector3 &v_) const { return Vector3(x+v_.x, y+v_.y, z+v_.z); }

     inline
    Vector3& operator+= (const Vector3 &v_) {
        x += v_.x;
        y += v_.y;
        z += v_.z;
        return *this;
    }

     inline
    Vector3 operator+(Real f_) const { return Vector3(x+f_, y+f_, z+f_); }

    /// lhs scalar cwise addition
     inline friend
    Vector3 operator+(const Real d_, const Vector3& vec) { return Vector3(d_+vec.x, d_+vec.y, d_+vec.z); }

     inline
    Vector3& operator+= (Real f_) {
        x += f_;
        y += f_;
        z += f_;
        return *this;
    }

    // -------------
    // Substractions
    // -------------

     inline
    Vector3 operator-(const Vector3 &v_) const {
        return Vector3(x-v_.x, y-v_.y, z-v_.z);
    }

     inline
    Vector3& operator-= (const Vector3& v_) {
        x -= v_.x;
        y -= v_.y;
        z -= v_.z;
        return *this;
    }

    /// opposite vector
     inline
    Vector3 operator-() const {
        return Vector3(-x, -y, -z);
    }

     inline
    Vector3 operator-(Real f_) const { return Vector3(x-f_, y-f_, z-f_); }

    /// lhs scalar cwise substraction
     inline friend
    Vector3 operator-(const Real d_, const Vector3& vec) { return Vector3(d_-vec.x, d_-vec.y, d_-vec.z); }

     inline
    Vector3& operator-= (Real f_) {
        x -= f_;
        y -= f_;
        z -= f_;
        return *this;
    }

    // -------------
    // Comparisons
    // -------------

     inline
    bool operator!= (const Vector3 &v_) const {
        return (x != v_.x) |  (y != v_.y) | (z != v_.z);
    }

     inline
    bool operator==(const Vector3& d_) const {
        return (x == d_.x) && (y == d_.y) && (z == d_.z);
    }

    /// @note no mathematical meaning but useful to use vectors in std::map
     inline
    bool operator< (const Vector3& v_) const
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

     inline
    Vector3 operator/(const Real d_) const {
        return Vector3(x/d_, y/d_, z/d_);
    }

     inline
    Vector3& operator/=(const Real d_) {
        x /= d_;
        y /= d_;
        z /= d_;
        return *this;
    }

     inline
    Vector3 operator/(const Vector3 &v_) const {
        return Vector3(x/v_.x, y/v_.y, z/v_.z);
    }

    // Should not be defined
     inline
    Vector3& operator/=(const Vector3& d_) {
        x /= d_.x;
        y /= d_.y;
        z /= d_.z;
        return *this;
    }

    // ----------------
    // Multiplication
    // ----------------

    /// rhs scalar multiplication
     inline
    Vector3 operator*(const Real d_) const { return Vector3(x*d_, y*d_, z*d_); }

    /// lhs scalar multiplication
     inline friend
    Vector3 operator*(const Real d_, const Vector3& vec) { return Vector3(d_*vec.x, d_*vec.y, d_*vec.z); }

     inline
    Vector3& operator*=(const Real d_) {
        x *= d_;
        y *= d_;
        z *= d_;
        return *this;
    }

     inline
    Vector3 operator*(const Vector3 &v_) const {
        return Vector3(x*v_.x, y*v_.y, z*v_.z);
    }

     inline
    Vector3& operator*=(const Vector3& d_) {
        x *= d_.x;
        y *= d_.y;
        z *= d_.z;
        return *this;
    }

    // -------------------------------------------------------------------------
    /// @name Operators on vector
    // -------------------------------------------------------------------------

    /// product of all components
     inline
    Real product() const { return x*y*z; }

    /// sum of all components
     inline
    Real sum() const { return x+y+z; }

    /// Average all components
     inline
    Real average() const { return (x+y+z)/Real(3); }

    /// semi dot product (component wise multiplication)
     inline
    Vector3 mult(const Vector3& v) const {
        return Vector3(x*v.x, y*v.y, z*v.z);
    }

    /// component wise division
     inline
    Vector3 div(const Vector3& v) const {
        return Vector3(x/v.x, y/v.y, z/v.z);
    }

    /// cross product
     inline
    Vector3 cross(const Vector3& v_) const {
        return Vector3(y*v_.z-z*v_.y, z*v_.x-x*v_.z, x*v_.y-y*v_.x);
    }

    /// dot product
     inline
    Real dot(const Vector3& v_) const {
        return x*v_.x+y*v_.y+z*v_.z;
    }

    /// Compute the cotangente (i.e. 1./tan) between 'this' and v_
     inline
    Real cotan(const Vector3& v_) const {
        // cot(alpha ) = dot(v1, v2) / ||cross(v1, v2)||
        // = ||v1||*||v2||*cos( angle(v1, v2) ) / ||v1||*||v2|| * sin( angle(v1, v2) )
        // = cos( angle(v1, v2) ) / sin( angle(v1, v2) )
        // = 1 / tan( angle(v1, v2) )
        // = cot( angle(v1, v2) ) = cot( alpha )
        return (this->dot(v_)) / (this->cross(v_)).norm();
    }

    /// Signed angle between 'v1' and 'v2'. Vector 'this' is the reference plane
    /// normal. Vectors 'v1' and 'v2' are projected to the reference plane
    /// in order to determine the sign of the angle. Now that we are in the
    /// reference plane if the shortest rotation <b>from</b> v1 <b>to</b> v2
    /// is counter clock wise the angle is positive.
    /// Clockwise rotation is negative
    /// @return signed angle between [-PI; PI] starting from v1 to v2
     inline
    Real signed_angle(const Vector3& v1, const Vector3& v2) const {
        return std::atan2(  this->dot( v1.cross(v2) ), v1.dot(v2) );
    }

    /// TODO:
    /// Returns the angle between this vector and the specified vector, in radians.
    /** @note This function takes into account that this vector or the other vector can be unnormalized, and normalizes the computations.
            If you are computing the angle between two normalized vectors, it is better to use AngleBetweenNorm().
        @see AngleBetweenNorm(). */
        /*
    float AngleBetween(const float3 &other) const;
    {
    float cosa = Dot(other) / Sqrt(LengthSq() * other.LengthSq());
    if (cosa >= 1.f)
        return 0.f;
    else if (cosa <= -1.f)
        return pi;
    else
        return acos(cosa);
    }
    */

    /// absolute value of the dot product
     inline
    Real abs_dot(const Vector3& v_) const {
        return std::abs(x * v_.x + y * v_.y + z * v_.z);
    }

    /// norm squared
     inline
    Real norm_squared() const {
        return dot(*this);
    }

    /// normalization
     inline
    Vector3 normalized() const {
        return (*this) * (Real(1)/std::sqrt(norm_squared()));
    }

    /// normalization
     inline
    Real normalize() {
        Real l = std::sqrt(norm_squared());
        Real f = Real(1) / l;
        x *= f;
        y *= f;
        z *= f;
        return l;
    }

    /// normalization
     inline
    Real safe_normalize(const Real eps = 1e-10) {
        Real l = std::sqrt(norm_squared());
        if(l > eps){
            Real f = Real(1) / l;
            x *= f;
            y *= f;
            z *= f;
            return l;
        } else {
            x = Real(1);
            y = Real(0);
            z = Real(0);
            return Real(0);
        }
    }

    /// norm
     inline
    Real norm() const {
        return std::sqrt(norm_squared());
    }

    /// value of the min coordinate
     inline
    Real get_min() const {
        return min(min(x,y),z);
    }

    /// value of the max coordinate
     inline
    Real get_max() const {
        return max(max(x,y),z);
    }

    /// get min between each component of this and 'v'
     inline
    Vector3 get_min( const Vector3& v ) const {
        return Vector3(min(x, v.x), min(y, v.y), min(z, v.z));
    }

    /// get max between each component of this and 'v'
     inline
    Vector3 get_max( const Vector3& v ) const {
        return Vector3(max(x, v.x), max(y, v.y), max(z, v.z));
    }

    /// @return if every components are within ]'min'; 'max'[
     inline
    bool check_range(Real min, Real max) const {
        return x > min && y > min && z > min &&
               x < max && y < max && z < max;
    }

    /// @return if every components are within ]'min'; 'max'[
     inline
    bool check_range(const Vector3& min, const Vector3& max) const {
        return x > min.x && y > min.y && z > min.z &&
               x < max.x && y < max.y && z < max.z;
    }

    /// @return if v is stricly equal to (this)
    /// @warning this is usually dangerous with floats.
     inline
    bool equals(const Vector3& v) const {
        return x == (v.x) && y == (v.y) && z == (v.z);
    }

    // TODO: lower_than greater_than

    /// @return if v is equal to (this) within the 'eps' threshold
     inline
    bool safe_equals(const Vector3& v, Real eps) const {
        return std::abs(x - v.x) < eps && std::abs(y - v.y) < eps && std::abs(z - v.z) < eps;
    }

    /// clamp each vector values
     inline
    Vector3 clamp(Real min_v, Real max_v) const {
        return Vector3( min( max(x, min_v), max_v),
                        min( max(y, min_v), max_v),
                        min( max(z, min_v), max_v));
    }

    /// clamp each vector values
     inline
    Vector3 clamp(const Vector3& min_v, const Vector3& max_v) const {
        return Vector3( min( max(x, min_v.x), max_v.x),
                        min( max(y, min_v.y), max_v.y),
                        min( max(z, min_v.z), max_v.z));
    }

    /// absolute value of each component
     inline
    Vector3 get_abs() const {
        return Vector3( std::abs(x), std::abs(y), std::abs(z) );
    }

    /// floor every components
     inline
    Vector3 floor() const {
        return Vector3( std::floor(x), std::floor(y), std::floor(z) );
    }

    /// rotate of 0 step to the left (present for symmetry)
     inline
    Vector3 perm_x() const {
        return Vector3(x, y, z);
    }

    /// rotate of 1 step to the left (so that y is the first coordinate)
     inline
    Vector3 perm_y() const {
        return Vector3(y, z, x);
    }

    /// rotate of 2 steps to the left (so that z is the first coordinate)
     inline
    Vector3 perm_z() const {
        return Vector3(z, x, y);
    }

    /// Given the vector '*this' generate a 3d frame where vectors y_axis and
    /// z_axis are orthogonal to '*this'.
    
    void coordinate_system (Vector3& y_axis_, Vector3& z_axis) const {
        //for numerical stability, and seen that z will
        //always be present, take the greatest component between
        //x and y.
        if( std::abs(x) > std::abs(y) ) {
            Real inv_len = Real(1) / std::sqrt(x * x + z * z);
            Vector3 tmp(-z * inv_len, Real(0), x * inv_len);
            y_axis_ = tmp;
        } else {
            Real inv_len = Real(1) / std::sqrt(y * y + z * z);
            Vector3 tmp(Real(0), z * inv_len, -y * inv_len);
            y_axis_ = tmp;
        }
        z_axis = (*this).cross (y_axis_);
    }

    /// Get a random orthogonal vector
    
    Vector3 get_ortho() const
    {
        Vector3 ortho = this->cross(Vector3(Real(1), Real(0), Real(0)));

        if (ortho.norm_squared() < Real(1e-06 * 1e-06))
            ortho = this->cross( Vector3(Real(0), Real(1), Real(0)) );

        return ortho;
    }

    // FIXME: I think the plane should be defined in the parameters not by (*this)
    // It will be easier to read and more intuitive
    /// @return the vector to_project projected on the plane defined by the
    /// normal '*this'
    /// @warning don't forget to normalize the vector before calling
    /// proj_on_plane() !
     inline
    Vector3 proj_on_plane(const Vector3& to_project) const
    {
        return ( (*this).cross(to_project) ).cross( (*this) );
    }

    /// @return the point to_project projected on the plane defined by the
    /// normal '*this' and passing through pos_plane
    /// @warning don't forget to normalize the vector before calling
    /// proj_on_plane() !
    /// @note implemented in Point3.h because of cross definitions
    
    inline Point3_base<Real> proj_on_plane(const Point3_base<Real>& pos_plane,
                                           const Point3_base<Real>& to_project) const;

    /*
    // TODO and in the other vector classes:

    /// Makes the given vectors linearly independent.
    /// This function directly follows the Gram-Schmidt procedure on the input vectors.
        The vector a is kept unmodified, and vector b is modified to be perpendicular to a.
        Finally, if specified, the vector c is adjusted to be perpendicular to a and b.
        @note If any of the input vectors is zero, then the resulting set of vectors cannot be made orthogonal.
        @see AreOrthogonal(), Orthonormalize(), AreOrthonormal().
    static void Orthogonalize(const float3 &a, float3 &b);
    static void Orthogonalize(const float3 &a, float3 &b, float3 &c);

    Vector3f ProjectTo(const Vector3f& direction) const
    {
        assume(!direction.IsZero());
        return direction * this->Dot(direction) / direction.LengthSq();
    }
    void float3::Orthogonalize(const float3 &a, float3 &b, float3 &c)
    {
        if (!a.IsZero())
        {
            b -= b.ProjectTo(a);
            c -= c.ProjectTo(a);
        }
        if (!b.IsZero())
            c -= c.ProjectTo(b);
    }

    /// Makes the given vectors linearly independent and normalized in length.
     This function directly follows the Gram-Schmidt procedure on the input vectors.
        The vector a is first normalized, and vector b is modified to be perpendicular to a, and also normalized.
        Finally, if specified, the vector c is adjusted to be perpendicular to a and b, and normalized.
        @note If any of the input vectors is zero, then the resulting set of vectors cannot be made orthonormal.
        @see Orthogonalize(), AreOrthogonal(), AreOrthonormal().
    static void Orthonormalize(float3 &a, float3 &b);
    static void Orthonormalize(float3 &a, float3 &b, float3 &c);

    void float3::Orthonormalize(float3 &a, float3 &b)
{
    assume(!a.IsZero());
    assume(!b.IsZero());
    a.Normalize();
    b -= b.ProjectToNorm(a);
    b.Normalize();
}

void float3::Orthonormalize(float3 &a, float3 &b, float3 &c)
{
    assume(!a.IsZero());
    a.Normalize();
    b -= b.ProjectToNorm(a);
    assume(!b.IsZero());
    b.Normalize();
    c -= c.ProjectToNorm(a);
    c -= c.ProjectToNorm(b);
    assume(!c.IsZero());
    c.Normalize();
}

/// Returns this vector reflected about a plane with the given normal.
     By convention, both this and the reflected vector point away from the plane with the given normal
        @see Refract().
    float3 Reflect(const float3 &normal) const;

    /// Refracts this vector about a plane with the given normal.
     By convention, the this vector points towards the plane, and the returned vector points away from the plane.
        When the ray is going from a denser material to a lighter one, total internal reflection can occur.
        In this case, this function will just return a reflected vector from a call to Reflect().
        @param normal Specifies the plane normal direction
        @param negativeSideRefractionIndex The refraction index of the material we are exiting.
        @param positiveSideRefractionIndex The refraction index of the material we are entering.
        @see Reflect().
    float3 Refract(const float3 &normal, float negativeSideRefractionIndex, float positiveSideRefractionIndex) const;

    /// Projects this vector onto the given unnormalized direction vector.
     @param direction The direction vector to project this vector onto. This function will normalize this
            vector, so you can pass in an unnormalized vector.
        @see ProjectToNorm().
    float3 ProjectTo(const float3 &direction) const;

    /// Projects this vector onto the given normalized direction vector.
     @param direction The vector to project onto. This vector must be normalized.
        @see ProjectTo().
    float3 ProjectToNorm(const float3 &direction) const;

float3 float3::Reflect(const float3 &normal) const
{
    assume2(normal.IsNormalized(), normal.SerializeToCodeString(), normal.Length());
    return 2.f * this->ProjectToNorm(normal) - *this;
}

/// Implementation from http://www.flipcode.com/archives/reflection_transmission.pdf .
float3 float3::Refract(const float3 &normal, float negativeSideRefractionIndex, float positiveSideRefractionIndex) const
{
    // This code is duplicated in float2::Refract.
    float n = negativeSideRefractionIndex / positiveSideRefractionIndex;
    float cosI = this->Dot(normal);
    float sinT2 = n*n*(1.f - cosI*cosI);
    if (sinT2 > 1.f) // Total internal reflection occurs?
        return (-*this).Reflect(normal);
    return n * *this - (n + Sqrt(1.f - sinT2)) * normal;
}

float3 float3::ProjectTo(const float3 &direction) const
{
    assume(!direction.IsZero());
    return direction * this->Dot(direction) / direction.LengthSq();
}

float3 float3::ProjectToNorm(const float3 &direction) const
{
    assume(direction.IsNormalized());
    return direction * this->Dot(direction);
}

    */
    // -------------------------------------------------------------------------
    /// @name Accessors
    // -------------------------------------------------------------------------

private:
    /// Prefer using the cast operator -> Point3()
     inline Point3 to_point3() const;
     inline Point3_d to_point3_d() const;
public:

    
    inline const Real& operator[](int i) const{
        tbx_assert( i < 3);
        return ((const Real*)this)[i];
    }

    
    inline Real& operator[](int i){
        tbx_assert( i < 3);
        return ((Real*)this)[i];
    }

    inline const Real* data() const { return &x; }

    /// Conversion returns the memory address of the vector. (Non const version)
     inline Real* data() { return &x; }

    /// @name subVec2 Access sub Vec2 components
    // Implemented in Vec2 because of cross definitions
    /// @{
     inline Vector2<Real> xy() const;
     inline Vector2<Real> yx() const;
     inline Vector2<Real> xz() const;
     inline Vector2<Real> zx() const;
     inline Vector2<Real> yz() const;
     inline Vector2<Real> zy() const;
    /// @}
private:
    template <typename T> static inline T max(T a, T b){ return ((a > b) ? a : b); }
    template <typename T> static inline T min(T a, T b){ return ((a < b) ? a : b); }
};

// =============================================================================

// -----------------------------------------------------------------------------
// Some implems of Vector4<Real>
// -----------------------------------------------------------------------------

 template <class Real> inline
Vector4<Real>::Vector4(const Vec3& v3, float w_) {
    x = Real(v3.x);
    y = Real(v3.y);
    z = Real(v3.z);
    w = Real(w_);
}

// -----------------------------------------------------------------------------

 template <class Real> inline
Vector4<Real>::Vector4(const Vec3_d& v3, double w_) {
    x = Real(v3.x);
    y = Real(v3.y);
    z = Real(v3.z);
    w = Real(w_);
}

// -----------------------------------------------------------------------------

 template <class Real> inline Vector3<Real> Vector4<Real>::xyz() const{ return Vector3<Real>(x,y,z); }
 template <class Real> inline Vector3<Real> Vector4<Real>::xzy() const{ return Vector3<Real>(x,z,y); }
 template <class Real> inline Vector3<Real> Vector4<Real>::yxz() const{ return Vector3<Real>(y,x,z); }
 template <class Real> inline Vector3<Real> Vector4<Real>::yzx() const{ return Vector3<Real>(y,z,x); }
 template <class Real> inline Vector3<Real> Vector4<Real>::zxy() const{ return Vector3<Real>(z,x,y); }
 template <class Real> inline Vector3<Real> Vector4<Real>::zyx() const{ return Vector3<Real>(z,y,x); }

 template <class Real> inline Vector3<Real> Vector4<Real>::wyz() const{ return Vector3<Real>(w,y,z); }
 template <class Real> inline Vector3<Real> Vector4<Real>::wzy() const{ return Vector3<Real>(w,z,y); }
 template <class Real> inline Vector3<Real> Vector4<Real>::ywz() const{ return Vector3<Real>(y,w,z); }
 template <class Real> inline Vector3<Real> Vector4<Real>::yzw() const{ return Vector3<Real>(y,z,w); }
 template <class Real> inline Vector3<Real> Vector4<Real>::zwy() const{ return Vector3<Real>(z,w,y); }
 template <class Real> inline Vector3<Real> Vector4<Real>::zyw() const{ return Vector3<Real>(z,y,w); }

 template <class Real> inline Vector3<Real> Vector4<Real>::xwz() const{ return Vector3<Real>(x,w,z); }
 template <class Real> inline Vector3<Real> Vector4<Real>::xzw() const{ return Vector3<Real>(x,z,w); }
 template <class Real> inline Vector3<Real> Vector4<Real>::wxz() const{ return Vector3<Real>(w,x,z); }
 template <class Real> inline Vector3<Real> Vector4<Real>::wzx() const{ return Vector3<Real>(w,z,x); }
 template <class Real> inline Vector3<Real> Vector4<Real>::zxw() const{ return Vector3<Real>(z,x,w); }
 template <class Real> inline Vector3<Real> Vector4<Real>::zwx() const{ return Vector3<Real>(z,w,x); }

 template <class Real> inline Vector3<Real> Vector4<Real>::xyw() const{ return Vector3<Real>(x,y,w); }
 template <class Real> inline Vector3<Real> Vector4<Real>::xwy() const{ return Vector3<Real>(x,w,y); }
 template <class Real> inline Vector3<Real> Vector4<Real>::yxw() const{ return Vector3<Real>(y,x,w); }
 template <class Real> inline Vector3<Real> Vector4<Real>::ywx() const{ return Vector3<Real>(y,w,x); }
 template <class Real> inline Vector3<Real> Vector4<Real>::wxy() const{ return Vector3<Real>(w,x,y); }
 template <class Real> inline Vector3<Real> Vector4<Real>::wyx() const{ return Vector3<Real>(w,y,x); }



}// END tbx NAMESPACE ==========================================================

#if defined(TBX_USE_SIMD) && !defined(__CUDACC__)
    #include "toolbox_algos/vector3_smid4f.inl"
#endif

#include "toolbox_maths/settings_end.hpp"
