#include "maya_commands/cmd_swe_cache_manager.hpp"

// -----------------------------------------------------------------------------

#include <maya/MSyntax.h>
#include <maya/MArgParser.h>

#include "sbr_utils.hpp"
#include <toolbox_stl/vector.hpp>
#include "toolbox_maya/utils/type_conversion.hpp"
#include <toolbox_maya/utils/maya_dependency_nodes.hpp>
#include <toolbox_maya/utils/maya_dag_nodes.hpp>
#include <toolbox_maya/data/maya_skeleton_utils.hpp>

#include "maya_nodes/node_swe_cache.hpp"
// =============================================================================
namespace skin_brush {
// =============================================================================

char Cmd_swe_cache_manager::_s_name[] = "SBR_cache_manager";

// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------

MStatus Cmd_swe_cache_manager::doIt(const MArgList& args)
{

    MString raw_command = MString(_s_name) + " " + to_str(args);
    try {
        MStatus status;
        MSyntax syntax;

        syntax.addFlag("-fca", "-findCache", MSyntax::kString /*skin cluster*/);
        syntax.addFlag("-gtb", "-goToBindPose", MSyntax::kString /*skin cluster*/);
        syntax.addFlag("-rvc", "-removeCache", MSyntax::kString /*skin cluster*/);
        syntax.addFlag("-lkc", "-lockCache", MSyntax::kString /*skin cluster*/, MSyntax::kBoolean);

        // Force rebuilding the cache (with the current skeleton pose)
        syntax.addFlag("-bca", "-buildCache", MSyntax::kString /*skin cluster*/);

        //syntax.setObjectType(MSyntax::kStringObjects);
        MArgParser parser(syntax, args, &status);
        if (!status) {
            MGlobal::displayError("Incorrect command argument! Please check flags and argument are valid: ");
            MGlobal::displayError(raw_command);
            return MS::kFailure;
        }

        //-*---------

        if (parser.isFlagSet("-findCache")) {
            MString skin_cluster_name;
            mayaCheck(parser.getFlagArgument("-findCache", 0, skin_cluster_name));
            MObject skin_cluster = get_MObject(skin_cluster_name);
            Node_swe_cache* cache_node;
            if (Node_swe_cache::find_valid_cache(skin_cluster, cache_node))
                setResult(get_name(cache_node->thisMObject()));
            else
                setResult("");

            return MS::kSuccess;
        }

        if (parser.isFlagSet("-goToBindPose")) {
            MString skin_cluster_name;
            mayaCheck(parser.getFlagArgument("-goToBindPose", 0, skin_cluster_name));
            MObject skin_cluster = get_MObject(skin_cluster_name);
            Node_swe_cache* cache;
            if (Node_swe_cache::find_valid_cache(skin_cluster, cache)) {
                restore_initial_pose(*(cache->get_skeleton()));
            }
            else {
                mayaWarning("No associated cache");
            }

            return MS::kSuccess;
        }

        if (parser.isFlagSet("-buildCache")) {
            MString skin_cluster_name;
            mayaCheck(parser.getFlagArgument("-buildCache", 0, skin_cluster_name));
            MObject skin_cluster = get_MObject(skin_cluster_name);

            MGlobal::displayInfo("Build cache make sure you are in bind pose.");
            Node_swe_cache::build_cache(skin_cluster);

            return MS::kSuccess;
        }
        else if (parser.isFlagSet("-removeCache")) {
            MString skin_cluster_name;
            mayaCheck(parser.getFlagArgument("-removeCache", 0, skin_cluster_name));
            MObject skin_cluster = get_MObject(skin_cluster_name);
            bool cache_exists = Node_swe_cache::has_cache(skin_cluster);
            Node_swe_cache::destroy_from_skin_cluster(skin_cluster);

            setResult(int(cache_exists));
            return MS::kSuccess;
        }


    }
    catch (std::exception& e) {
        MGlobal::displayError("The command \"" + raw_command + "\" failed with the following error: ");
        MGlobal::displayError(e.what());
        MGlobal::displayError("Check input arguments or flags are valid.");
        std::cerr << e.what();
        return MS::kFailure;
    }
    return MS::kSuccess;
}

} // END Namespace =============================================================
