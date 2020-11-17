#include <maya/MFnPlugin.h>

#include <maya/MFnPluginData.h>
#include <maya/MGlobal.h>

//// -----------------------------------------------------------------------------

#include "sbr_settings.hpp"
#include "maya_nodes/node_swe_cache.hpp"
#include "maya_commands/cmd_swe_brush.hpp"
#include "maya_commands/cmd_swe_cache_manager.hpp"

//// ------
#include <toolbox_stl/time_tracker.hpp>
#include "toolbox_maya/utils/maya_error.hpp"

/**
 * @file plugin.cpp
 * @brief entry point of the Maya plugin.
 *
 * <code>MStatus initializePlugin(MObject obj)</code> is the equivalent of
 * <code>void main(){ }</code> for Maya plugins
*/
// =============================================================================
namespace skin_brush {
// =============================================================================

/// @brief first function executed by Maya when loading the plugin
MStatus initializePlugin(MObject obj)
{
    try {

        MStatus status;


        std::string plugin_name = "Skin brushes";

        g_timer = Time_tracker(g_time_tracking_on);
        g_timer.set_display_func( [](std::string msge){ MGlobal::displayInfo( MString(msge.c_str()) ); } );

        if (g_debug_mode)
            MGlobal::displayWarning("SWE: DEBUG MODE ON");

        MFnPlugin plugin(obj, "Rodolphe Vaillant", "1.0.0", "Any", &status);
        mayaCheck(status);        

        // ------------------
        // Setup Nodes
        // ------------------

        mayaCheck(plugin.registerNode(Node_swe_cache::_s_name, Node_swe_cache::_s_id,
                                      Node_swe_cache::creator, Node_swe_cache::initialize, Node_swe_cache::_s_type));

        // ------------------
        // Setup commands
        // ------------------

        mayaCheck(plugin.registerCommand(Cmd_swe_brush::_s_name, Cmd_swe_brush::creator));
        mayaCheck(plugin.registerCommand(Cmd_swe_cache_manager::_s_name, Cmd_swe_cache_manager::creator));

    }
    catch (std::exception& e) {
        maya_print_error(e);
        return MS::kFailure;
    }
    return MS::kSuccess;
}

// -----------------------------------------------------------------------------

/// @brief last function executed by Maya when unloading the plugin
MStatus uninitializePlugin(MObject obj)
{

    try {
        MFnPlugin plugin(obj);

        /// **!! WARNING !!**:
        /// it is important to deregister node/commands/data/...
        /// in *REVERSE* order as they were registered.        
        mayaCheck(plugin.deregisterCommand(Cmd_swe_cache_manager::_s_name));
        mayaCheck(plugin.deregisterCommand(Cmd_swe_brush::_s_name));
        mayaCheck(plugin.deregisterNode(Node_swe_cache::_s_id));
    }
    catch (std::exception& e) {
        maya_print_error(e);
        return MS::kFailure;
    }

    return MS::kSuccess;
}

} // END skin_brush Namespace ===============================================
