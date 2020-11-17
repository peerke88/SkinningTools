#ifndef TOOL_BOX_TBX_ASSERT_HPP
#define TOOL_BOX_TBX_ASSERT_HPP


#ifndef NDEBUG

#include "toolbox_config/tbx_macros.hpp"
#include "toolbox_config/char_array.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

struct Error {
    const char* _file; // On stack
    int _line;
    const char* _function;
    Str _stack;
    const char* _msg;
    tbx::Str* _arguments;
    unsigned _nb_args;
    const char* _expr; // On stack
};

void print_error( const Error& e);

void throw_runtime_error(const char* message);

Str get_stack_trace();

}// END tbx NAMESPACE ==========================================================
#endif // ifndef NDEBUG

// =============================================================================
// tbx_warning()
// =============================================================================
#ifndef NDEBUG
    /// @def tbx_warning
    /// @brief print a warning message with reference to line number
    /// file name, function name etc.
    #define tbx_warning(msg, ...) do{ const int l = __LINE__; \
            tbx::Str array[] = { "", ##__VA_ARGS__ };\
            const unsigned arg_num = sizeof(array)/sizeof(tbx::Str);\
            tbx::Error err = {TBX_TO_STRING(__FILE__), l, TBX_FUNCTION_NAME, /*tbx::get_stack_trace()*/"", (msg), (array+1), (arg_num-1), ""}; \
            tbx::print_error(err); \
        }while(false)
#else
    #define tbx_warning(msg, ...) do { } while(false)
#endif // ifndef NDEBUG
// END tbx_warning() ===========================================================


// =============================================================================
// tbx_assert_m()
// =============================================================================
#ifndef NDEBUG
    /// @def tbx_assert_m
    /// @brief asserts and print a message if triggered
    #define tbx_assert_m(expression, msg)  do{ const int l = __LINE__; \
        if(!(expression)){ \
            tbx::Error err = {TBX_TO_STRING(__FILE__), l, TBX_FUNCTION_NAME, tbx::get_stack_trace(), (msg), nullptr, 0, TBX_TO_STRING((expression))}; \
            tbx::print_error(err); \
            tbx::throw_runtime_error("tbx assert message"); \
        } \
    }while(false)
#else
    #define tbx_assert_m(a, str) do { } while(false)
#endif // ifndef NDEBUG
// END tbx_assert_m() ============================================================


// =============================================================================
// tbx_assert()
// =============================================================================
#ifndef NDEBUG
    /// @def tbx_assert_m
    /// @brief asserts and print a message if triggered
    #define tbx_assert(expression) do{ const int l = __LINE__; \
        if(!(expression)){ \
            tbx::Error err = {TBX_TO_STRING(__FILE__), l, TBX_FUNCTION_NAME, tbx::get_stack_trace(), (""), nullptr, 0, TBX_TO_STRING((expression))}; \
            tbx::print_error(err); \
            tbx::throw_runtime_error("tbx assert"); \
        } \
    }while(false)
#else
    #define tbx_assert(expression) do { } while(false)
#endif // ifndef NDEBUG
// END tbx_assert() ============================================================

#endif // TOOL_BOX_TBX_ASSERT_HPP
