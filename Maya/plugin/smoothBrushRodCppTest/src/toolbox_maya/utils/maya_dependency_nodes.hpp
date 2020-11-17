#ifndef TOOLBOX_MAYA_MAYA_DEPENDENCY_NODES_HPP
#define TOOLBOX_MAYA_MAYA_DEPENDENCY_NODES_HPP

#include <maya/MString.h>
#include <maya/MObject.h>
#include <maya/MDagPath.h>
#include <maya/MTypeId.h>

/**
    @brief Wrappers around MFnDependencyNode
*/

// =============================================================================
namespace tbx_maya {
// =============================================================================

// -----------------------------------------------------------------------------
/// @name Tools MFnDependencyNode
// -----------------------------------------------------------------------------

/// @brief Create a shape node of a custom type, and return its interface.
///
/// The shape name will be suffixed with "Shape",
/// and the given name will be assigned to the surrounding transform.
/// If transfo_node_out is non-NULL, it will be set to the transform node.
template <typename T>
T* create_shape(MString name, MObject* transfo_node_out = nullptr);

/// @brief create and add a deformer node to the dependency graph.
/// Interface required:
/// T::_s_name
/// T::initialize_deformer();
/// @return the newly created deformer.
template <class T>
T* create_deformer(const MObject& mesh_shape, const MString& extra_args = "");

/// @brief Create and add a custom node to the dependency graph.
/// Interface required:
/// T::_s_name
/// @return the newly created node of type T.
template <class T>
T* create_node();

/// Get a user interface from a node, with type checking.
/// @return NULL On failure.
/// Dfm_implicit_skin* surface = get_interface_node<Dfm_implicit_skin>(node);
template <typename T>
inline T* get_interface_node(const MObject& node);

/// Delete a dependency node
void delete_node(MObject node);

/// @brief return true if the dependency node exists
bool node_exists(const MString& node_name);

/// @return name of the dependency node (or dag node)
MString get_name(MObject obj);

/// @return name of the dag node
MString get_name(MDagPath obj);

/// @return type id of the dependency node (or dag node)
MTypeId get_type_id(MObject obj);

/// @return type name of the dependency node (or dag node)
MString get_type_name(MObject obj);

} // END tbx_maya Namespace =====================================================

#include "toolbox_maya/utils/maya_error.hpp"
#include <maya/MGlobal.h>
#include <maya/MFnDependencyNode.h>

// =============================================================================
namespace tbx_maya {
// =============================================================================

template <class T>
T* create_node()
{
    MStatus status = MS::kSuccess;
    MFnDependencyNode dep_node_fn;
    MObject obj = dep_node_fn.create(T::_s_id, &status);
    mayaCheck(status);
    return get_interface_node<T>(obj);
}

// -----------------------------------------------------------------------------

template <typename T>
inline T* get_interface_node(const MObject& node)
{
    if (node.isNull())
        return nullptr;

    MStatus status;
    MFnDependencyNode node_fn(node, &status);
    mayaCheck(status);

    MTypeId expected_id = T::_s_id;
    MTypeId id = node_fn.typeId(&status);
    mayaCheck(status);
    mayaAssertMsg(expected_id == id, "Node has the wrong type");

    T* obj = dynamic_cast<T*>(node_fn.userNode(&status));
    mayaCheck(status);
    return obj;
}

} // END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_MAYA_DEPENDENCY_NODES_HPP
