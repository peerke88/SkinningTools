#include "maya_commands/cmd_swe_brush.hpp"

// -----------------------------------------------------------------------------

#include <maya/MArgList.h>
#include <maya/MGlobal.h>

// -----------------------------------------------------------------------------

#include <toolbox_maya/data/maya_skeleton_utils.hpp>
#include <toolbox_maya/utils/maya_error.hpp>
#include <toolbox_maya/utils/maya_dag_nodes.hpp>
#include <toolbox_maya/utils/type_conversion.hpp>
#include <toolbox_maya/utils/sub_mesh.hpp>
#include <toolbox_maya/utils/maya_mfnmesh_utils.hpp>

//--------
#include <toolbox_stl/vector.hpp>
#include <toolbox_mesh/iterators/first_ring_it.hpp>
#include <toolbox_maya/utils/find_node.hpp>

// -----------------------------------------------------------------------------

#include "toolbox_mesh/mesh_geometry.hpp"
#include "toolbox_mesh/mesh_topology.hpp"
//#include "maya_commands/cmd_swe_edit.hpp"
#include "toolbox_stl/time_tracker.hpp"
#include "operations/smoothing.hpp"

#include "operations/relax_grad_descent_optim.hpp"
#include "operations/smoothing.hpp"
#include "data/brush.hpp"
#include "data/rig.hpp"
#include "sbr_utils.hpp"
#include "toolbox_maya/data/maya_skin_weights.hpp"

using namespace tbx_maya;

// =============================================================================
namespace skin_brush {
// =============================================================================

char Cmd_swe_brush::_s_name[] = "SBR_brush";

// -----------------------------------------------------------------------------

static MString get_flag_string(const MArgList& args, const MString& str)
{
    MStatus status;
    unsigned len = args.length(&status);
    mayaCheck(status);
    MString name_arg;
    for(unsigned i = 0; i < len; ++i)
    {
        MString val = args.asString(i, &status);

        if( status == MS::kSuccess && str == val )
        {
            name_arg = args.asString(++i, &status);
            mayaCheck( status );
            break; // only one occurence is necessary.
        }
    }
    return name_arg;
}

// -----------------------------------------------------------------------------

/// fetch the argument "-smooth" string (skin_cluster_name)
static MString get_flag_smooth(const MArgList& args) {
    return get_flag_string(args, "-smooth");
}

// -----------------------------------------------------------------------------

/// fetch the argument "-brushContext" string (skin_cluster_name)
static MString get_flag_brush_context(const MArgList& args) {
    return get_flag_string(args, "-brushContext");
}

// -----------------------------------------------------------------------------

/// fetch the argument "-relaxation" string (skin_cluster_name)
static MString get_flag_relaxation(const MArgList& args) {
    return get_flag_string(args, "-relaxation");
}

// -----------------------------------------------------------------------------

/// fetch the argument "-buildCache" string (skin_cluster_name)
static MString get_flag_build_cache(const MArgList& args) {
    return get_flag_string(args, "-buildCache");
}

// -----------------------------------------------------------------------------

/// fetch the argument "-fixValues" double (min) double (max)
static std::vector<tbx::Vec2> get_flag_fix_values(const MArgList& args)
{
    MStatus status;
    std::vector<tbx::Vec2> constraints;
    unsigned len = args.length(&status);
    mayaCheck(status);

    for(unsigned i = 0; i < len; ++i)
    {
        MString val = args.asString(i, &status);

        if( status == MS::kSuccess && MString("-fixValues") == val )
        {

            float min = float(args.asDouble(++i, &status));
            mayaCheck( status );
            float max = float(args.asDouble(++i, &status));
            mayaCheck( status );
            constraints.push_back( Vec2(min, max) );
        }
    }
    return constraints;
}

// -----------------------------------------------------------------------------

static int get_flag_int(const MArgList& args,
                        const MString& str,
                        int default_value)
{
    MStatus status;
    unsigned len = args.length(&status);
    mayaCheck(status);
    int value = default_value;
    for(unsigned i = 0; i < len; ++i)
    {
        MString val = args.asString(i, &status);

        if( status == MS::kSuccess && str == val )
        {

            value = args.asInt(++i, &status);
            mayaCheck( status );
            break; // only one occurence is necessary.
        }
    }
    return value;
}

// -----------------------------------------------------------------------------

static double get_flag_double(const MArgList& args,
                              const MString& str,
                              double default_value)
{
    MStatus status;
    unsigned len = args.length(&status);
    mayaCheck(status);
    double value = default_value;
    for(unsigned i = 0; i < len; ++i)
    {
        MString val = args.asString(i, &status);

        if( status == MS::kSuccess && str == val )
        {

            value = args.asDouble(++i, &status);
            mayaCheck( status );
            break; // only one occurence is necessary.
        }
    }
    return value;
}

// -----------------------------------------------------------------------------

/// fetch the argument "-maxInfluences" int
static int get_flag_max_influences(const MArgList& args) {
    return get_flag_int(args, "-maxInfluences", 0);
}

// -----------------------------------------------------------------------------

/// fetch the argument "-brushMask" int (slot) int (length array) int[] (vert_ids) float[] (brush_values)
/// @note the last two arguments are optional if length array is null.
/// Usually used with artUserPaintCtx -sac
static std::vector<Brush> get_flag_brush_mask(const MArgList& args)
{
    MStatus status;
    std::vector<Brush> mask;
    unsigned len = args.length(&status);
    mayaCheck(status);

    for(unsigned i = 0; i < len; ++i)
    {
        MString val = args.asString(i, &status);

        if( status == MS::kSuccess && MString("-brushMask") == val )
        {
            // no idea what the 'slot' value stand for but we have to skip it...
            int slot = args.asInt(++i, &status);
            mayaCheck( status );
            int len = args.asInt(++i, &status);
            mayaCheck( status );
            MIntArray ints;
            MDoubleArray floats;
            if( len > 0 )
            {
                ints = args.asIntArray(++i, &status);
                mayaCheck( status );
                floats = args.asDoubleArray(++i, &status);
                mayaCheck( status );
            }

            mayaAssertMsg( ints.length() == floats.length(), "Invalid command flag for -brushMask" );
            for(unsigned j = 0; j < ints.length(); ++j)
                mask.push_back( Brush(ints[j], float(floats[j])) );
        }
    }
    return mask;
}

// -----------------------------------------------------------------------------

static bool has_flag(const MArgList& args, const MString& flag_name)
{
    MStatus status;
    unsigned len = args.length(&status);
    mayaCheck(status);
    for(unsigned i = 0; i < len; ++i)
    {
        MString val = args.asString(i, &status);

        if( status == MS::kSuccess && flag_name == val ) {
            return true;
        }
    }
    return false;
}

// -----------------------------------------------------------------------------

static inline
void check_vertex_selection(std::vector<int>& selection, int max_verts)
{
    std::vector<int> temp = selection;
    selection.clear();
    bool error = false;
    for(int vert_id : temp){
        if(vert_id < 0 || vert_id > max_verts)
            error = true;
        else
            selection.push_back( vert_id );
    }

    if(error)
        MGlobal::displayError("Invalid vertex Id, Maybe the selected mesh and selected vertices does not match?");
}

// -----------------------------------------------------------------------------
static inline
std::vector<int> include_welded_vertices(
        const std::vector<int>& selection,
        const std::vector< std::vector<int> >& welded_vertices)
{
    std::vector<int> new_selection = selection;
    std::vector<int> new_vertices;
    for( int v_idx : selection )
    {
        for( int brother : welded_vertices[v_idx] )
        {
            if(!tbx::exists(new_vertices, brother) &&
               !tbx::exists(selection, brother) )
            {
                new_vertices.push_back(brother);
            }
        }
    }

    //MGlobal::displayInfo(MString("New verts:") + new_vertices.size() );
    for( int idx : new_vertices )
        new_selection.push_back( idx );

    tbx_assert( !has_duplicates(new_selection) );
    return new_selection;
}

// -----------------------------------------------------------------------------

MStatus Cmd_swe_brush::doIt(const MArgList& args)
{
    MStatus status;

    try
    {        

        MString raw_command = MString(_s_name)+" "+to_str(args);

        _skin_cluster_name = "";
        _locked_joints.clear();
        _action = eUndef;


        if ( (_skin_cluster_name = get_flag_build_cache(args)).length() >0 )
        {
            _action = eBuildCache;
            MObject skin_cluster = get_MObject(_skin_cluster_name);
            MGlobal::displayInfo("Build cache make sure you are in bind pose");
            Node_swe_cache::build_cache(skin_cluster);
            return MS::kSuccess;
        }


        // -------------
        // Extract flags
        // -------------
        _brush_context = get_flag_brush_context(args);
        _constraints = get_flag_fix_values( args ); // -fixValues double (min) double (max)
        _max_influences = get_flag_max_influences( args );
        _extra_links = has_flag( args , "-enableExtraLinks");

        std::vector<Brush> mask = get_flag_brush_mask( args ); // -brushMask int (slot) int (length array) int[] (vert_ids) float[] (brush_values)

        if( (_skin_cluster_name = get_flag_smooth( args )).length() > 0 ) // -smooth string (skin cluster)
        {
            _skin_cluster = get_MObject( _skin_cluster_name );
            _action = eSmooth;
        }        
        else if( (_skin_cluster_name = get_flag_relaxation( args )).length() > 0 ) // -relaxation string (skin cluster))
        {
            _skin_cluster = get_MObject( _skin_cluster_name );
            _action = eRelax;
        }               

        // -----
        // Check command flags
        // -----
        _flood = has_flag(args, "-flood");

        if( _action == eUndef){
            MGlobal::displayError("Incorrect command argument! Please check flags and argument are valid: ");
            MGlobal::displayError("(Undefined stroke, missing or wrong action flag such as -smooth, -relaxation etc.) ");
            MGlobal::displayError(raw_command);
            return MS::kFailure;
        } else if( _skin_cluster_name == "" ) {
            MGlobal::displayError("Incorrect command argument! Please check flags and argument are valid: ");
            MGlobal::displayError("(skin cluster name missing) ");
            MGlobal::displayError(raw_command);
            return MS::kFailure;
        } else if( _brush_context == "" && !_flood ) {
            MGlobal::displayError("Incorrect command argument! Please check flags and argument are valid: ");
            MGlobal::displayError("(brush context is missing) ");
            MGlobal::displayError(raw_command);
            return MS::kFailure;
        }

        // true when the user paints with a brush
        // false when user applies the brush by vertex/face/... selection.
        bool is_brush_stroke = has_flag(args, "-brushMask");

        if( (mask.size() > 0 || is_brush_stroke) && !_flood )
        {
            MObject mesh_shape;
            if( !find_dfm_output_deformed_mesh(_skin_cluster, mesh_shape) ){
                mayaAbort("Can't find output mesh");
            }
        }

        if( (_cache = find_cache(_skin_cluster)) == nullptr )
        {
            MGlobal::displayError("Aborting command please init the bind pose first.");
            return MS::kFailure;
        }

        if(_extra_links){
            _radius_extra_links = get_flag_double( args, "-enableExtraLinks", 0.0 );
            _cache->get_rig()->precompute_extra_links( float(_radius_extra_links) );
        }
        // End load cache ----------


        std::vector<int>& selection = _vertex_selection;
        build_selection(selection, _skin_cluster, mask);

        // Tweak selection: Not needed if every vertices are selected.
        if(  (selection.size() < get_nb_vertices( _cache->find_output_mesh() )) && _extra_links )
        {
            // Some vertices are welded together but the user might only
            // select a sub set of those vertices, we need to include every
            // vertices other-wise unprocessed vertices might lock the values
            // of its other welded siblings. (e.g. when smoothing skin weights)
            selection = include_welded_vertices( selection, _cache->get_rig()->get_weld_list() );

            // Propagate selection but *only* for extra links
            // Because maya brush operates only on one surface at a time it
            // can be a hassle to switch painting between various cloth layers
            // for instance.
            if( is_brush_stroke )
            {
                selection = grow_selection(
                            selection,
                            First_ring_it(_cache->get_rig()->get_extra_vertex_links()) );

            }
        }

        int nb_verts = get_nb_vertices( _cache->find_output_mesh() );
        check_vertex_selection(selection, nb_verts);

        _cache->update();

        if( (selection.size() > 0) || _flood )
        {
            _sub_mesh = (selection.size() > 0 /*&& !_flood*/) ? Sub_mesh(selection) : Sub_mesh( unsigned(nb_verts));
            _locked_joints = get_locked_joints(*(_cache->get_skeleton()));            
            // Save skin weights for the undo.
            _original_weights = _cache->get_skeleton()->_weights;
            status = redoIt();
        }

    }
    catch (std::exception& e)
    {
        MGlobal::displayError( e.what() );
        std::cerr << e.what();
        status = MS::kFailure;
    }



    return status;
}

// -----------------------------------------------------------------------------

MStatus Cmd_swe_brush::redoIt( )
{
    try
    {

        if( !Node_swe_cache::has_cache(_skin_cluster) )
            return MS::kFailure;
        if(_action == eUndef)
            return MS::kSuccess;        

        // shortcuts
        const Rig& rig = *(_cache->get_rig());        
        const Sub_mesh& sub_mesh = _sub_mesh;
        std::vector<std::map<int, float> >& weights = _cache->get_skeleton()->_weights;        

        switch (_action) {
        case eSmooth:
        {
            Smoothing_type type = eCOTAN;
            if(_extra_links) {
                type = eMIXED_LINK;
            }

            smooth_skin_weights_all_joints(weights, rig, _constraints, _max_influences, _locked_joints, sub_mesh, type);
        }break;        
        case eRelax:
        {
            relax_grad_descent_optim(_cache, weights, rig, _constraints, _extra_links, sub_mesh);

        }break;        

        default:
            break;
        }

        if(_extra_links)
        {            
            for( tbx_mesh::Vert_idx destination_idx = 0; destination_idx < rig.get_weld_source_vertex().size(); ++destination_idx )
            {
                tbx_mesh::Vert_idx source_idx = rig.get_weld_source_vertex()[destination_idx];
                if(source_idx > -1)
                    weights[destination_idx] = weights[source_idx];
            }
        }

        skin_weights::set_subset_through_mplug(_skin_cluster, sub_mesh.vertex_list(), weights);
        _cache->_cache_skin_weights_dirty = false;
    }
    catch (std::exception& e)
    {
        MGlobal::displayError( e.what() );
        std::cerr << e.what();
        return MS::kFailure;
    }

    return MS::kSuccess;

}

// -----------------------------------------------------------------------------

MStatus Cmd_swe_brush::undoIt( )
{
    try
    {
        skin_weights::set_subset_through_mplug(_skin_cluster, _sub_mesh.vertex_list(), _original_weights);
        Node_swe_cache* cache = nullptr;
        if( (cache = find_cache(_skin_cluster, false /*don't update*/)) != nullptr )
        {
            cache->get_skeleton()->_weights = _original_weights;
        }
    }
    catch (std::exception& e)
    {
        MGlobal::displayError( e.what() );
        std::cerr << e.what();
        return MS::kFailure;
    }
    return MS::kSuccess;
}

}// END skin_brush Namespace ========================================
