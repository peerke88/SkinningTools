#include "toolbox_maya/utils/maya_transform.hpp"

#include <maya/MFnTransform.h>
#include <maya/MFnIkJoint.h>
#include <maya/MQuaternion.h>
#include <maya/MPlug.h>
#include "toolbox_maya/utils/maya_error.hpp"
#include "toolbox_maya/utils/type_conversion.hpp"
#include "toolbox_maya/utils/maya_dag_nodes.hpp"


// =============================================================================
namespace tbx_maya {
// =============================================================================


MObject create_joint(const MMatrix& matrix,
                     const double3& orientation,
                     MTransformationMatrix::RotationOrder order,
                     bool segmentScaleCompensate)
{
    MStatus status;
    MFnIkJoint fn_joint;
    MObject new_joint = fn_joint.create(MObject::kNullObj, &status);
    mayaCheck(status);

    fn_joint.setOrientation(orientation, order);
    MFnDependencyNode dg_fn ( new_joint );
    MPlug segment_comp_plug = dg_fn.findPlug( ("segmentScaleCompensate"), true, &status );
    mayaCheck(status);

    mayaCheck( fn_joint.set( matrix ) );

    mayaCheck( segment_comp_plug.setValue(segmentScaleCompensate) );
    return new_joint;
}

// -----------------------------------------------------------------------------

MObject create_transform(MString name)
{
    MStatus status;
    MFnTransform transform;
    MObject node = transform.create(MObject::kNullObj, &status);
    mayaCheck(status);

    transform.setName(name, false, &status);
    mayaCheck(status);
    return node;
}

// -----------------------------------------------------------------------------

void translate_by(MObject transform, const tbx::Vec3& v){
    translate_by(transform, to_MVector(v));
}

// ---

void translate_by(MObject transform, const MVector& v)
{
    MStatus status;
    MFnTransform fn_transform(get_transform( transform ), &status);
    mayaCheck( status );
    mayaCheck( fn_transform.translateBy( v, MSpace::kTransform) );
}

// -----------------------------------------------------------------------------

MTransformationMatrix get_MTransformationMatrix(MObject transform){
    MStatus status;
    MFnTransform fn_transform(get_transform( transform ), &status);
    mayaCheck( status );
    MTransformationMatrix transfo = fn_transform.transformation(&status);
    mayaCheck( status );
    return transfo;
}

// -----------------------------------------------------------------------------

void set_MTransformationMatrix(MObject transform, const MTransformationMatrix& transfo)
{
    MStatus status;
    MFnTransform fn_transform(get_transform( transform ), &status);
    mayaCheck( status );
    mayaCheck( fn_transform.set(transfo) );
}

// -----------------------------------------------------------------------------

void set_MMatrix(MObject transform, const MMatrix& matrix)
{
    MStatus status;
    transform = get_transform( transform );
    if( transform.hasFn(MFn::kJoint ) )
    {
        /*
         *  Because of a bug in Maya setting a joint to a MMatrix is a pain.
         *  Contrary to a standard tranformation that only contains a 4x4 matrix
         *  a Joint contains additional information:
         *  - joint orientation
         *  - 'segmentScaleCompensate' a boolean option.
         *  when doing:
         *  MFnTransform::set( const MMatrix& ) or MFnIkJoint::set( const MMatrix& )
         * any additional information such as joint orientation, or segment scale
         * optional are reset to default values... (identity and true)
         * Therefore we need to save and restore those values..
        */
        MFnIkJoint fn_transform(transform, &status);
        mayaCheck(status);
        MQuaternion quat;
        mayaCheck(fn_transform.getOrientation(quat));

        MFnDependencyNode dg_fn ( transform );
        MPlug segment_comp_plug = dg_fn.findPlug( ("segmentScaleCompensate"), true, &status );
        mayaCheck(status);

        bool seg_comp_value;
        mayaCheck( segment_comp_plug.getValue(seg_comp_value) );
        {
            mayaCheck( fn_transform.set( quat.asMatrix().inverse() * matrix ) );
        }
        // Restore values
        mayaCheck( fn_transform.setOrientation(quat) );
        segment_comp_plug.setBool( seg_comp_value);
    }
    else
    {
        MFnTransform fn_transform(transform, &status);
        mayaCheck( status );
        mayaCheck( fn_transform.set(matrix) );
    }
}

}// END tbx_maya Namespace =====================================================
