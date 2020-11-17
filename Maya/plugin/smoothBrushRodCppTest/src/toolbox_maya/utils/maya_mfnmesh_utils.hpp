#ifndef TOOLBOX_MAYA_MAYA_MFNMESH_UTILS_HPP
#define TOOLBOX_MAYA_MAYA_MFNMESH_UTILS_HPP

#include <maya/MDagPath.h>
#include <maya/MPointArray.h>

#include <toolbox_maths/vector3.hpp>

#include <vector>

#include "toolbox_maya/utils/forward_declaration.hpp"
TBX_MAYA_FORWARD_DECLARATION(class MFnMesh);

/**
    @brief Wrappers around MFnMesh
*/
// =============================================================================
namespace tbx_maya {
// =============================================================================

// -----------------------------------------------------------------------------
/// @name Selection
// -----------------------------------------------------------------------------

/// @param type : MFn::kMeshEdgeComponent, MFn::kMeshPolygonComponent etc.
bool get_selected_components_of_type(MFn::Type type,
                                     const MDagPath& path,
                                     MObject& component);

/// Get the list of vertices currently selected.
/// Usage:
/// @code
/** MObject component;
    if( has_selected_vertices(mesh_path, component) )
    {
        MItMeshVertex vert_it(path, component, &status);
        mayaCheck( status );
        for ( ; !vert_it.isDone() ; vert_it.next() )
        {
            int vidx = vert_it.index(&status);
            mayaCheck(status);
            // vidx can be used with tbx_maya::Maya_mesh :D
        }
    }
    @endcode
*/
/// @warning component is only valid when true is returned.
/// @param path : dag path to the mesh shape we want to check selected verts
/// @param component : currently selected component (vertex, face etc.)
/// @return true if we can find path in Maya's active selection list
/// and if at least one vertex component is selected.
bool has_selected_vertices(const MDagPath& path, MObject& component);
bool has_selected_faces   (const MDagPath& path, MObject& component);
bool has_selected_edges   (const MDagPath& path, MObject& component);

/// @return list of selected vertices of the mesh 'mesh_shape'
void get_selected_vertices(std::vector<int>& vertex_list, MObject mesh_shape);

/// Check currently selected components (face, vertex etc.)
/// and convert everything to vertex indices
void get_selection_and_convert_to_vertex(
    std::vector<int>& vertex_list,
    MObject mesh_shape);

// -----------------------------------------------------------------------------
/// @name Vertex indices
// -----------------------------------------------------------------------------

/// @return number of vertices of the mesh 'mesh_shape'
int get_nb_vertices(MObject mesh_shape);
int get_nb_vertices(const MFnMesh& mesh);

void set_points(MObject mesh_shape, MPointArray& new_points);
void set_points(MObject mesh_shape, const std::vector<tbx::Vec3>& new_points);

}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_MAYA_MFNMESH_UTILS_HPP
