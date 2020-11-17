#pragma once

#include "toolbox_config/tbx_assert.hpp"
#include "toolbox_maths/vector3.hpp"
#include "toolbox_config/meta_headers/meta_math_cu.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

/**
 * @name Mat3
 * @brief Handling 3*3 matrix
 *
 * Memory layout
  =============

  The 3x3 matrix is stored linearly with 9 reals.
  The matrix is a <b>row first layout (i.e row major)</b>
 *
 * @see Transfo Vector3<Real>
 */
template<class Real>
struct Matrix3x3 {

    // row major
    Real a, b, c; ///< first row
    Real d, e, f; ///< second row
    Real g, h, i; ///< third row

     inline Matrix3x3() {   }

    
    template <class In_real>
    inline explicit
    Matrix3x3(const Matrix3x3<In_real>& m) {
        a = Real(m.a); b = Real(m.b); c = Real(m.c);
        d = Real(m.d); e = Real(m.e); f = Real(m.f);
        g = Real(m.g); h = Real(m.h); i = Real(m.i);
    }

     inline
    Matrix3x3(Real a_, Real b_, Real c_,
              Real d_, Real e_, Real f_,
              Real g_, Real h_, Real i_)
    {
        a = a_; b = b_; c = c_;
        d = d_; e = e_; f = f_;
        g = g_; h = h_; i = i_;
    }

     inline
    Matrix3x3(const Vector3<Real>& x,
              const Vector3<Real>& y,
              const Vector3<Real>& z)
    {
        a = x.x; b = y.x; c = z.x;
        d = x.y; e = y.y; f = z.y;
        g = x.z; h = y.z; i = z.z;
    }

     static inline
    Matrix3x3 diagonal(Real d)
    {
        return Matrix3x3(d      , Real(0), Real(0),
                         Real(0), d      , Real(0),
                         Real(0), Real(0), d    );
    }

    static inline Matrix3x3 from_array_ptr( const Real* row_major_ptr){
        Matrix3x3 result;
        for(int i = 0; i < 9; ++i)
            result[i] = row_major_ptr[i];
        return result;
    }

    // -------------------------------------------------------------------------
    /// @name operators overload
    // -------------------------------------------------------------------------


    //----------------
    // Multiplications
    //----------------

    
    Vector3<Real> operator*(const Vector3<Real>& v) const
    {
        Real x = v.x * a + v.y * b + v.z * c;
        Real y = v.x * d + v.y * e + v.z * f;
        Real z = v.x * g + v.y * h + v.z * i;
        return Vector3<Real>(x, y, z);
    }

    
    inline Matrix3x3 operator*(const Matrix3x3& m) const
    {
        return Matrix3x3(a * m.a + b * m.d + c * m.g,
                         a * m.b + b * m.e + c * m.h,
                         a * m.c + b * m.f + c * m.i,
                         d * m.a + e * m.d + f * m.g,
                         d * m.b + e * m.e + f * m.h,
                         d * m.c + e * m.f + f * m.i,
                         g * m.a + h * m.d + i * m.g,
                         g * m.b + h * m.e + i * m.h,
                         g * m.c + h * m.f + i * m.i);
    }

    
    inline Matrix3x3 operator*(Real x) const
    {
        return Matrix3x3(a * x, b * x, c * x,
                         d * x, e * x, f * x,
                         g * x, h * x, i * x);
    }

     inline
    Matrix3x3& operator*=(Real x)
    {
        a *= x; b *= x; c *= x;
        d *= x; e *= x; f *= x;
        g *= x; h *= x; i *= x;
        return *this;
    }

     inline friend
    Matrix3x3 operator*(const Real x_, const Matrix3x3& mat)
    {
        return Matrix3x3(x_ * mat.a, x_ * mat.b, x_ * mat.c,
                         x_ * mat.d, x_ * mat.e, x_ * mat.f,
                         x_ * mat.g, x_ * mat.h, x_ * mat.i);
    }

    //----------
    // Divisions
    //----------

     inline
    Matrix3x3 operator/(Real x) const
    {
        return Matrix3x3(a / x, b / x, c / x,
                         d / x, e / x, f / x,
                         g / x, h / x, i / x);
    }

private:
    // Dividing a matrix by another doesn't have any clear meaning
    
    inline Matrix3x3 operator/(const Matrix3x3& m) /* = delete*/ const;
public:

     inline
    Matrix3x3& operator/=(Real x)
    {
        a /= x; b /= x; c /= x;
        d /= x; e /= x; f /= x;
        g /= x; h /= x; i /= x;
        return *this;
    }

     inline friend
    Matrix3x3 operator/(const Real x_, const Matrix3x3& mat)
    {
        return Matrix3x3(x_ / mat.a, x_ / mat.b, x_ / mat.c,
                         x_ / mat.d, x_ / mat.e, x_ / mat.f,
                         x_ / mat.g, x_ / mat.h, x_ / mat.i);
    }

    //----------
    // Additions
    //----------


    
    inline Matrix3x3 operator+(const Matrix3x3& m) const
    {
        return Matrix3x3(a + m.a, b + m.b, c + m.c,
                         d + m.d, e + m.e, f + m.f,
                         g + m.g, h + m.h, i + m.i);
    }

     inline
    Matrix3x3 operator+(Real x) const
    {
        return Matrix3x3(a + x, b + x, c + x,
                         d + x, e + x, f + x,
                         g + x, h + x, i + x);
    }

     inline friend
    Matrix3x3 operator+(const Real x_, const Matrix3x3& mat)
    {
        return Matrix3x3(x_ + mat.a, x_ + mat.b, x_ + mat.c,
                         x_ + mat.d, x_ + mat.e, x_ + mat.f,
                         x_ + mat.g, x_ + mat.h, x_ + mat.i);
    }

     inline
    Matrix3x3& operator+=(Real x)
    {
        a += x; b += x; c += x;
        d += x; e += x; f += x;
        g += x; h += x; i += x;
        return *this;
    }

    //--------------
    // Substractions
    //--------------

    
    inline Matrix3x3 operator-(const Matrix3x3& m) const
    {
        return Matrix3x3(a - m.a, b - m.b, c - m.c,
                         d - m.d, e - m.e, f - m.f,
                         g - m.g, h - m.h, i - m.i);
    }

     inline
    Matrix3x3 operator-() const
    {
        return Matrix3x3(-a, -b, -c,
                         -d, -e, -f,
                         -g, -h, -i);
    }

     inline
    Matrix3x3 operator-(Real x) const
    {
        return Matrix3x3(a - x, b - x, c - x,
                         d - x, e - x, f - x,
                         g - x, h - x, i - x);
    }

     inline friend
    Matrix3x3 operator-(const Real x_, const Matrix3x3& mat)
    {
        return Matrix3x3(x_ - mat.a, x_ - mat.b, x_ - mat.c,
                         x_ - mat.d, x_ - mat.e, x_ - mat.f,
                         x_ - mat.g, x_ - mat.h, x_ - mat.i);
    }

     inline
    Matrix3x3& operator-=(Real x)
    {
        a -= x; b -= x; c -= x;
        d -= x; e -= x; f -= x;
        g -= x; h -= x; i -= x;
        return *this;
    }

    // -------------------------------------------------------------------------
    /// @name Accessors
    // -------------------------------------------------------------------------

    /// Conversion returns the memory address of the matrix.
    /// (row major)
     explicit operator const Real*() const = delete; //{ return ((Real*)(this)); }
    /// Conversion returns the memory address of the vector. (Non const version)
     explicit operator Real*() = delete; //{ return ((Real*)(this)); }

    /// Conversion returns the memory address of the matrix.
    /// (row major)
     const Real* data() const { return ((Real*)(this)); }
    /// Conversion returns the memory address of the vector. (Non const version)
     Real* data() { return ((Real*)(this)); }

    //----------------
    // Access elements
    //----------------

     inline
    const Real& operator()(int row, int column) const
    {
        tbx_assert(row >= 0 && row < 3);
        tbx_assert(column >= 0 && column < 3);
        return ((Real*)(this))[column + row*3];
    }

     inline
    Real& operator()(int row, int column)
    {
        tbx_assert(row >= 0 && row < 3);
        tbx_assert(column >= 0 && column < 3);
        return ((Real*)(this))[column + row*3];
    }

     inline Real& operator[](int idx) {
        tbx_assert(idx >= 0 && idx < 9);
        return ((Real*)(this))[idx];
    }

     inline const Real& operator[](int idx) const {
        tbx_assert(idx >= 0 && idx < 9);
        return ((Real*)(this))[idx];
    }

    // -------------------------------------------------------------------------
    /// @name operations
    // -------------------------------------------------------------------------

    
    inline Real det() const
    {
        return a * ( e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
    }

    /// @return the matrix with normalized x, y, z column vectors
    /// (basically eliminates scale factors of the matrix)
    
    inline Matrix3x3 normalized() const {
        return Matrix3x3(x().normalized(), y().normalized(), z().normalized());
    }

    
    inline Matrix3x3 inverse() const
    {
        Real c0 = e * i - f * h;
        Real c1 = f * g - d * i;
        Real c2 = d * h - e * g;
        Real idet = (a * c0 + b * c1 + c * c2);
        if(false){
            idet = Real(1.0) / idet;
            return Matrix3x3(c0 , c * h - b * i, b * f - c * e,
                             c1 , a * i - c * g, c * d - a * f,
                             c2 , b * g - a * h, a * e - b * d) * idet;
        }else{
            return Matrix3x3(c0 , c * h - b * i, b * f - c * e,
                             c1 , a * i - c * g, c * d - a * f,
                             c2 , b * g - a * h, a * e - b * d) / idet;
        }

    }

    
    inline Matrix3x3 transpose() const
    {
        return Matrix3x3(a, d, g,
                         b, e, h,
                         c, f, i);
    }

    
    inline void set_abs()
    {
        a = std::abs(a); b = std::abs(b); c = std::abs(c);
        d = std::abs(d); e = std::abs(e); f = std::abs(f);
        g = std::abs(g); h = std::abs(h); i = std::abs(i);
    }


    
    inline Real max_elt() const
    {
        return max(i, max(max(max(a,b),max(c,d)),
                      max(max(e,f),max(g,h))));
    }

    
    inline Real min_elt() const
    {
        return min(i, min(min(min(a,b),min(c,d)),
                      min(min(e,f),min(g,h))));
    }

    
    Matrix3x3 get_ortho() const
    {
        Matrix3x3 h0 = (*this);
        Matrix3x3 h1 = h0;
        h1.set_abs();
        Real eps = (Real(1) +  h1.min_elt()) * Real(1e-5);
        for(int i = 0; i < 500/* to avoid infinite loop */; i++){
            h0 = (h0 + (h0.inverse()).transpose()) * Real(0.5);
            h1 = h1 - h0;
            h1.set_abs();
            if(h1.max_elt() <= eps)
                break;
            h1 = h0;
        }
        return h0;
    }

    
    Real get_rotation_axis_angle(Vector3<Real>& axis) const
    {
        axis.x = h - f + Real(1e-5);
        axis.y = c - g;
        axis.z = d - b;
        Real sin_angle = axis.safe_normalize();
        Real cos_angle = a + e + i - Real(1);
        return std::atan2(sin_angle, cos_angle);
    }

    
    inline Vector3<Real> x() const { return Vector3<Real>(a, d, g); }
    
    inline Vector3<Real> y() const { return Vector3<Real>(b, e, h); }
    
    inline Vector3<Real> z() const { return Vector3<Real>(c, f, i); }

    
    inline void set_x(const Vector3<Real>& x) { a = x.x; d = x.y; g = x.z; }
    
    inline void set_y(const Vector3<Real>& y) { b = y.x; e = y.y; h = y.z; }
    
    inline void set_z(const Vector3<Real>& z) { c = z.x; f = z.y; i = z.z; }

     inline
    void set(Real a_, Real b_, Real c_,
             Real d_, Real e_, Real f_,
             Real g_, Real h_, Real i_)
    {
        a = a_; b = b_; c = c_;
        d = d_; e = e_; f = f_;
        g = g_; h = h_; i = i_;
    }

    //--------------------------------------------------------------------------
    /// @name Static constructors
    //--------------------------------------------------------------------------

    
    static inline Matrix3x3 identity()
    {
        return Matrix3x3(Real(1), Real(0), Real(0),
                         Real(0), Real(1), Real(0),
                         Real(0), Real(0), Real(1));

    }

    /// @return the rotation matrix given 'axis' and 'angle' in radian
    
    static inline Matrix3x3 rotate(const Vector3<Real>& axis, Real radian_angle)
    {
        Vector3<Real> n = axis;
        n.normalize();
        Real cp = std::cos(radian_angle);
        Real sp = std::sin(radian_angle);
        Real acp = Real(1) - cp;
        Real nxz = n.x * n.z;
        Real nxy = n.x * n.y;
        Real nyz = n.y * n.z;
        return Matrix3x3(cp + acp * n.x * n.x,
                         acp * nxy - sp * n.z,
                         acp * nxz + sp * n.y,

                         acp * nxy + sp * n.z,
                         cp + acp * n.y * n.y,
                         acp * nyz - sp * n.x,

                         acp * nxz - sp * n.y,
                         acp * nyz + sp * n.x,
                         cp + acp * n.z * n.z);
    }

    /// @return a orthogonal/normalized frame with its x axis aligned to x_axis
    
    static inline Matrix3x3 coordinate_system(const Vector3<Real>& x_axis)
    {
        Vector3<Real> fx, fy, fz;
        fx = x_axis.normalized();
        fx.coordinate_system(fy, fz);
        return Matrix3x3(fx, fy, fz);
    }

private:
    template <typename T> static inline T max(T a, T b){ return ((a > b) ? a : b); }
    template <typename T> static inline T min(T a, T b){ return ((a < b) ? a : b); }
};

}// END tbx NAMESPACE ==========================================================

#include "toolbox_maths/settings_end.hpp"
