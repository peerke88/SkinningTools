#include "toolbox_config/tbx_assert.hpp"

#ifndef NDEBUG

#include "toolbox_config/tbx_printf.hpp"

// Hiding heavy headers here:
#include <string>
#include <algorithm>
#include <iostream>

// =============================================================================
namespace tbx {
// =============================================================================

///@return a copy of 'str' with all occurences of 'src' replaced by 'dst'
inline static std::string replace(const std::string& str, char src, char dst)
{
    std::string res = str;
    std::replace( res.begin(), res.end(), src, dst);
    return res;
}

// -----------------------------------------------------------------------------

/// @return the file name from a given file's full path.
/// Most of the time this function behaves similarly to the unix basename(1)
/// command. It will ignore any trailing slash.
inline static std::string get_base_name( const std::string& path )
{
    std::string res;
    // Anti-slashes become slashes (windows path handling)
    res = tbx::replace(path, '\\', '/');

    // We remove any trailing slashes.
    size_t pos = res.find_last_not_of('/');
    // Don't strip the last / from "/"
    if (pos == std::string::npos)
    {
        pos = res.find_first_of("/");
    }

    res = res.substr(0, pos + 1);

    // Now find the previous slash and cut the string.
    pos = res.find_last_of('/');

    if( pos != std::string::npos )
    {
        res = res.substr(pos+1);
    }

    return res;
}

// -----------------------------------------------------------------------------

///@return a copy of 'str' with all occurences of 'charac' removed
inline static std::string remove(const std::string& str, char charac)
{
    std::string res = str;
    res.erase(std::remove(res.begin(), res.end(), charac), res.end());
    return res;
}

// -----------------------------------------------------------------------------

#ifdef NDEBUG
    const bool g_debug_mode = false;
#else
    const bool g_debug_mode = true;
#endif

std::string error_string(const Error& e)
{
    std::string err;
    err += "\n";

    std::string expr(e._expr);
    if( expr.length() )
        err += "Expression: " + expr + "\n";

    std::string msg(e._msg);
    if( msg.length() )
        err += "Message: " + tbx::get_fmessage(e._msg, e._arguments, e._nb_args) + "\n";

    std::string file_name = tbx::get_base_name(tbx::remove(e._file, '"'));
    err += "Line: ("+std::to_string(e._line)+") File: "+file_name+"\n";
    err += "Function: "+std::string(e._function)+"\n";
    err += "File path: " + std::string(e._file) + "\n";

    std::string stack(e._stack);
    if( g_debug_mode && stack.length() )
    {
        err += "==== BEGIN STACK TRACE ====\n";
        err += stack;
        err += "====  END STACK TRACE  ====\n";
    }
    err += "\n";
    return err;
}

// -----------------------------------------------------------------------------

Str get_stack_trace(){
    // Since stack tracing is slow we only do it in debug mode
    return "Trace disabled\n";
    //return "Trace disabled\n";
}

// -----------------------------------------------------------------------------

void print_error( const Error& err)
{
    std::cerr << tbx::error_string(err) << std::endl;
}

void throw_runtime_error(const char* message)
{
    throw  std::runtime_error(message);
}

}// END tbx NAMESPACE ==========================================================

#endif // NDEBUG
