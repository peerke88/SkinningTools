#pragma once

/**
 *  Factorize typedefs and forward definitions of various types of our math
 *  librarie; This is useful in case of cycling dependencies.
 *
 *  If we rename something this helps centralizing the changes.
*/

// =============================================================================
namespace tbx {
// =============================================================================

template <class Real> struct Vector4;
/// @brief 4 dimensional vector (floats)
typedef Vector4<float> Vec4;
/// @brief 4 dimensional vector (doubles)
typedef Vector4<double> Vec4_d;

// -----------------------------------------------------------------------------

template<class Real> struct Point3_base;
/// @brief 3 dimensional point (floats)
typedef Point3_base<float> Point3;
/// @brief 3 dimensional point (doubles)
typedef Point3_base<double> Point3_d;

// -----------------------------------------------------------------------------

template <class Real> struct Vector3;
/// @brief 3 dimensional vector (floats)
typedef Vector3<float> Vec3;
/// @brief 3 dimensional vector (doubles)
typedef Vector3<double> Vec3_d;
struct Vector3_i;
/// @brief 3 dimensional vector (ints)
typedef Vector3_i Vec3_i;

// -----------------------------------------------------------------------------

struct Vector2_i;
/// @brief 2 dimensional vector (ints)
typedef Vector2_i Vec2_i;

template <class Real> struct Vector2;
/// @brief 2 dimensional vector (floats)
typedef Vector2<float> Vec2;
/// @brief 2 dimensional vector (doubles)
typedef Vector2<double> Vec2_d;

// -----------------------------------------------------------------------------

template <class Real> struct Matrix3x3;
///@brief Matrix 3x3 (floats)
typedef Matrix3x3<float> Mat3;
///@brief Matrix 3x3 (doubles)
typedef Matrix3x3<double> Mat3_d;

// -----------------------------------------------------------------------------

template <class Real> struct Matrix2x2;
/// @brief Matrix 2x2 (floats)
typedef Matrix2x2<float> Mat2;
/// @brief Matrix 2x2 (doubles)
typedef Matrix2x2<double> Mat2_d;

// -----------------------------------------------------------------------------

template <class Real> class AMatrix4x4;
typedef AMatrix4x4<float> Transfo;
typedef AMatrix4x4<double> Transfo_d;

// -----------------------------------------------------------------------------

///@brief The sole purpose of a Point_vec3 is to indicate that a vec3 should
/// be interpreted as a point when processed by some routine. For instance,
/// Mat4x4 * Point(vec3) should be equivalent to
/// Mat4x4 * Vec4(vec3.x, vec3.y, vec3.z, 1.0)
template <class Real>
struct Point_vec3 {
    const Vector3<Real>& _data;
    Point_vec3(const Vector3<Real>& v) : _data(v) {}
};

/// build a Point_vec3 without the need to specify the template parameter:
template <class Real> inline
Point_vec3<Real> Point(const Vector3<Real>& v) { return Point_vec3<Real>(v);  }

}// END tbx NAMESPACE ==========================================================

#include "toolbox_maths/settings_end.hpp"
