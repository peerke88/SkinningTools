#ifndef TOOLBOX_MAYA_MAYA_UTILS_HPP
#define TOOLBOX_MAYA_MAYA_UTILS_HPP

#include <maya/MString.h>
#include <maya/MGlobal.h>
#include <maya/MArgList.h>

#include <vector>

//#include <toolbox_maths/vector3.hpp>

#include "toolbox_maya/utils/maya_error.hpp"

/**
    @brief Various utilities to ease the access to the Maya API

    Note that one advantage of these utilities is to wrap maya error handling
    and convert them to exceptions.
*/

// =============================================================================
namespace tbx_maya {
// =============================================================================

// -----------------------------------------------------------------------------
/// @name Misc
// -----------------------------------------------------------------------------

///@return absolute path to "plugin_name" or an empty string if not found.
MString get_plugin_path(const MString& plugin_name);


///@brief shorcut to MString::split()
MStringArray split(const MString& str, char c);

///@return if 'string' contains "xxxx:yyyyyyyyy" removes  the first "xxxx:"
/// which represent the namespace.
static inline
MString remove_namespace(const MString& string){
    MStringArray tokens = split(string, ':');
    mayaAssert( tokens.length() > 0 );
    return tokens[tokens.length()-1];
}

/// @brief wraps brief MUserEventMessage::postUserEvent()
void post_user_event(const MString& string);

// -----------------------------------------------------------------------------
/// @name Tools MSelectionList
// -----------------------------------------------------------------------------

/// @return the object of api type "type" in "list"
/// (or null pointer if nothing is found)
MObject has(const MSelectionList& list, MFn::Type type);

std::vector<MDagPath> get_active_selection(bool ordered_selection = true);

/// @return the objects in the active selection list that match 'type_filter'
std::vector<MDagPath> get_selected(MFn::Type type_filter);

/// @return the objects in the active selection list that match one
/// of the types of 'type_list'
std::vector<MDagPath> get_selected(const std::vector<MFn::Type>& type_list);

// -----------------------------------------------------------------------------
/// @name Tools MFnSkinCluster
// -----------------------------------------------------------------------------

std::vector<MObject> get_influence_objects(MObject skin_cluster);


}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_MAYA_UTILS_HPP
