#include "toolbox_maya/utils/maya_mfnmesh_utils.hpp"

#include <maya/MGlobal.h>
#include <maya/MSelectionList.h>
#include <maya/MItSelectionList.h>
#include <maya/MItMeshPolygon.h>
#include <maya/MItMeshEdge.h>
#include <maya/MItMeshVertex.h>
#include <maya/MFnMesh.h>

#include "toolbox_maya/utils/type_conversion.hpp"
#include "toolbox_maya/utils/maya_error.hpp"
#include "toolbox_maya/utils/maya_dag_nodes.hpp"

#include <toolbox_stl/vector.hpp>
#include <toolbox_stl/time_tracker.hpp>

// =============================================================================
namespace tbx_maya {
// =============================================================================


bool get_selected_components_of_type(MFn::Type type,
                                     const MDagPath& path,
                                     MObject& component)
{

    MStatus status;
    MSelectionList selection_list;
    mayaCheck( MGlobal::getActiveSelectionList(selection_list) );
    MItSelectionList iter(selection_list, MFn::kInvalid, &status);
    mayaCheck(status);
    for ( ; !iter.isDone(); iter.next())
    {
        MDagPath curr_selection;

        if( !iter.getDagPath( curr_selection, component ) )
            continue;

        if( curr_selection == path &&
            !component.isNull() &&
            component.apiType() == type)
        {
            return true;
        }
    }
    return false;
}

// -----------------------------------------------------------------------------

bool has_selected_vertices(const MDagPath& path, MObject& component)
{
    
    bool res = get_selected_components_of_type(MFn::kMeshVertComponent,
                                               path,
                                               component);
    

    return res;
}

// -----------------------------------------------------------------------------

bool has_selected_faces(const MDagPath& path, MObject& component)
{
    return get_selected_components_of_type(MFn::kMeshPolygonComponent,
                                           path,
                                           component);
}

// -----------------------------------------------------------------------------

bool has_selected_edges(const MDagPath& path, MObject& component)
{
    return get_selected_components_of_type(MFn::kMeshEdgeComponent,
                                           path,
                                           component);
}

// -----------------------------------------------------------------------------

int get_nb_vertices(MObject mesh_shape)
{
    MStatus status;
    MItMeshVertex mesh_it(mesh_shape, &status);
    mayaCheck(status);
    int nb_verts = mesh_it.count(&status);
    mayaCheck(status);
    return nb_verts;
}

// -----------------------------------------------------------------------------

int get_nb_vertices(const MFnMesh& mesh)
{
    MStatus status;
    int nb_verts = mesh.numVertices(&status);
    mayaCheck(status);
    return nb_verts;
}

// -----------------------------------------------------------------------------

void get_selected_vertices(std::vector<int>& vertex_list, MObject mesh_shape)
{
    // NOTE: parse string like in get_selection_and_convert_to_vertex
    // for faster performances
    MStatus status;
    vertex_list.clear();
    MObject component;
    MDagPath path = get_MDagPath(mesh_shape);
    if( tbx_maya::has_selected_vertices(path, component) )
    {
        MItMeshVertex vert_it(path, component, &status);
        mayaCheck( status );
        int size_selection = vert_it.count(&status);
        mayaCheck( status );
        vertex_list.reserve( size_selection );
        //int i = 0;
        for ( ; !vert_it.isDone() ; vert_it.next() ){
            int vidx = vert_it.index(&status);
            mayaCheck(status);
            vertex_list.push_back( vidx );
            //++i;
        }
    }
}

// -----------------------------------------------------------------------------

void get_selection_and_convert_to_vertex(
        std::vector<int>& vertex_list,
        MObject mesh_shape)
{
    MStatus status;
    std::vector<int> face_list;
    std::vector<int> edge_list;
    vertex_list.clear();

    
    MObject component;
    MDagPath path = get_MDagPath(mesh_shape);
    // Check if edges are selected and convert to vertex index
    if( tbx_maya::has_selected_edges(path, component) )
    {
        // Look up every edges
        MItMeshEdge edge_it(path, component, &status);
        mayaCheck( status );

        int count = edge_it.count(&status);
        mayaCheck( status );
        edge_list.reserve(count * 2);

        for(; !edge_it.isDone(); edge_it.next())
        {
            // Get edge vertices:
            int vert_0 = edge_it.index(0, &status);
            mayaCheck( status );
            int vert_1 = edge_it.index(1, &status);
            mayaCheck( status );

            edge_list.push_back( vert_0 );
            edge_list.push_back( vert_1 );
        }
    }
    

    
    // Check if faces are selected and convert to vertex index
    if( tbx_maya::has_selected_faces(path, component) )
    {
        // Lookup every faces
        MItMeshPolygon face_it(path, component, &status);
        mayaCheck( status );

        int count = face_it.count(&status);
        mayaCheck( status );
        face_list.reserve(count * 4);

        for(; !face_it.isDone(); face_it.next())
        {
            // Get this face's vertices
            MIntArray vertex_indices;
            mayaCheck( face_it.getVertices(vertex_indices) );
            // Add vertices to our list
            for(unsigned i = 0; i < vertex_indices.length(); i++)
            {
                face_list.push_back( vertex_indices[i] );
            }
        }
    }
    


    bool has_faces = (face_list.size() > 0);
    bool has_edges = (edge_list.size() > 0);

    
    // Check if vertices are selected and add to the selection list
    if( tbx_maya::has_selected_vertices(path, component) )
    {
        
        MItMeshVertex vert_it(path, component, &status);
        mayaCheck( status );
        

        
        int count = vert_it.count(&status);
        mayaCheck( status );
        vertex_list.reserve(count);
        

        
        for ( ; !vert_it.isDone() ; vert_it.next() ){
            int vidx = vert_it.index(&status);
            mayaCheck(status);
            vertex_list.push_back( vidx );
        }
        

    }
    

    // Merge lists
    {
        //this operations will eliminate duplicate indices in edge and face list
        tbx::merge(vertex_list, edge_list);
        tbx_assert( !tbx::has_duplicates(vertex_list) );
        tbx::merge(vertex_list, face_list);
        tbx_assert( !tbx::has_duplicates(vertex_list) );
    }

}

// -----------------------------------------------------------------------------

void set_points(MObject mesh_shape, MPointArray& new_points)
{
    MStatus status;
    MFnMesh fn_mesh(get_shape(mesh_shape), &status);
    mayaCheck( status );
    mayaCheck( fn_mesh.setPoints(new_points) );
    mayaCheck( status );
}

void set_points(MObject mesh_shape, const std::vector<tbx::Vec3>& new_points){
    set_points(mesh_shape, to_MPointArray(new_points));
}

}// END tbx_maya Namespace =====================================================
