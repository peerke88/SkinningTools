#include "toolbox_maya/utils/maya_attributes.hpp"
// -----------

// =============================================================================
namespace tbx_maya {
// =============================================================================

template<class T> inline
T find_element_as(MArrayDataHandle array_handle, int logical_idx)
{
    MStatus status;
    mayaCheck( array_handle.jumpToElement(logical_idx) );
    MDataHandle item_handle = array_handle.inputValue(&status);
    mayaCheck(status);
    return attr_as<T>(item_handle);
}


// -----------------------------------------------------------------------------

template<class T> inline
T get_element_at(MArrayDataHandle array_handle, int physical_index)
{
    MStatus status;
    mayaCheck( array_handle.jumpToArrayElement(physical_index) );
    MDataHandle item_handle = array_handle.inputValue(&status);
    mayaCheck(status);
    return attr_as<T>(item_handle);
}

// -----------------------------------------------------------------------------

template<> inline MDataHandle plug_as(const MPlug& plug) {
    MStatus status;
    MDataHandle v;
#if MAYA_API_VERSION >= 20180000
    v = plug.asMDataHandle(&status);
#else
    v = plug.asMDataHandle(MDGContext::fsNormal, &status);
#endif
    mayaCheck(status);
    return v;
}

template<> inline int plug_as(const MPlug& plug) {
    MStatus status;
    int v;
#if MAYA_API_VERSION >= 20180000
    v = plug.asInt(&status);
#else
    v = plug.asInt(MDGContext::fsNormal, &status);
#endif
    mayaCheck(status);
    return v;
}

template<> inline short plug_as(const MPlug& plug) {
    MStatus status;
    short v;
#if MAYA_API_VERSION >= 20180000
    v = plug.asShort(&status);
#else
    v = plug.asShort(MDGContext::fsNormal, &status);
#endif
    mayaCheck(status);
    return v;
}

template<> inline float plug_as(const MPlug& plug) {
    MStatus status;
    float v;
#if MAYA_API_VERSION >= 20180000
    v = plug.asFloat(&status);
#else
    v = plug.asFloat(MDGContext::fsNormal, &status);
#endif
    mayaCheck(status);
    return v;
}

template<> inline bool plug_as(const MPlug& plug) {
    MStatus status;
    bool v;
#if MAYA_API_VERSION >= 20180000
    v = plug.asBool(&status);
#else
    v = plug.asBool(MDGContext::fsNormal, &status);
#endif
    mayaCheck(status);
    return v;
}

template<> inline char plug_as(const MPlug& plug) {
    MStatus status;
    char v;
#if MAYA_API_VERSION >= 20180000
    v = plug.asChar(&status);
#else
    v = plug.asChar(MDGContext::fsNormal, &status);
#endif
    mayaCheck(status);
    return v;
}

template<> inline double plug_as(const MPlug& plug) {
    MStatus status;
    double v;
#if MAYA_API_VERSION >= 20180000
    v = plug.asDouble(&status);
#else
    v = plug.asDouble(MDGContext::fsNormal, &status);
#endif
    mayaCheck(status);
    return v;
}

template<> inline MAngle plug_as(const MPlug& plug) {
    MStatus status;
    MAngle v;
#if MAYA_API_VERSION >= 20180000
    v = plug.asMAngle(&status);
#else
    v = plug.asMAngle(MDGContext::fsNormal, &status);
#endif
    mayaCheck(status);
    return v;
}

template<> inline MObject plug_as(const MPlug& plug)
{
    MStatus status;
    MObject object;
    #if MAYA_API_VERSION >= 20180000
        object = plug.asMObject( &status);
    #else
        object = plug.asMObject(MDGContext::fsNormal, &status);
    #endif
    mayaCheck(status);
    return object;
}

template<> inline tbx::Vec3 plug_as(const MPlug& plug)
{
    MStatus status;
    MObject obj;
    #if MAYA_API_VERSION >= 20180000
        obj = plug.asMObject( &status);
    #else
        obj = plug.asMObject(MDGContext::fsNormal, &status);
    #endif
    mayaCheck(status);

    MFnNumericData fn_mat(obj, &status);
    tbx::Vec3 v;
    mayaCheck( fn_mat.getData3Float(v.x, v.y, v.z) );
    return v;
}

template<> inline tbx::Point3 plug_as(const MPlug& plug)
{
    MStatus status;
    MObject obj;
    #if MAYA_API_VERSION >= 20180000
        obj = plug.asMObject( &status);
    #else
        obj = plug.asMObject(MDGContext::fsNormal, &status);
    #endif
    mayaCheck(status);

    MFnNumericData fn_mat(obj, &status);
    tbx::Point3 v;
    mayaCheck( fn_mat.getData3Float(v.x, v.y, v.z) );
    return v;
}

template<> inline MMatrix plug_as(const MPlug& plug)
{
    MStatus status;
    MObject obj;
    #if MAYA_API_VERSION >= 20180000
        obj = plug.asMObject( &status);
    #else
        obj = plug.asMObject(MDGContext::fsNormal, &status);
    #endif
    mayaCheck(status);

    MFnMatrixData fn_mat(obj, &status);
    mayaCheck(status);
    MMatrix mat = fn_mat.matrix(&status);
    mayaCheck(status);
    return mat;
}

template<> inline MTransformationMatrix plug_as(const MPlug& plug)
{
    MStatus status;
    MObject obj;
    #if MAYA_API_VERSION >= 20180000
        obj = plug.asMObject( &status);
    #else
        obj = plug.asMObject(MDGContext::fsNormal, &status);
    #endif
    mayaCheck(status);

    MFnMatrixData fn_mat(obj, &status);
    mayaCheck(status);
    MTransformationMatrix mat = fn_mat.transformation(&status);
    mayaCheck(status);
    return mat;
}

template<> inline MString plug_as(const MPlug& plug)
{
    // use MFnStringData ?
    MStatus status;
    MString string;
    #if MAYA_API_VERSION >= 20180000
        string = plug.asString( &status);
    #else
        string = plug.asString(MDGContext::fsNormal, &status);
    #endif
    mayaCheck(status);
    return string;
}

}// END tbx_maya Namespace =====================================================
