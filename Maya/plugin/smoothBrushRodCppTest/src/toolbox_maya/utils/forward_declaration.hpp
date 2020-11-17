#ifndef TBX_MAYA_FORWARD_DECLARATION_HPP
#define TBX_MAYA_FORWARD_DECLARATION_HPP


/**
    Since Maya 2018 forward declarations were banned and you need to include
    MApiNamespace.h instead. To use forward declaration across all Maya API use
    this header as follows:

    @code
    // Place this on the top of your header where you declare all your includes:

    #include "toolbox_maya/utils/forward_declaration.hpp"
    TBX_MAYA_FORWARD_DECLARATION(class MDataBlock);
    TBX_MAYA_FORWARD_DECLARATION(class MObject);
    //etc.
    @endcode
*/

#include <maya/MTypes.h>
#if MAYA_API_VERSION >= 20180000
// Since Maya 2018 forward declaration must be done through this header:
#include <maya/MApiNamespace.h>
#endif

#if MAYA_API_VERSION >= 20180000
    #define TBX_MAYA_FORWARD_DECLARATION(dcl)
#else
    #define TBX_MAYA_FORWARD_DECLARATION(dcl) dcl
#endif


#endif // TBX_MAYA_FORWARD_DECLARATION_HPP
