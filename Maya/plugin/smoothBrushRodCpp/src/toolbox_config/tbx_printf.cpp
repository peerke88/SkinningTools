#include "toolbox_config/tbx_printf.hpp"

#ifndef NDEBUG
#include "toolbox_config/char_array.hpp"

// Heavy headers hidden here:
#include <iostream>
#include <vector>
#include <string>

#ifdef TBX_ANDROID_OS
     #include <android/log.h>
#else
     #include <cstdio>
#endif

// =============================================================================
namespace tbx {
// =============================================================================

void print_message( const char* message, bool use_stderr)
{
    #ifdef TBX_ANDROID_OS
        __android_log_print(ANDROID_LOG_ERROR, "!! TBX ERROR MSG: ", (message));
        fflush(stdout);
    #else
    if( use_stderr ){
        std::cout << message;
        std::cout << std::flush;
    }else{
        std::cerr << message;
        std::cerr << std::flush;
    }
    #endif
}

// -----------------------------------------------------------------------------

inline static
std::vector<std::string> split_format_string(const std::string& str)
{
    std::vector<std::string> res;
    size_t pos = 0;
    std::string token;
    std::string s = str;
    while ((pos = s.find('%')) != std::string::npos) {
        token = s.substr(0, pos);
        res.push_back( token );
        s.erase(0, pos + 2);
    }
    //if( s.length() > 0)
    res.push_back( s );
    return res;
}

// -----------------------------------------------------------------------------

Str get_fmessage(const char* msg,
                 const Str arguments[],
                 unsigned num_arg)
{
    std::string res = "";
    std::vector<std::string> token_list = split_format_string(std::string(msg));

    num_arg = (token_list.size()-1) > num_arg ? num_arg : unsigned(token_list.size()-1);
    for(unsigned i = 0; i < num_arg; ++i) {
        res = res + token_list[i] + arguments[i].c_str();
    }

    if( token_list.back().length() > 0 )
        res += token_list.back();

    return Str(res.c_str());
}

// -----------------------------------------------------------------------------

void printf_message(const char* msg,
                    const Str arguments[],
                    unsigned num_arg,
                    bool use_stderr)
{
    print_message( get_fmessage(msg, arguments, num_arg), use_stderr);
}

}// END tbx NAMESPACE ==========================================================
#endif
