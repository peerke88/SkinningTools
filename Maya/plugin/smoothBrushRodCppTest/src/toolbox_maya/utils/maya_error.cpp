#include "toolbox_maya/utils/maya_error.hpp"

#include <maya/MGlobal.h>

#ifndef TOOLBOX_MAYA_NDEBUG
//#include "toolbox_config/stacktrace/call_stack.hpp"
#include "toolbox_stl/string.hpp"
#endif

// =============================================================================
namespace tbx_maya {
// =============================================================================


void maya_print_error(std::exception& e)
{
    MGlobal::displayError( e.what() );
    std::cerr << e.what();
}

#ifndef TOOLBOX_MAYA_NDEBUG
// -----------------------------------------------------------------------------

MString maya_error_string(const Maya_error& e)
{
    MString err;
    err += "\n";
    if( e._msg.length() )
        err += ": " + e._msg + "\n";
    if( e._code.length() ) {
        err += "Statement: (";
        err += e._code + ")\n";
    }
    err += "Line: (";
    err += e._line;
    err += ") File: ";
    err += tbx::get_base_name(tbx::remove(e._file.asUTF8(), '"')).c_str();
    err += "\n";
    err += "Function: ";
    err += e._function;
    err += "\n";
    err += "File path: " + e._file + "\n";
    if( g_debug_mode )
    {
        err += "--- Stack Trace ---\n";
        err += e._stack.c_str();
        err += "--- Stack Trace End ---\n";
    }
    err += "\n";
    return err;
}

// -----------------------------------------------------------------------------

void maya_print_error(const Maya_error& e)
{
    MString err = maya_error_string(e);
    MGlobal::displayError(err);
    std::cerr << err;
}

// -----------------------------------------------------------------------------

void maya_print_warning(const Maya_error& e)
{
    MString err = maya_error_string(e);
    MGlobal::displayWarning(err);
    std::cout << err;
}

// -----------------------------------------------------------------------------

std::string get_stack_trace(){
    // Since stack tracing is slow we only do it in debug mode
    return "Trace disabled\n";
    //return g_debug_mode? tbx::stacktrace::get(1) : "Trace disabled\n";
}

// -----------------------------------------------------------------------------

std::string Maya_exception::make_error(MStatus status, const Maya_error& e)
{
    MString err;
    err += "[Begin]\n";
    err += maya_error_string(e);
    err += "MStatus: " + status.errorString() + "\n";
    err += "[end]\n";
    return err.asChar();
}

// -----------------------------------------------------------------------------

Maya_exception::Maya_exception(MStatus status_, const Maya_error& e)
    : std::runtime_error( make_error(status_, e) )
    //, _status(status_)
{
}

// -----------------------------------------------------------------------------

Maya_exception::Maya_exception(const Maya_error& e)
    : std::runtime_error( maya_error_string(e).asUTF8() )
    //, _status(MS::kFailure)
{

}

#endif

}// END tbx_maya Namespace =====================================================

