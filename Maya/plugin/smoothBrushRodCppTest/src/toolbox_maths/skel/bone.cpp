#include "toolbox_maths/skel/bone.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

Bone::Bone(const tbx::Point3 &p1,
           const tbx::Point3 &p2,
           bone::Id i ,
           bone::Role type)
    : _bone_id(i)
    , _bone_role(type)
{
    set_start_end(p1, p2);
}

// -----------------------------------------------------------------------------

Bone::Bone(const tbx::Point3& org,
           const tbx::Vec3& dir,
           float length,
           bone::Id i, bone::Role type)
    : _length( length )
    , _bone_id(i)
    , _bone_role(type)
{
    set_orientation(org, dir);
}

// -----------------------------------------------------------------------------

tbx::Transfo Bone::get_frame() const
{
    tbx::Vec3 x = _dir.normalized();
    tbx::Vec3 ortho = x.cross(tbx::Vec3(0.f, 1.f, 0.f));
    tbx::Vec3 z, y;
    if (ortho.norm_squared() < 1e-06f * 1e-06f)
    {
        ortho = tbx::Vec3(0.f, 0.f, 1.f).cross(x);
        y = ortho.normalized();
        z = x.cross(y).normalized();
    }
    else
    {
        z = ortho.normalized();
        y = z.cross(x).normalized();
    }

    return tbx::Transfo(tbx::Mat3(x, y, z), _org.to_vec3() );
}

// -----------------------------------------------------------------------------

Bone Bone::transform(const tbx::Transfo& tr) const
{
    tbx::Bone copy = *this;
    copy._org = tr * org();
    copy._dir = tr * dir();
    copy._length = copy._dir.norm();
    return copy;
}

} // END tbx NAMESPACE =========================================================

