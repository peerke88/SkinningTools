#pragma once

#include "toolbox_maths/vector3.hpp"
#include "toolbox_maths/point3.hpp"
#include "toolbox_config/tbx_assert.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

struct Ray {
    Point3 _pos;
    Vec3  _dir;

     inline
    Ray() : _pos( Point3(0.f, 0.f, 0.f) ), _dir( Vec3::zero() ) {  }

     inline
    Ray(const Point3& pos_, const Vec3& dir_) :
        _pos( pos_ ), _dir( dir_ )
    { }

    /// to set the position

    inline void set_pos(const Point3& pos_) { _pos = pos_; }

    /// to set the direction

    inline void set_dir(const Vec3& dir_) { _dir = dir_; }

    /// get the point at coordinate t along the ray

    inline Point3 operator ()(const float t_) const {
        return _pos + _dir * t_;
    }
};

}// END tbx NAMESPACE ==========================================================

#include "toolbox_maths/settings_end.hpp"
