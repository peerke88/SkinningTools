#ifndef TOOLBOX_BONE_HPP
#define TOOLBOX_BONE_HPP

#include "toolbox_config/tbx_assert.hpp"
#include "toolbox_maths/point3.hpp"
#include "toolbox_maths/transfo.hpp"
#include "toolbox_maths/skel/bone_type.hpp"


// =============================================================================
namespace tbx {
// =============================================================================

/**
  @brief A class representing a bone

  A bone defines a segment between two 3D points (_org, end).
  Attribute '_org' defines the starting point of the segment.

  The second ending point can be computed <code>end = _dir + _org;</code>
  Notice _dir magnitude equals the length() of the bone.

  Bones direction points toward the skeleton leaves.
  Usually bones at the leaves have length == 0

  @code
       _org                 (_org + _dir) == end
         +------------------------>
      joint                    son_joint (if any)
  @endcode

  @see anim::Skeleton
*/
class Bone {
public:
    
    explicit inline Bone(bone::Id i = -1);

    
    /// Construct a bone between two points
    explicit Bone(const tbx::Point3& p1, const tbx::Point3& p2,
                  bone::Id i = -1, bone::Role role = bone::Role::eUNDEF);

    
    /// Construct a bone with origin and direction.
    explicit  Bone(const tbx::Point3& org, const tbx::Vec3& dir, float length,
                   bone::Id i = -1, bone::Role role = bone::Role::eUNDEF);

    ~Bone(){ }

    // -------------------------------------------------------------------------
    /// @name Getters
    // -------------------------------------------------------------------------

    /// Get the bone's origin position
     inline tbx::Point3 org() const;

    /// Get the bone's end position
     inline tbx::Point3 end() const;

    /// Get the bone length
     inline float length() const;

    /// Get the bone direction (not normalized)
    /// org() + dir() == end_point_bone
     inline tbx::Vec3 dir() const;

    /// Gets the bone ID from the skeleton
     inline bone::Id id() const;

    /// Gets the bone role in the skeleton's hierachy
     inline bone::Role role() const;

    // -------------------------------------------------------------------------
    /// @name Setters
    // -------------------------------------------------------------------------

    /// Change the bone length.
     void set_length (float  l );

    /// Set the start and end point of the bone.
    
    void set_start_end(const tbx::Point3& p0, const tbx::Point3& p1);

    /// Set the start point and direction of the bone.
    /// @param dir : direction of the bone (norm is ignored)
    
    void set_orientation(const tbx::Point3& org, const tbx::Vec3& dir);

    /// Set the bone ID in the skeleton.
    void set_id(bone::Id i);

    /// Set the role of the bone (leaf, root, internal)
    void set_role(bone::Role t);

    // -------------------------------------------------------------------------
    /// @name Work on infinite line
    // -------------------------------------------------------------------------

    /// 'p' is projected on the bone line,
    /// then it returns the distance from the  origine '_org'
     inline
    float parametric_dist_from_origin(const tbx::Point3& p) const;

    /// Orthogonal distance from the bone line to a point
     inline
    float dist_ortho_from_line(const tbx::Point3& p) const;


    // -------------------------------------------------------------------------
    /// @name Work on segment
    // -------------------------------------------------------------------------

    /// squared distance from a point 'p'
    /// to the bone's segment (_org; _org+_dir).
     inline
    float dist_sq_from_segment(const tbx::Point3& p) const;

    /// euclidean distance from a point 'p'
    /// to the bone's segment (_org; _org+_dir).
     inline
    float dist_from_segment(const tbx::Point3& p) const;

    /// project p on the bone segment if the projection is outside the segment
    /// then returns the origin or the end point of the bone.
     inline
    tbx::Point3 project_on_segment(const tbx::Point3& p) const;

    ///@return from another fellow bone:
    /// (org0 - org1).norm() + (end0 - end1).norm()
     inline
    float dist_from_bone(const Bone& bone) const;

    // -------------------------------------------------------------------------
    /// @name Misc
    // -------------------------------------------------------------------------

    /// Get the local frame of the bone. This method only guarantes to generate
    /// a frame with an x direction parallel to the bone and centered about '_org'
    
    tbx::Transfo get_frame() const;

    ///@return the bone transformed by the transformation 'tr'
    Bone transform(const tbx::Transfo& tr) const;

protected:
    // -------------------------------------------------------------------------
    /// @name Characteristics
    // -------------------------------------------------------------------------
    tbx::Point3 _org;       ///< Bone origin (first joint position)
    tbx::Vec3   _dir;       ///< Bone direction towards its son if any (un-normalized)
    float       _length;    ///< Bone length (o + _dir.normalized*length = bone_end_point)

    // -------------------------------------------------------------------------
    /// @name Info related to the skelton
    // -------------------------------------------------------------------------

    /// Bone identifier in anim::Skeleton class
    /// or -1 if not referenced by a skeleton.
    bone::Id    _bone_id;

    /// Role in the skeleton's hierachy (leaf, root, internal)
    /// undef if not referenced by a skeleton
    bone::Role _bone_role;
};

} // END tbx NAMESPACE =========================================================

#include "toolbox_maths/skel/bone.inl"

#include "toolbox_maths/settings_end.hpp"

#endif // TOOLBOX_BONE_HPP
