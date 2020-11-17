#pragma once

#include "toolbox_maths/math_typedefs.hpp"
#include "toolbox_config/tbx_assert.hpp"
#include "toolbox_maths/vector3.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

template <class Real>
struct Point3_base {

    Real x, y, z;

    
    Point3_base(){
        x = Real(0); y = Real(0); z = Real(0);
    }

    
    Point3_base(Real a, Real b, Real c) { x = a; y = b; z = c; }

    
    explicit Point3_base(Real v) { x = v; y = v; z = v; }

     template <class In_real>
    explicit Point3_base(const Vector3<In_real>& vec){
        x = Real(vec.x); y = Real(vec.y); z = Real(vec.z);
    }

     template <class In_real>
    explicit Point3_base(const Point3_base<In_real>& p){
        x = Real(p.x); y = Real(p.y); z = Real(p.z);
    }

     static inline Point3_base zero() { return Point3_base(Real(0), Real(0), Real(0)); }

    
    inline void set(Real x_, Real y_, Real z_) { x = x_; y = y_; z = z_; }

    static Point3_base random(Real r){
        Real r2 = Real(2) * r;
        Real x_ = Real(rand()) * Real(1) / Real(RAND_MAX);
        Real y_ = Real(rand()) * Real(1) / Real(RAND_MAX);
        Real z_ = Real(rand()) * Real(1) / Real(RAND_MAX);
        return Point3_base(x_ * r2 - r, y_ * r2 - r, z_ * r2 - r);
    }

    /// displacement
    
    Point3_base operator+(const Vec3 &v_) const {
        return Point3_base(x+v_.x, y+v_.y, z+v_.z);
    }

    Point3_base operator+=(const Vec3 &v_) {
        *this = *this + v_;
        return *this;
    }

    /// displacement
    
    Point3_base operator-(const Vec3& v_) const {
        return Point3_base(x-v_.x, y-v_.y, z-v_.z);
    }

    /// difference
    
    Vec3 operator-(const Point3_base& p_) const {
        return Vec3(x-p_.x, y-p_.y, z-p_.z);
    }

    /// opposite point
    
    Point3_base operator-() const {
        return Point3_base(-x, -y, -z);
    }

    
    Point3_base operator/(Real s) const {
        return Point3_base(x/s, y/s, z/s);
    }

    /// squared distance to another point
    
    Real distance_squared (const Point3_base& p_) const {
        return (p_ - *this).norm_squared();
    }

    
    Real norm() const {
        return std::sqrt(x*x + y*y + z*z);
    }


    /// value of the min coordinate
    
    Real get_min() const {
        return min(min(x,y),z);
    }

    /// value of the max coordinate
    
    Real get_max() const {
        return max( max(x, y), z );
    }

    
    explicit operator Vec3() const {
        return Vec3(float(x), float(y), float(z));
    }

    
    explicit operator Vec3_d() const {
        return Vec3_d(double(x), double(y), double(z));
    }

    #ifdef __CUDACC__
    __device__ __host__
    float4 to_float4() const{
        return make_float4(float(x), float(y), float(z), 0.f);
    }
    #endif

    
    Vec3 to_vec3() const {
        return Vec3(float(x), float(y), float(z));
    }

    
    Vec3_d to_vec3_d() const {
        return Vec3_d(double(x), double(y), double(z));
    }

    
    inline Point3_base operator+(const Point3_base& p) const {
        return Point3_base(x + p.x, y + p.y, z + p.z);
    }

    
    Point3_base& operator+= (const Point3_base& p_) {
        x += p_.x;
        y += p_.y;
        z += p_.z;
        return *this;
    }

    
    inline Point3_base operator*(Real f) const {
        return Point3_base(x * f, y * f, z * f);
    }

    
    inline const Real& operator[](int i) const{
        tbx_assert( i < 3);
        return ((const Real*)this)[i];
    }

    
    inline Real& operator[](int i){
        tbx_assert( i < 3);
        return ((Real*)this)[i];
    }

    /// Conversion returns the memory address of the point.
    /// Very convenient to pass a tbx::Point3_base pointer as a parameter to OpenGL:
    /// @code
    /// Point3 pos;
    /// glVertex3fv(pos);
    /// @endcode
    inline operator const Real*() const { return &x; }

    
    inline Point3_base perm_x() const { return Point3_base(x, y, z); }

    
    inline Point3_base perm_y() const { return Point3_base(y, z, x); }

    
    inline Point3_base perm_z() const { return Point3_base(z, x, y); }

    inline void print() const {
        tbx_printf("(%f,%f,%f) ", x, y, z);
    }
private:
    template <typename T> static inline T max(T a, T b){ return ((a > b) ? a : b); }
    template <typename T> static inline T min(T a, T b){ return ((a < b) ? a : b); }
};

// =============================================================================

// -----------------------------------------------------------------------------
// Some implems of Vec3
// -----------------------------------------------------------------------------


template<class Real> inline
Vector3<Real>::Vector3(const Point3_d& p3){
    x = Real(p3.x);
    y = Real(p3.y);
    z = Real(p3.z);
}

// -----------------------------------------------------------------------------


template<class Real> inline
Vector3<Real>::Vector3(const Point3& p3){
    x = Real(p3.x);
    y = Real(p3.y);
    z = Real(p3.z);
}

// -----------------------------------------------------------------------------


template <class Real> inline
Point3_base<Real> Vector3<Real>::proj_on_plane(
        const Point3_base<Real>& pos_plane,
        const Point3_base<Real>& to_project) const
{
    return to_project + (*this) * (pos_plane - to_project).dot( (*this) );
}

// -----------------------------------------------------------------------------

//
//template <class Real> inline
//Point3 Vector3<Real>::to_point3() const{
//    return Point3(float(x), float(y), float(z));
//}
//// -----------------------------------------------------------------------------

//
//template <class Real> inline
//Point3_d Vector3<Real>::to_point3d() const{
//    return Point3_d(double(x), double(y), double(z));
//}

// -----------------------------------------------------------------------------
// Some implems of Vec4
// -----------------------------------------------------------------------------


template <class Real> inline
Vector4<Real>::Vector4(const Point3& p3, float w_)
{
    x = Real(p3.x);
    y = Real(p3.y);
    z = Real(p3.z);
    w = Real(w_);
}

// -----------------------------------------------------------------------------


template <class Real> inline
Vector4<Real>::Vector4(const Point3_d& p3, double w_)
{
    x = Real(p3.x);
    y = Real(p3.y);
    z = Real(p3.z);
    w = Real(w_);
}



}// END tbx NAMESPACE ==========================================================

#include "toolbox_maths/settings_end.hpp"


