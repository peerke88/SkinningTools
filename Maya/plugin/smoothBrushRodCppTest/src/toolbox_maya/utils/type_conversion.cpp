#include "toolbox_maya/utils/type_conversion.hpp"

#include "toolbox_maya/utils/maya_error.hpp"

// =============================================================================
namespace tbx_maya {
// =============================================================================

tbx::Transfo to_transfo(const MMatrix& mmat)
{
    tbx::Transfo mat;
#if 1
    mat[ 0] = (float) mmat[0][0]; mat[ 1] = (float) mmat[1][0];
    mat[ 2] = (float) mmat[2][0]; mat[ 3] = (float) mmat[3][0];
    mat[ 4] = (float) mmat[0][1]; mat[ 5] = (float) mmat[1][1];
    mat[ 6] = (float) mmat[2][1]; mat[ 7] = (float) mmat[3][1];
    mat[ 8] = (float) mmat[0][2]; mat[ 9] = (float) mmat[1][2];
    mat[10] = (float) mmat[2][2]; mat[11] = (float) mmat[3][2];
    mat[12] = (float) mmat[0][3]; mat[13] = (float) mmat[1][3];
    mat[14] = (float) mmat[2][3]; mat[15] = (float) mmat[3][3];
#else

    for (unsigned j = 0; j < 4; ++j){
        for (unsigned k = 0; k < 4; ++k){
            mat(j, k) = static_cast<float>( mmat[k][j] );
        }
    }
#endif
    return mat;
}

// -----------------------------------------------------------------------------

std::vector<MString> to_stdvector(const MStringArray& array) {
    std::vector<MString> vec(array.length());
    for(unsigned i = 0; i < vec.size(); ++i)
        vec[i] = array[i];
    return vec;
}

// -----------------------------------------------------------------------------

tbx::Bbox3 to_bbox3(const MBoundingBox& maya_bbox)
{
    return tbx::Bbox3(to_vec3(maya_bbox.min()), to_vec3(maya_bbox.max()));
}

// -----------------------------------------------------------------------------

MPointArray to_MPointArray(const std::vector<tbx::Vec3>& vertex_list){
    MPointArray array;
    mayaCheck( array.setLength( unsigned(vertex_list.size()) ) );
    for(unsigned i = 0; i < vertex_list.size(); ++i)
           array[i] = to_MPoint(vertex_list[i]);
    return array;
}

}// END tbx_maya Namespace =====================================================
