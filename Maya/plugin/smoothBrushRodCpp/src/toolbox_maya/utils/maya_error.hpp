#ifndef TOOLBOX_MAYA_MAYA_ERROR_HPP
#define TOOLBOX_MAYA_MAYA_ERROR_HPP

//#ifndef TOOLBOX_MAYA_NDEBUG
    #include <maya/MString.h>
    #include <maya/MStatus.h>
    // -------------------------
    #include <exception>
    // -------------------------
    #include <toolbox_config/tbx_macros.hpp>

//#endif // TOOLBOX_MAYA_NDEBUG

/**
 * Guidlines.
 *
 * Maya plugin are a pain to debug.
 * We need to print as much as possibles info into the Maya console because
 * using the debugger every time is not really productive.
 * To this end we use the following functions as much as possible.
 * - mayaCheck(); to check MStatus;
 * - mayaAssert(); instead of the standard tbx_assert();
 * - etc.
 *
 * On the other hand I encourage debugging of the implicit framework
 * using standard debugger and assertions. Just use a separate standalone
 * application easier to handle than Maya plugins.
*/


// =============================================================================
namespace tbx_maya {
// =============================================================================

#ifdef NDEBUG
    const bool g_debug_mode = false;
#else
    const bool g_debug_mode = true;
#endif

// -----------------------------------------------------------------------------
void maya_print_error(std::exception& e);

#ifndef TOOLBOX_MAYA_NDEBUG
/// _file : source file name
/// _line : source file line number
/// _function : function name the exception is thrown from
/// _reason : specific user message.
struct Maya_error {
    const MString _file;
    int _line;
    MString _function;
    std::string _stack;
    MString _code;
    MString _msg;
};

// -----------------------------------------------------------------------------

MString maya_error_string( const Maya_error& e);

void maya_print_error(const Maya_error& e);

void maya_print_warning(const Maya_error& e);

std::string get_stack_trace();

class Maya_exception : public std::runtime_error {
    static std::string make_error(MStatus status, const Maya_error& e);
public:

    Maya_exception(MStatus status_, const Maya_error& e);

    Maya_exception(const Maya_error& e);

private:
    //const MStatus _status;
};

#endif // TOOLBOX_MAYA_NDEBUG
}// END tbx_maya Namespace =====================================================


#ifndef TOOLBOX_MAYA_NDEBUG

/// Display a warning msge with reference to line number and file name.
#define mayaWarning(msg) do{ const int l = __LINE__;\
        tbx_maya::Maya_error err = {TBX_TO_STRING(__FILE__), l, TBX_FUNCTION_NAME, tbx_maya::get_stack_trace(), "", (msg)};\
        tbx_maya::maya_print_warning(err); \
    }while(false)

/// Throw exception along with your message (msg)
#define mayaAbort(msg) do{ const int l = __LINE__;\
        tbx_maya::Maya_error err = {TBX_TO_STRING(__FILE__), l, TBX_FUNCTION_NAME, tbx_maya::get_stack_trace(), "", (msg)};\
        throw tbx_maya::Maya_exception(err); \
    }while(false)

/// Don't use tbx_assert() they are a pain in Maya use this instead.
/// It will print a nicer error message.
#define mayaAssertMsg(state, msg) do{ const int l = __LINE__;\
        if( !(state) ){ \
            tbx_maya::Maya_error err = {TBX_TO_STRING(__FILE__), l, TBX_FUNCTION_NAME, tbx_maya::get_stack_trace(), TBX_TO_STRING(state), (msg)};\
            throw tbx_maya::Maya_exception(err); \
        }\
    }while(false)

#define mayaAssert(state) do{ const int l = __LINE__;\
        if( !(state) ){ \
            tbx_maya::Maya_error err = {TBX_TO_STRING(__FILE__), l, TBX_FUNCTION_NAME, tbx_maya::get_stack_trace(), TBX_TO_STRING(state), ""};\
            throw tbx_maya::Maya_exception(err); \
        }\
    }while(false)

/// @def mayaCheck
/// throws an exception when MStatuts fails.
#define mayaCheck(code) do{ const MStatus g_uniq_ShadoW_StatuS_(code); const int l = __LINE__;\
        if(g_uniq_ShadoW_StatuS_ != MS::kSuccess){ \
            tbx_maya::Maya_error err = {TBX_TO_STRING(__FILE__), l, TBX_FUNCTION_NAME, tbx_maya::get_stack_trace(), TBX_TO_STRING(code), ""};\
            throw tbx_maya::Maya_exception(g_uniq_ShadoW_StatuS_, err);\
        }\
    }while(false)

#else // RELEASE MODE

#define mayaWarning(msg) do{  }while(false)
#define mayaAbort(msg) do { throw std::runtime_error(MString(msg).asChar()); } while(false)
#define mayaAssertMsg(state, msg) do { } while(false)
#define mayaAssert(state) do { } while(false)
#define mayaCheck(code) do{ code; }while(false)

#endif

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_MAYA_ERROR_HPP
