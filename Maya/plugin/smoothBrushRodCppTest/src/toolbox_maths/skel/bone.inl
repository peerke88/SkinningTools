#include "toolbox_maths/skel/bone.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

inline Bone::Bone(bone::Id i)
    : _bone_id(i)
    , _bone_role(bone::Role::eUNDEF)
{
    set_start_end(tbx::Point3::zero(), tbx::Point3::zero());
}

// -----------------------------------------------------------------------------
// Getters
// -----------------------------------------------------------------------------

inline tbx::Point3 Bone::org() const{ return _org;}

inline tbx::Point3 Bone::end() const{ return _org + _dir;}

inline float Bone::length() const{ return _length;}

inline tbx::Vec3 Bone::dir() const{ return _dir;}

inline bone::Id Bone::id() const { return _bone_id;}

inline bone::Role Bone::role() const { return _bone_role; }

// -----------------------------------------------------------------------------
// Setters
// -----------------------------------------------------------------------------

inline void Bone::set_length(float l){ _length = l;}

inline void Bone::set_id(bone::Id i){ _bone_id = i;}

inline void Bone::set_role(bone::Role t){ _bone_role = t; }

inline void Bone::set_start_end(const tbx::Point3& p0, const tbx::Point3& p1)
{
    _org = p0;
    _dir = p1 - p0;
    _length = _dir.norm();
}

// -----------------------------------------------------------------------------

inline void Bone::set_orientation(const tbx::Point3& org, const tbx::Vec3& dir)
{
    _org = org;
    _dir = dir.normalized() * _length;
}


// -----------------------------------------------------------------------------
// Distance computation
// -----------------------------------------------------------------------------

inline float Bone::parametric_dist_from_origin(const tbx::Point3& p) const
{
    const tbx::Vec3 op = p - _org;
    return op.dot(_dir.normalized());
}

// -----------------------------------------------------------------------------

inline float Bone::dist_ortho_from_line(const tbx::Point3& p) const
{
    const tbx::Vec3 op = p - _org;
    return op.cross(_dir.normalized()).norm();
}

// -----------------------------------------------------------------------------

inline float Bone::dist_sq_from_segment(const tbx::Point3& p) const {
    tbx::Vec3 op = p - _org;
    float x = op.dot(_dir) / (_length * _length);
    x = fminf(1.f, fmaxf(0.f, x));
    tbx::Point3 proj = _org + _dir * x;
    float d = proj.distance_squared(p);
    return d;
}

// -----------------------------------------------------------------------------

inline float Bone::dist_from_segment(const tbx::Point3& p) const {
    return sqrtf( dist_sq_from_segment( p ) );
}

// -----------------------------------------------------------------------------

inline tbx::Point3 Bone::project_on_segment(const tbx::Point3& p) const
{
    const tbx::Vec3 op = p - _org;
    float d = op.dot(_dir.normalized()); // projected dist from origin

    if(d < 0)            return _org;
    else if(d > _length) return _org + _dir;
    else                 return _org + _dir.normalized() * d;
}

// -----------------------------------------------------------------------------

 inline
float Bone::dist_from_bone(const Bone& bone) const {
    return (this->org() - bone.org()).norm() + (this->end() - bone.end()).norm();
}


} // END tbx NAMESPACE =========================================================
