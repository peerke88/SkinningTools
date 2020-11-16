#include "toolbox_maya/data/maya_mesh.hpp"

#include <maya/MFnMesh.h>
#include <maya/MItMeshVertex.h>
#include <maya/MItMeshPolygon.h>
#include <maya/MPointArray.h>
#include <maya/MIntArray.h>
#include <maya/MMatrix.h>

#include <toolbox_mesh/mesh_utils.hpp>
#include <toolbox_maya/utils/maya_dependency_nodes.hpp>
#include <toolbox_maya/utils/maya_error.hpp>
#include <toolbox_maya/utils/maya_utils.hpp>
#include <toolbox_maya/utils/maya_dag_nodes.hpp>
#include <toolbox_maya/utils/type_conversion.hpp>
#include <toolbox_mesh/mesh_geometry.hpp>
#include <toolbox_mesh/mesh_topology.hpp>

using namespace tbx;


// =============================================================================
namespace tbx_maya {
// =============================================================================

static
void fetch_geom(MObject in_mobject_mesh,
                tbx_mesh::Mesh_geometry& out_mesh,
                std::vector<tbx::Vec3>& out_normals,
                MMatrix vert_transfo)
{
    out_mesh.clear_data();
    MStatus status = MS::kSuccess;
    MItMeshVertex mesh_it(in_mobject_mesh, &status);
    mayaCheck(status);

    // Load vertices and normals.
    int num_verts = mesh_it.count(&status);
    mayaCheck(status);

    out_mesh._vertices.resize(num_verts);
    out_normals.resize(num_verts);

    int idx = 0;
    for ( ; !mesh_it.isDone(); mesh_it.next())
    {
        MPoint point = mesh_it.position(MSpace::kObject, &status);
        mayaCheck(status);

        // If specified, transform the point from object space
        // to another coordinate space.
        point = point * vert_transfo;
        out_mesh._vertices[idx] = to_vec3( point );

        // Load the vertex's normal.
        // If the normal has unshared normals, this will retrieve
        // the averaged normal.
        MVector normal;
        mayaCheck( mesh_it.getNormal(normal, MSpace::kObject) );
        normal = normal.transformAsNormal(vert_transfo);

        out_normals[idx] = to_vec3( normal );
        ++idx;
    }

    // Load tris using Maya's triangulation.
    for(MItMeshPolygon it(in_mobject_mesh); !it.isDone(); it.next())
    {
        if( !it.hasValidTriangulation() )
        {
            int idx = it.index( &status );
            mayaWarning(MString("Warning: Polygon with index ")+idx+"doesn't have a valid triangulation");
            continue;
        }

        MPointArray tri_vertices;
        MIntArray tri_indices;
        mayaCheck( it.getTriangles(tri_vertices, tri_indices, MSpace::kObject) );
        mayaAssert(tri_indices.length() % 3 == 0);
        for(int t = 0; t < (int) tri_indices.length(); t += 3)
        {
            tbx_mesh::Tri_face face;
            for(int v = 0; v < 3; ++v)
                face[v] = tri_indices[t + v];

            out_mesh._triangles.push_back(face);
        }
    }
}

// -----------------------------------------------------------------------------

Maya_mesh::Maya_mesh()
    : _geom(nullptr)
    , _topo(nullptr)
{
    _geom = new tbx_mesh::Mesh_geometry();
    _topo = new tbx_mesh::Mesh_topology();
}

// -----------------------------------------------------------------------------

Maya_mesh::Maya_mesh(const Maya_mesh& mesh)
    : _geom(nullptr)
    , _topo(nullptr)
{
    _geom = new tbx_mesh::Mesh_geometry(*mesh._geom);
    _topo = new tbx_mesh::Mesh_topology(*mesh._topo);
    _topo->reset_geometry_pointer(_geom);

    _attributes = mesh._attributes;
    _attributes.reset_pointers(*_geom, *_topo);
}

// -----------------------------------------------------------------------------

Maya_mesh::Maya_mesh(MObject mesh_node,
                     const MMatrix& mesh_transformation)
    : _geom(nullptr)
    , _topo(nullptr)
{
    _geom = new tbx_mesh::Mesh_geometry();
    _topo = new tbx_mesh::Mesh_topology();
    load(mesh_node, mesh_transformation);
}

// -----------------------------------------------------------------------------

void Maya_mesh::load(MObject mesh_node, const MMatrix& mesh_transformation)
{
    mayaAssertMsg( mesh_node.hasFn(MFn::kMesh),
                   "This shape doesn't have MFn::kMesh. Only meshes are supported.");
    clear();
    // Don't use get_shape() it's the user responsibility
    // What's more: get_shape() might fail even on valid MFn::kMesh nodes
    // e.g when the object comes from a weird plug or data block
    Maya_mesh::load(/*get_shape*/(mesh_node), mesh_transformation, *_geom, _attributes.normals());
    _topo->update( *_geom );
    _attributes.reset_pointers( *_geom, *_topo );
}

// -----------------------------------------------------------------------------

void Maya_mesh::clear()
{
    _geom->clear_data();
    _topo->clear_data();
    _attributes.clear();
}

// -----------------------------------------------------------------------------

Maya_mesh::~Maya_mesh(){
    clear();
    delete _geom;
    _geom = nullptr;
    delete _topo;
    _topo = nullptr;

}

// -----------------------------------------------------------------------------

/*static*/
void Maya_mesh::load(MObject mesh_node,
                     const MMatrix& world_matrix,
                     tbx_mesh::Mesh_geometry& out_geom,
                     std::vector<tbx::Vec3>& out_normals)
{
    mayaAssertMsg( mesh_node.hasFn(MFn::kMesh),
                   "This shape doesn't have MFn::kMesh. Only meshes are supported.");

    fetch_geom(mesh_node, out_geom, out_normals, world_matrix);
    tbx_mesh::mesh_utils::flip_edge_corners( out_geom );
}

// -----------------------------------------------------------------------------

MObject Maya_mesh::add_maya_dag_mesh( const Maya_mesh& mesh)
{
    MStatus status;
    MFnMesh mesh_fn;
    MObject new_mesh;
    MPointArray vertex_list(mesh._geom->nb_vertices());
    MIntArray nb_vertex_per_face(mesh._geom->nb_triangles());
    MIntArray triangle_list(mesh._geom->nb_triangles() * 3);

    for(int i = 0; i < mesh._geom->nb_triangles(); ++i)
    {
        tbx_mesh::Tri_face face = mesh._geom->_triangles[i];
        triangle_list[i*3 + 0] = face.a;
        triangle_list[i*3 + 1] = face.b;
        triangle_list[i*3 + 2] = face.c;

        nb_vertex_per_face[i] = 3;
    }

    for(int i = 0; i < mesh._geom->nb_vertices(); ++i)
        vertex_list[i] = to_MPoint( mesh._geom->vertex(i) );

    // Maybe use a mel command to speed up this:
    new_mesh = mesh_fn.create( mesh._geom->nb_vertices(),
                               mesh._geom->nb_triangles(),
                               vertex_list,
                               nb_vertex_per_face,
                               triangle_list,
                               MObject::kNullObj,
                               &status);
    mayaCheck( status );

    for(int i = 0; i < mesh._geom->nb_vertices(); ++i)
    {
        MVector mvec = to_MVector( mesh.normals()[i] );
        mayaCheck( mesh_fn.setVertexNormal( mvec, i) );
    }

    return new_mesh;
}

// -----------------------------------------------------------------------------
/*
void Maya_mesh::assign_material_to(MObject mesh, const std::string& material_name)
{
    Save_active_selection save_selection;
    MString cmd;
    MString name(material_name.c_str());
    if( !node_exists(name) )
    {
        // string $shader_name = `shadingNode -name blinn_implicit_skin -asShader blinn`;
        cmd = ("shadingNode -name \"")+name+("\" -asShader blinn");
        MString shader_name;
        mayaCheck( MGlobal::executeCommand(cmd, shader_name, true) );
        mayaAssert(shader_name == name);

        cmd = (("sets -renderable true -noSurfaceShader true -empty -name ")+shader_name+("SG;"));
        mayaCheck( MGlobal::executeCommand(cmd, true) );

        cmd = (("connectAttr -f ") + shader_name + (".outColor ") + shader_name + ("SG.surfaceShader;"));
        MString res;
        mayaCheck( MGlobal::executeCommand(cmd, res, true) );
        MGlobal::displayInfo( MString(("Connected: "))+res );

        //setAttr "blinn1.color" -type double3 0.146 0.404538 0.5 ;
        cmd = (("setAttr \"")+shader_name+(".color\" -type double3 0.146 0.404538 0.5 ;"));
        mayaCheck( MGlobal::executeCommand(cmd, true) );

        //setAttr "blinn1.diffuse" 1;
        cmd = (("setAttr \"")+shader_name+(".diffuse\" 1;"));
        mayaCheck( MGlobal::executeCommand(cmd, true) );
    }


    {
        mayaCheck( MGlobal::selectByName(get_dag_long_name(mesh), MGlobal::kReplaceList) );
        cmd = (("sets -e -forceElement ") + name + ("SG;"));
        mayaCheck( MGlobal::executeCommand(cmd, false) );
    }
}
*/

// -----------------------------------------------------------------------------

unsigned Maya_mesh::nb_vertices() const { return (unsigned)_geom->nb_vertices(); }

Vec3 Maya_mesh::vertex(tbx_mesh::Vert_idx idx) const { return _geom->vertex(idx); }

// -----------------------------------------------------------------------------

void Maya_mesh::set_vertex(tbx_mesh::Vert_idx idx, Vec3& v){
    _attributes.clear();
    _geom->_vertices[idx] = v;
}

}// END tbx_maya Namespace =====================================================
