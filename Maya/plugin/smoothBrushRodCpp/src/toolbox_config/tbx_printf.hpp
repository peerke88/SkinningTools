#ifndef TOOL_BOX_ASSERT_UTILS_HPP
#define TOOL_BOX_ASSERT_UTILS_HPP


#ifndef NDEBUG
#include "toolbox_config/char_array.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

/// @return the content of 'msg' with %f, %d etc. substituted with 'arguments[]'
Str get_fmessage(const char* msg,
                 const Str arguments[],
                 unsigned num_arg);

/// @param use_stderr : whether we use stderr as output or not
void print_message( const char* message, bool use_stderr = false);

void printf_message(const char* msg,
                    const tbx::Str arguments[],
                    unsigned num_arg,
                    bool use_stderr = false);

}// END tbx NAMESPACE ==========================================================
#endif


// tbx_printf() ===================================================================
#ifndef NDEBUG
    /// @def TBX_ANDROID_OS
    /// @brief print log message (platform independent)
    /// Works like any other printf() but flushes the output buffer to be sure
    /// your message is printed on screen as soon as possible:
    /// @code
    ///     tbx_printf("stuff %s %d", "bla", 5.0f);
    /// @endcode
    ///
    /// @note For android users: use the command "adb logcat"
    /// to access android logs. clear it with "adb logcat -c"
    ///
    //  @warning if you see the error "cannot pass objects of
    //  non-triavially-copyable type blabla through ..." it might mean an
    //  argument inside the "..." has the wrong type. Don't use std::string
    //  for instance
    #define tbx_printf(message, ...) do{\
            tbx::Str array[] = { "", ##__VA_ARGS__ };\
            const unsigned arg_num = sizeof(array)/sizeof(tbx::Str);\
            tbx::printf_message((message), (array+1), (arg_num-1));\
        }while(false)
#else
    #define tbx_printf(str, ...) do { } while(false)
#endif // ifndef NDEBUG
// END tbx_printf() ===============================================================



// tbx_print() ================================================================
#ifndef NDEBUG
    /// @def tbx_print
    /// @brief print a message with std::cout and flush
    ///
    /// To avoid relying on the heavy std::string use our lightweigth string:
    /// tbx::Str
    /// @code
    ///     tbx_print("A message\n");
    ///     tbx_print("A message and id: " + tbx::Str(10) + "\n");
    ///     // instead of:
    ///     tbx_print( (std::string("A message and id: ") + 10 + "\n").c_str() );
    /// @endcode
    #define tbx_print(str)\
    do{\
        tbx::print_message(str);\
    }while(false)
#else
    #define tbx_print(str) do { } while(false)
#endif // ifndef NDEBUG
// END tbx_print() ============================================================

#endif // TOOL_BOX_ASSERT_UTILS_HPP
