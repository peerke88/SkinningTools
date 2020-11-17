#ifndef TOOLBOX_MAYA_MAYA_TRANSFORM_HPP
#define TOOLBOX_MAYA_MAYA_TRANSFORM_HPP

#include <maya/MString.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MObject.h>

#include <toolbox_maths/vector3.hpp>

/**
    @brief Wrappers around MFnTransform
*/
// =============================================================================
namespace tbx_maya {
// =============================================================================

// -----------------------------------------------------------------------------
/// @name MFnTransform tools
// -----------------------------------------------------------------------------


// todo : to be tested !!
MObject create_joint(const MMatrix& matrix,
                     const double3& orientation,
                     MTransformationMatrix::RotationOrder order,
                     bool segmentScaleCompensate);

/// @return a maya transform node named 'transform_name'
MObject create_transform(MString transform_name);

void translate_by(MObject transform, const tbx::Vec3& v);
void translate_by(MObject transform, const MVector& v);

///@note if transform is just a transform then returned MTransformationMatrix
/// will only hold 4x4 matrix information. If it is a kJoint then
/// MTransformationMatrix will also hold jointOrient attribute
/// (double3 + rotation order) and segmentScaleCompensate bool attribute.
/// (at least that's my theory)
MTransformationMatrix get_MTransformationMatrix(MObject transform);
void set_MTransformationMatrix(MObject transform, const MTransformationMatrix& transfo);

// 'transform' can be both MFnTransform or a kJoint
void set_MMatrix(MObject transform, const MMatrix& matrix);

}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_MAYA_TRANSFORM_HPP
