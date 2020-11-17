#ifndef TOOLBOX_TYPE_CONVERSION_HPP
#define TOOLBOX_TYPE_CONVERSION_HPP

#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MMatrix.h>
#include <maya/MPoint.h>
#include <maya/MVector.h>
#include <maya/MBoundingBox.h>
#include <maya/MPointArray.h>
#include <maya/MColor.h>

// -----------------------------------------------------------------------------

#include <string>
#include <vector>

// -----------------------------------------------------------------------------

#include <toolbox_maths/vector3.hpp>
#include <toolbox_maths/transfo.hpp>
#include <toolbox_maths/bbox3.hpp>


// =============================================================================
namespace tbx_maya {
// =============================================================================

// -----------------------------------------------------------------------------
/// @name Type conversion (Maya API <-> Our internal types)
// -----------------------------------------------------------------------------

tbx::Bbox3   to_bbox3(const MBoundingBox& maya_bbox);
tbx::Transfo to_transfo(const MMatrix& mmat);

inline static MString     to_MString(const std::string& str){ return MString(str.c_str());                               }
inline static MPoint      to_MPoint (const tbx::Point3& p)  { return MPoint     ((float)p.x , (float)p.y , (float)p.z);  }
inline static MPoint      to_MPoint (const tbx::Vec3& v)    { return MPoint     ((float)v.x , (float)v.y , (float)v.z);  }
inline static MVector     to_MVector(const tbx::Vec3& v)    { return MVector    ((float)v.x , (float)v.y , (float)v.z);  }
inline static tbx::Vec3   to_vec3   (const MPoint& p)       { return tbx::Vec3  ((float)p.x , (float)p.y , (float)p.z);  }
inline static tbx::Vec3   to_vec3   (const MVector& v)      { return tbx::Vec3  ((float)v[0], (float)v[1], (float)v[2]); }
inline static std::string to_str    (const MString& str)    { return std::string(str.asChar());                          }

std::vector<MString> to_stdvector(const MStringArray& array);

MPointArray to_MPointArray(const std::vector<tbx::Vec3>& vertex_list);

/// @brief convert 'list' to a std::vector<MDagPath>
/// @warning ignores node that are note dag nodes (obviously...)
std::vector<MDagPath> to_stdvector(const MSelectionList& list);

MString to_str(const MSelectionList& list);

///@return the MArgList as a single string
MString to_str(const MArgList& args);


}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_TYPE_CONVERSION_HPP
