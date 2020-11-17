#ifndef TOOL_BOX_STD_UTILS_STRING_HPP
#define TOOL_BOX_STD_UTILS_STRING_HPP

#include <cstring>
#include <cstdarg>
#include <sstream>
#include <algorithm>
#include <memory>
#include <vector>

// =============================================================================
namespace tbx {
// =============================================================================

/// @brief split a string with a character delimiter
/// @return split("jhon:sam:clair", ':') -> {"jhon", "sam", "clair"}
inline static std::vector<std::string> split(const std::string& str, char delim = ' ')
{
    std::vector<std::string> res;
    std::stringstream ss(str);
    std::string token;
    while (std::getline(ss, token, delim)) {
        res.push_back(token);
    }
    return res;
}

// -----------------------------------------------------------------------------

/// @brief split a string with a string delimiter
/// @return split("jhon>=sam>=clair", ">=") -> {"jhon", "sam", "clair"}
inline static
std::vector<std::string> split(const std::string& str, const std::string& delimiter)
{
    std::vector<std::string> res;
    size_t pos = 0;
    std::string token;
    std::string s = str;
    while ((pos = s.find(delimiter)) != std::string::npos) {
        token = s.substr(0, pos);
        res.push_back( token );
        s.erase(0, pos + delimiter.length());
    }
    res.push_back( s );
    return res;
}

// -----------------------------------------------------------------------------

/// Convert a scalar (int float double long unsigned etc.) to a string
/// @warning no type checking is done
// Possibly later we could specialized the template
#if 0
template<typename T>
static std::string to_string(T number)
{
   std::stringstream ss;
   ss << number;
   return ss.str();
}
#else
using std::to_string;
#endif

// -----------------------------------------------------------------------------

/// Converting a string to real value.
/// the template parameter will not be infered call with this syntax:
/// @code
///     float v = tbx::to_real<float>( str_val );
///     int   v = tbx::to_real<int>  ( str_val );
/// @endcode
template<typename T>
static T to_real(const std::string& number)
{
    std::stringstream ss( number );
    T real;
    ss >> real;
    return real;
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

///@return a copy of 'str' with all occurences of 'src' replaced by 'dst'
inline static std::string replace(const std::string& str, char src, char dst)
{
    std::string res = str;
    std::replace( res.begin(), res.end(), src, dst);
    return res;
}

// -----------------------------------------------------------------------------

///@return true if (to_find) is found in (str)
inline static bool exists(const std::string& str, const std::string& to_find )
{
    return str.find(to_find) != std::string::npos;
}

// -----------------------------------------------------------------------------

/// @return the path to a parent directory of a given file's full path.
/// Most of the time this function behaves similarly to the unix dirname(1)
/// command. It will ignore any trailing slash.
inline std::string get_dir_name( const std::string& path )
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

    res = res.substr(0, pos + 1 );

    // Now find the previous slash and cut the string.
    pos = res.find_last_of('/');

    // The directory is actually "/" because the last slash is in first position.
    // In that case we should return "/"
    if ( pos == 0 )
    {
        res = "/";
    }
    else if ( pos != std::string::npos )
    {
        res = res.substr(0, pos );
    }
    else
    {
        res = ".";
    }

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

/// Writes a formatted print into the given string, similarly to sprintf.
/// @return the number of characters printed, or a negative value if there was
///  any error.
inline static int string_printf(std::string& str, const char* fmt, ... )
{
    // Random guessing value from the size of the format string.
    int size = (int)strlen(fmt) * 2;
    int final_size = 0 ;
    str.clear();

    std::unique_ptr<char[]> buffer;
    va_list args;

    while(1)
    {
        // Dynamically allocate a string and assign it to the unique ptr
        buffer.reset( new char [size] );

        // Attempt to printf into the buffer
        va_start(args, fmt);
        final_size = vsnprintf( &buffer[0], (size_t)size, fmt, args );
        va_end(args);

        // If our buffer was too small, we know that final_size
        // gives us the required buffer size.
        if (final_size >= size )
        {
            size = std::max( size + 1, final_size );
        }
        else
        {
            break;
        }
    }
    if (final_size > 0 )
    {
        str = std::string(buffer.get());
    }
    return final_size;
}

}// END tbx NAMESPACE ==========================================================

#include "toolbox_stl/settings_end.hpp"

#endif // TOOL_BOX_STD_UTILS_STRING_HPP
