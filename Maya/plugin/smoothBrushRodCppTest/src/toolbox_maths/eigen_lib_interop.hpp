#ifndef TOOL_BOX_EIGEN_INTEROP_HPP
#define TOOL_BOX_EIGEN_INTEROP_HPP



#include <toolbox_maths/matrix3x3.hpp>
#include <toolbox_maths/quat.hpp>
#include <Eigen/Core>
#include <Eigen/Geometry>

/**
    Convertions between the Eigen lib and our types.
*/

// =============================================================================
namespace tbx {
// =============================================================================

template<class Real> static inline
Eigen::Vector3d to_eigen_Vector3d(const tbx::Vector3<Real>& v){
    return Eigen::Vector3d(double(v.x), double(v.y), double(v.z));
}

// -----------------------------------------------------------------------------

template<class Real>
static inline
Eigen::Matrix3d to_eigen_Matrix3d(const tbx::Matrix3x3<Real>& m){
    Eigen::Matrix3d mat;
    mat << double(m.a), double(m.b), double(m.c),
           double(m.d), double(m.e), double(m.f),
           double(m.g), double(m.h), double(m.i);
    return mat;
}

// -----------------------------------------------------------------------------

static inline
tbx::Vec3 to_vec3(Eigen::Vector3f v){ return tbx::Vec3( v(0), v(1), v(2)); }

// -----------------------------------------------------------------------------

static inline
tbx::Vec3 to_vec3(const Eigen::Vector3d& v){
    return tbx::Vec3(float(v(0)), float(v(1)), float(v(2)));
}

// -----------------------------------------------------------------------------

static inline
tbx::Mat3 to_mat3(const Eigen::Matrix3d& m){
    tbx::Mat3 mat(float(m(0,0)), float(m(0,1)), float(m(0,2)),
                  float(m(1,0)), float(m(1,1)), float(m(1,2)),
                  float(m(2,0)), float(m(2,1)), float(m(2,2)));
    return mat;
}

// -----------------------------------------------------------------------------

static inline
tbx::Mat3 to_mat3(const Eigen::Matrix3f& m){
    tbx::Mat3 mat((m(0,0)), (m(0,1)), (m(0,2)),
                  (m(1,0)), (m(1,1)), (m(1,2)),
                  (m(2,0)), (m(2,1)), (m(2,2)));
    return mat;
}

// -----------------------------------------------------------------------------

static inline
std::string to_string(Eigen::ComputationInfo info){
    switch(info){
    case Eigen::Success: return ("Success, Computation was successful.");
    case Eigen::NumericalIssue: return ("NumericalIssue, The provided data did not satisfy the prerequisites.");
    case Eigen::NoConvergence: return ("InvalidInput, Iterative procedure did not converge.");
    case Eigen::InvalidInput: return ("InvalidInput, The inputs are invalid, or the algorithm has been improperly called. When assertions are enabled, such errors trigger an assert.");
    }
    return ("UnknownError(")+std::to_string(int(info))+("), maybe this routine is not up to date check Eigen documentation");
}

}// END tbx ====================================================================

#include "toolbox_maths/settings_end.hpp"

#endif // TOOL_BOX_EIGEN_INTEROP_HPP
