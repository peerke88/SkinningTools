#include "toolbox_maths/transfo.hpp"


// =============================================================================
namespace tbx {
// =============================================================================


template<class Real> inline
AMatrix4x4<Real>::AMatrix4x4(Real a00, Real a01, Real a02, Real a03,
                             Real a10, Real a11, Real a12, Real a13,
                             Real a20, Real a21, Real a22, Real a23,
                             Real a30, Real a31, Real a32, Real a33)
{
    m[ 0] = a00; m[ 1] = a01; m[ 2] = a02; m[ 3] = a03;
    m[ 4] = a10; m[ 5] = a11; m[ 6] = a12; m[ 7] = a13;
    m[ 8] = a20; m[ 9] = a21; m[10] = a22; m[11] = a23;
    m[12] = a30; m[13] = a31; m[14] = a32; m[15] = a33;
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real>::AMatrix4x4(const Matrix3x3<Real>& x)
{
    m[ 0] = x.a; m[ 1] = x.b; m[ 2] = x.c; m[ 3] = Real(0);
    m[ 4] = x.d; m[ 5] = x.e; m[ 6] = x.f; m[ 7] = Real(0);
    m[ 8] = x.g; m[ 9] = x.h; m[10] = x.i; m[11] = Real(0);
    m[12] = Real(0); m[13] = Real(0); m[14] = Real(0); m[15] = Real(1);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real>::AMatrix4x4(const Matrix3x3<Real>& x, const Vector3<Real>& v){
    m[ 0] = x.a; m[ 1] = x.b; m[ 2] = x.c; m[ 3] = v.x;
    m[ 4] = x.d; m[ 5] = x.e; m[ 6] = x.f; m[ 7] = v.y;
    m[ 8] = x.g; m[ 9] = x.h; m[10] = x.i; m[11] = v.z;
    m[12] = Real(0); m[13] = Real(0); m[14] = Real(0); m[15] = Real(1);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real>::AMatrix4x4(const Vector3<Real>& v)
{
    m[ 0] = Real(1); m[ 1] = Real(0); m[ 2] = Real(0); m[ 3] = v.x;
    m[ 4] = Real(0); m[ 5] = Real(1); m[ 6] = Real(0); m[ 7] = v.y;
    m[ 8] = Real(0); m[ 9] = Real(0); m[10] = Real(1); m[11] = v.z;
    m[12] = Real(0); m[13] = Real(0); m[14] = Real(0); m[15] = Real(1);
}

// -----------------------------------------------------------------------------
// @name Accessors
// -----------------------------------------------------------------------------

 template<class Real> inline Vector3<Real> AMatrix4x4<Real>::x() const{ return Vector3<Real>( m[0], m[4], m[ 8] ); }
 template<class Real> inline Vector3<Real> AMatrix4x4<Real>::y() const{ return Vector3<Real>( m[1], m[5], m[ 9] ); }
 template<class Real> inline Vector3<Real> AMatrix4x4<Real>::z() const{ return Vector3<Real>( m[2], m[6], m[10] ); }

// -----------------------------------------------------------------------------


template<class Real> inline
Matrix3x3<Real> AMatrix4x4<Real>::get_mat3() const
{
    return Matrix3x3<Real>(m[0], m[1], m[2],
                           m[4], m[5], m[6],
                           m[8], m[9], m[10]);
}

// -----------------------------------------------------------------------------

 template<class Real> inline void AMatrix4x4<Real>::set_x(const Vector3<Real>& x){ m[0] = x.x; m[4] = x.y; m[ 8] = x.z; }
 template<class Real> inline void AMatrix4x4<Real>::set_y(const Vector3<Real>& y){ m[1] = y.x; m[5] = y.y; m[ 9] = y.z; }
 template<class Real> inline void AMatrix4x4<Real>::set_z(const Vector3<Real>& z){ m[2] = z.x; m[6] = z.y; m[10] = z.z; }

// -----------------------------------------------------------------------------

 template<class Real> inline
void AMatrix4x4<Real>::set_translation(const Vector3<Real>& tr)
{
    m[3] = tr.x; m[7] = tr.y; m[11] = tr.z;
}

// -----------------------------------------------------------------------------


template<class Real> inline
void AMatrix4x4<Real>::copy_translation(const AMatrix4x4& tr){
    const Vector3<Real> trans = tr.get_translation();
    m[3] = trans.x; m[7] = trans.y; m[11] = trans.z;
}

// -----------------------------------------------------------------------------


template<class Real> inline
void AMatrix4x4<Real>::set_mat3(const Matrix3x3<Real>& x){
    m[ 0] = x.a; m[ 1] = x.b; m[ 2] = x.c;
    m[ 4] = x.d; m[ 5] = x.e; m[ 6] = x.f;
    m[ 8] = x.g; m[ 9] = x.h; m[10] = x.i;
}

// -----------------------------------------------------------------------------
// Operators
// -----------------------------------------------------------------------------



template<class Real> inline
Vector4<Real> AMatrix4x4<Real>::operator*(const Vector4<Real>& v) const
{
    return Vector4<Real>(
                m[ 0] * v.x + m[ 1] * v.y + m[ 2] * v.z + m[ 3] * v.w,
                m[ 4] * v.x + m[ 5] * v.y + m[ 6] * v.z + m[ 7] * v.w,
                m[ 8] * v.x + m[ 9] * v.y + m[10] * v.z + m[11] * v.w,
                m[12] * v.x + m[13] * v.y + m[14] * v.z + m[15] * v.w);
}

// -----------------------------------------------------------------------------


template<class Real> inline
Point3_base<Real> AMatrix4x4<Real>::operator*(const Point3_base<Real>& v) const
{
    return Point3_base<Real>(
                m[0] * v.x + m[1] * v.y + m[ 2] * v.z + m[ 3],
                m[4] * v.x + m[5] * v.y + m[ 6] * v.z + m[ 7],
                m[8] * v.x + m[9] * v.y + m[10] * v.z + m[11]);
}

// -----------------------------------------------------------------------------


template<class Real> inline
Vector3<Real> AMatrix4x4<Real>::operator*(const Point_vec3<Real>& vec_as_point) const
{
    const Vector3<Real>& v = vec_as_point._data;
    return Vector3<Real>(
                m[0] * v.x + m[1] * v.y + m[ 2] * v.z + m[ 3],
                m[4] * v.x + m[5] * v.y + m[ 6] * v.z + m[ 7],
                m[8] * v.x + m[9] * v.y + m[10] * v.z + m[11]);
}


// -----------------------------------------------------------------------------


template<class Real> inline
Vector3<Real> AMatrix4x4<Real>::operator*(const Vector3<Real>& v) const {
    return Vector3<Real>(
            m[0] * v.x + m[1] * v.y + m[ 2] * v.z,
            m[4] * v.x + m[5] * v.y + m[ 6] * v.z,
            m[8] * v.x + m[9] * v.y + m[10] * v.z);
}


// -----------------------------------------------------------------------------


template<class Real> inline Vector3<Real>
AMatrix4x4<Real>::mult_as_point(const Vector3<Real>& v) const
{
    return Vector3<Real>(                
                m[0] * v.x + m[1] * v.y + m[ 2] * v.z + m[ 3],
                m[4] * v.x + m[5] * v.y + m[ 6] * v.z + m[ 7],
                m[8] * v.x + m[9] * v.y + m[10] * v.z + m[11]);
}

// -----------------------------------------------------------------------------


template<class Real> inline
Point3_base<Real> AMatrix4x4<Real>::mult_as_vec(const Point3_base<Real>& v) const
{
    return Vector3<Real>(
            m[0] * v.x + m[1] * v.y + m[ 2] * v.z,
            m[4] * v.x + m[5] * v.y + m[ 6] * v.z,
            m[8] * v.x + m[9] * v.y + m[10] * v.z);
}

// -----------------------------------------------------------------------------


template<class Real> inline
Point3_base<Real> AMatrix4x4<Real>::project(const Point3_base<Real> &v) const
{
    Point3_base<Real> tmp =  Point3_base<Real>(
                m[0] * v.x + m[1] * v.y + m[ 2] * v.z + m[ 3],
                m[4] * v.x + m[5] * v.y + m[ 6] * v.z + m[ 7],
                m[8] * v.x + m[9] * v.y + m[10] * v.z + m[11]);

    return tmp / (m[12] * v.x + m[13] * v.y + m[14] * v.z + m[15]);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::operator*(const AMatrix4x4<Real>& t) const
{
    AMatrix4x4<Real> res;
    for(int i = 0; i < 4; i++){
        int j = i*4;
        res[j+0] = m[j] * t.m[0] + m[j+1] * t.m[4] + m[j+2] * t.m[ 8] + m[j+3] * t.m[12];
        res[j+1] = m[j] * t.m[1] + m[j+1] * t.m[5] + m[j+2] * t.m[ 9] + m[j+3] * t.m[13];
        res[j+2] = m[j] * t.m[2] + m[j+1] * t.m[6] + m[j+2] * t.m[10] + m[j+3] * t.m[14];
        res[j+3] = m[j] * t.m[3] + m[j+1] * t.m[7] + m[j+2] * t.m[11] + m[j+3] * t.m[15];
    }
    return res;
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real>& AMatrix4x4<Real>::operator*=(const AMatrix4x4& t)
{
    (*this) = (*this) * t;
    return (*this);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::operator*(Real x) const
{
    AMatrix4x4<Real> res;
    for(int i = 0; i < 16; i++){
        res[i] = m[i] * x;
    }
    return res;
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::operator+(const AMatrix4x4<Real>& t) const
{
    AMatrix4x4<Real> res;
    for(int i = 0; i < 16; i++){
        res[i] = m[i] + t.m[i];
    }
    return res;
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real>& AMatrix4x4<Real>::operator+=(const AMatrix4x4<Real>& t)
{
    (*this) = (*this) + t;
    return (*this);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::operator-(const AMatrix4x4<Real>& t) const
{
    AMatrix4x4<Real> res;
    for(int i = 0; i < 16; i++){
        res[i] = m[i] - t.m[i];
    }
    return res;
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real>& AMatrix4x4<Real>::operator-=(const AMatrix4x4<Real>& t)
{
    (*this) = (*this) - t;
    return (*this);
}

// -----------------------------------------------------------------------------
/// @name Getters
// -----------------------------------------------------------------------------



template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::transpose() const
{
    return AMatrix4x4<Real>(
                m[0], m[4], m[ 8], m[12],
                m[1], m[5], m[ 9], m[13],
                m[2], m[6], m[10], m[14],
                m[3], m[7], m[11], m[15]);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::fast_inverse() const
{
    Matrix3x3<Real> a(
                m[0], m[1], m[ 2],
                m[4], m[5], m[ 6],
                m[8], m[9], m[10]);

    Vector3<Real> b(m[3], m[7], m[11]);
    Matrix3x3<Real> x = a.inverse();
    Vector3<Real> y = x * b;
    return AMatrix4x4<Real>(
                x.a, x.b, x.c, -y.x,
                x.d, x.e, x.f, -y.y,
                x.g, x.h, x.i, -y.z,
                Real(0), Real(0), Real(0),  Real(1));
}

// -----------------------------------------------------------------------------


template<class Real> inline
Real MINOR(const AMatrix4x4<Real>& m, const int r0, const int r1, const int r2, const int c0, const int c1, const int c2)
{
    return m[4*r0+c0] * (m[4*r1+c1] * m[4*r2+c2] - m[4*r2+c1] * m[4*r1+c2]) -
           m[4*r0+c1] * (m[4*r1+c0] * m[4*r2+c2] - m[4*r2+c0] * m[4*r1+c2]) +
           m[4*r0+c2] * (m[4*r1+c0] * m[4*r2+c1] - m[4*r2+c0] * m[4*r1+c1]);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> adjoint(const AMatrix4x4<Real>& m)
{
    return AMatrix4x4<Real>(
                MINOR(m,1,2,3,1,2,3), -MINOR(m,0,2,3,1,2,3),  MINOR(m,0,1,3,1,2,3), -MINOR(m,0,1,2,1,2,3),
               -MINOR(m,1,2,3,0,2,3),  MINOR(m,0,2,3,0,2,3), -MINOR(m,0,1,3,0,2,3),  MINOR(m,0,1,2,0,2,3),
                MINOR(m,1,2,3,0,1,3), -MINOR(m,0,2,3,0,1,3),  MINOR(m,0,1,3,0,1,3), -MINOR(m,0,1,2,0,1,3),
               -MINOR(m,1,2,3,0,1,2),  MINOR(m,0,2,3,0,1,2), -MINOR(m,0,1,3,0,1,2),  MINOR(m,0,1,2,0,1,2));
}

// -----------------------------------------------------------------------------


template<class Real> inline
Real AMatrix4x4<Real>::det() const
{
    return m[0] * MINOR(*this, 1, 2, 3, 1, 2, 3) -
           m[1] * MINOR(*this, 1, 2, 3, 0, 2, 3) +
           m[2] * MINOR(*this, 1, 2, 3, 0, 1, 3) -
           m[3] * MINOR(*this, 1, 2, 3, 0, 1, 2);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::full_inverse() const
{
    return adjoint(*this) * (Real(1) / det());
}

template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::normalized() const
{
    return AMatrix4x4<Real>(get_mat3().normalized(), get_translation());
}

// -----------------------------------------------------------------------------

 template<class Real> inline
bool AMatrix4x4<Real>::is_frame_ortho(Real eps) const
{
    return fabsf( x().dot( y() ) ) < eps &&
           fabsf( x().dot( z() ) ) < eps &&
           fabsf( y().dot( z() ) ) < eps;
}

// -----------------------------------------------------------------------------

template<class Real> inline
void AMatrix4x4<Real>::print() const
{
    tbx_printf("%f %f %f %f\n", m[0 ], m[1 ], m[2 ], m[3 ] );
    tbx_printf("%f %f %f %f\n", m[4 ], m[5 ], m[6 ], m[7 ] );
    tbx_printf("%f %f %f %f\n", m[8 ], m[9 ], m[10], m[11] );
    tbx_printf("%f %f %f %f\n", m[12], m[13], m[14], m[15] );
}

// -----------------------------------------------------------------------------
/*
template<class Real> inline
std::ostream& operator<< ( std::ostream& ofs, const AMatrix4x4<Real>& tr )
{
    ofs << tr.m[0 ] << ", " << tr.m[1 ] << ", " << tr.m[2 ] << ", " << tr.m[3 ] << "\n";
    ofs << tr.m[4 ] << ", " << tr.m[5 ] << ", " << tr.m[6 ] << ", " << tr.m[7 ] << "\n";
    ofs << tr.m[8 ] << ", " << tr.m[9 ] << ", " << tr.m[10] << ", " << tr.m[11] << "\n";
    ofs << tr.m[12] << ", " << tr.m[13] << ", " << tr.m[14] << ", " << tr.m[15];
    return ofs;
}*/

// -------------------------------------------------------------------------
/// @name Static transformation constructors (translation/rotation/scale)
// -------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::translate(Real dx, Real dy, Real dz)
{
    return AMatrix4x4<Real>(Real(1), Real(0), Real(0), dx,
                            Real(0), Real(1), Real(0), dy,
                            Real(0), Real(0), Real(1), dz,
                            Real(0), Real(0), Real(0), Real(1));
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::translate(const Vector3<Real>& v)
{
    return AMatrix4x4<Real>::translate(v.x, v.y, v.z);
}


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::scale(Real sx, Real sy, Real sz)
{
    return AMatrix4x4<Real>(
                sx     , Real(0), Real(0), Real(0),
                Real(0), sy     , Real(0), Real(0),
                Real(0), Real(0), sz     , Real(0),
                Real(0), Real(0), Real(0), Real(1));
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::scale(const Vector3<Real>& v)
{
    return AMatrix4x4<Real>::scale(v.x, v.y, v.z);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::scale(Real s)
{
    return AMatrix4x4<Real>::scale(s, s, s);
}

// -----------------------------------------------------------------------------

/// @return the scale matrix given scale factors in 'v' and
/// scale origin 'center'

template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::scale(const Vector3<Real>& center, const Vector3<Real>& v)
{
    AMatrix4x4<Real> sc = AMatrix4x4<Real>::scale( v );
    return AMatrix4x4<Real>::translate(center) * sc * AMatrix4x4<Real>::translate(-center);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::scale(const Vector3<Real>& center, Real s)
{
    AMatrix4x4<Real> sc = AMatrix4x4<Real>::scale(s);
    return AMatrix4x4<Real>::translate(center) * sc * AMatrix4x4<Real>::translate(-center);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::rotate(
        const Vector3<Real>& center,
        const Vector3<Real>& axis,
        Real radian_angle,
        const Matrix3x3<Real>& frame)
{
    AMatrix4x4<Real> r(frame * Matrix3x3<Real>::rotate(axis, radian_angle) * frame.inverse());
    return AMatrix4x4<Real>::translate(center) * r * AMatrix4x4<Real>::translate(-center);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::rotate(
        const Vector3<Real>& center,
        const Vector3<Real>& axis,
        Real radian_angle)
{
    AMatrix4x4<Real> r(Matrix3x3<Real>::rotate(axis, radian_angle));
    return AMatrix4x4<Real>::translate(center) * r * AMatrix4x4<Real>::translate(-center);
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::rotate(const Vector3<Real>& axis, Real radian_angle)
{
    return AMatrix4x4<Real>(Matrix3x3<Real>::rotate(axis, radian_angle));
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::identity()
{
    return AMatrix4x4<Real>(
                Real(1), Real(0), Real(0), Real(0),
                Real(0), Real(1), Real(0), Real(0),
                Real(0), Real(0), Real(1), Real(0),
                Real(0), Real(0), Real(0), Real(1));
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::null()
{
    return AMatrix4x4<Real>(
                Real(0), Real(0), Real(0), Real(0),
                Real(0), Real(0), Real(0), Real(0),
                Real(0), Real(0), Real(0), Real(0),
                Real(0), Real(0), Real(0), Real(0));
}

// -----------------------------------------------------------------------------


template<class Real> inline
AMatrix4x4<Real> AMatrix4x4<Real>::coordinate_system(const Vector3<Real>& org, const Vector3<Real>& x_axis)
{
    return AMatrix4x4(Matrix3x3<Real>::coordinate_system( x_axis), org);
}

}// END tbx NAMESPACE ==========================================================
