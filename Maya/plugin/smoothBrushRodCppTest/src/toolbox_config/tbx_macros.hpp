#ifndef TOOL_BOX_TBX_MACROS_HPP
#define TOOL_BOX_TBX_MACROS_HPP

// -----------------------------------------------------------------------------

#ifndef TBX_TO_STRING
    #define TBX_TO_STRING(x) TBX_EVAL_STRING(x)
    #define TBX_EVAL_STRING(x) #x
#endif

// -----------------------------------------------------------------------------

#ifndef TBX_FUNCTION_NAME
    #ifdef WIN32   //WINDOWS
        #define TBX_FUNCTION_NAME   __FUNCTION__
    #else          //*NIX
        #define TBX_FUNCTION_NAME   __func__
    #endif
#endif

// -----------------------------------------------------------------------------

#endif // TOOL_BOX_TBX_MACROS_HPP
