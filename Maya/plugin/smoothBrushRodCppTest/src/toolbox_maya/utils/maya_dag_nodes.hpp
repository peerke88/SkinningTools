#ifndef TOOLBOX_MAYA_MAYA_DAG_NODES_HPP
#define TOOLBOX_MAYA_MAYA_DAG_NODES_HPP

#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MDagPath.h>
#include <maya/MBoundingBox.h>
#include <maya/MMatrix.h>

#include <vector>
#include "toolbox_maths/bbox3.hpp"

/**
    @brief Wrappers around MFnDagNode
*/

// =============================================================================
namespace tbx_maya {
// =============================================================================

// -----------------------------------------------------------------------------
/// @name Tools MFnDagNode
// -----------------------------------------------------------------------------

/// Copy the (MFnDagNode) node
/// @return the newly created copy
MObject copy(MObject node);

/// @return transform associated to a shape
MObject get_transform(MObject node);

/// @return the MObject identified by the string 'node_name'
MObject get_MObject(const MString& node_name);

/// @return the MObject identified by the dag path
MObject get_MObject(const MDagPath& dag_path);

/// @return the MObject from an MFn function set of a dag node
//inline MObject get_MObject(const MFnDagNode& fn_set)
//{
//    MStatus status = MS::kSuccess;
//    MDagPath path = fn_set.dagPath(&status);
//    mayaCheck(status);
//    return get_MObject(path);
//}

/// @return if the dag path is valid ( path.isValid() )
bool is_valid(const MDagPath& path);

/// @return list of MObject identified by the list of MString 'array'
std::vector<MObject> get_MObjects(const MStringArray& array);

/// @return true if node is a shape or a shape child shape exists
bool has_shape(MObject node);
bool has_shape(const MDagPath& path);

/// @return the shape node underneath 'node' (or itself if already a shape)
/// @warning
///     @item fails if "node" can't be converted to a shape.
///     You must just first check (has_shape(node) == true)
///     @item fails if "node" has several shapes
MObject get_shape(MObject node);
MDagPath get_shape(const MDagPath& path);

unsigned get_nb_shapes(const MDagPath& dag_path);
unsigned get_nb_shapes(const MObject& node);

std::vector<MObject> get_all_shapes(MObject node);
std::vector<MDagPath> get_all_shapes(const MDagPath& path);

MDagPath get_MDagPath(const MObject& obj);
MDagPath get_MDagPath(const MString& path);

///@warning must be a dag object other nodes will be ignored
MString get_dag_long_name(const MObject& obj);
MString get_dag_long_name(const MDagPath& path);
MString get_dag_long_name(const MString& name);

// Shortest unique name / see maya_dependency_nodes.hpp to get only the name
// of the object with get_name()
///@warning must be a dag object other nodes will be ignored
MString get_short_name(const MObject& obj);
MString get_short_name(const MDagPath& path);
MString get_short_name(const MString& name);

void set_parent(MObject  parent, MObject child);
void set_parent(MDagPath parent, MObject child);

// Its a strange thing but in Maya API you can get more than one parent
// ?!*$ !-٩(๏̯๏̯)۶_-!
std::vector<MDagPath> get_parents (const MDagPath& dag_node);
/// @return first valid parent or invalid
MDagPath get_the_parent(const MDagPath& dag_node);

std::vector<MDagPath> get_children(const MDagPath& dag_node);

// -----------------------------------------------------------------------------

tbx::Bbox3 get_bbox3(MObject dag_obj);
MBoundingBox get_MBoundingBox(MObject dag_obj);

// -----------------------------------------------------------------------------

/// @return dag node world MMatrix (dag node only).
MMatrix world_mmatrix(const MObject dag_node);
/// @return dag node world MMatrix.
MMatrix world_mmatrix(const MDagPath& path);
/// @return dag node world transformation.
tbx::Transfo world_transfo(const MDagPath& path);
/// @return dag node local MMatrix.
MMatrix local_mmatrix(const MDagPath& path);
/// @return dag node local transformation.
tbx::Transfo local_transfo(const MDagPath& path);

// ----------

/// Lock node's attributes "translate", "rotate", "scale"
void lock_transforms(MObject node);

/// @brief Apply current transformation to the object and set it to identiy
void freeze_transforms(MObject node);


}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_MAYA_DAG_NODES_HPP
