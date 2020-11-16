#ifndef TOOL_BOX_META_MATH_CU_HPP
#define TOOL_BOX_META_MATH_CU_HPP

/*
https://en.wikipedia.org/wiki/Microsoft_Visual_C%2B%2B#Internal_version_numbering
MSVC++ 14.2  _MSC_VER == 1920 (Visual Studio 2019 Version 16.0)
MSVC++ 14.16 _MSC_VER == 1916 (Visual Studio 2017 version 15.9)
MSVC++ 14.15 _MSC_VER == 1915 (Visual Studio 2017 version 15.8)
MSVC++ 14.14 _MSC_VER == 1914 (Visual Studio 2017 version 15.7)
MSVC++ 14.13 _MSC_VER == 1913 (Visual Studio 2017 version 15.6)
MSVC++ 14.12 _MSC_VER == 1912 (Visual Studio 2017 version 15.5)
MSVC++ 14.11 _MSC_VER == 1911 (Visual Studio 2017 version 15.3)
MSVC++ 14.1  _MSC_VER == 1910 (Visual Studio 2017 version 15.0)
MSVC++ 14.0  _MSC_VER == 1900 (Visual Studio 2015 version 14.0)
MSVC++ 12.0  _MSC_VER == 1800 (Visual Studio 2013 version 12.0)
MSVC++ 11.0  _MSC_VER == 1700 (Visual Studio 2012 version 11.0)
MSVC++ 10.0  _MSC_VER == 1600 (Visual Studio 2010 version 10.0)
MSVC++ 9.0   _MSC_FULL_VER == 150030729 (Visual Studio 2008, SP1)
MSVC++ 9.0   _MSC_VER == 1500 (Visual Studio 2008 version 9.0)
MSVC++ 8.0   _MSC_VER == 1400 (Visual Studio 2005 version 8.0)
MSVC++ 7.1   _MSC_VER == 1310 (Visual Studio .NET 2003 version 7.1)
MSVC++ 7.0   _MSC_VER == 1300 (Visual Studio .NET 2002 version 7.0)
MSVC++ 6.0   _MSC_VER == 1200 (Visual Studio 6.0 version 6.0)
MSVC++ 5.0   _MSC_VER == 1100 (Visual Studio 97 version 5.0)
 *
 */

/** @file math_cu.hpp

  This header allows to use maths functions in nvcc, gcc, msvc... compilers

*/

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

#ifdef __CUDACC__

    #include <cuda_runtime.h>
    #include <math_constants.h>

#else

    #include <cmath>
//    #ifdef isnan
//        //#warning "WARNING: isnan was defined, removing definition"
//        #undef isnan // Prevents definition of macro min max
//    #endif

    #ifndef _MSC_VER
        inline float floorf(float a) { return floor(a); }
    #endif

    #if (_MSC_VER == 1800)
        #include "float.h"
        inline int isnan(double v){ return _isnan(v); }
    #else
        //inline int isnan(double v){ return std::isnan(v); }
    #endif

    #ifdef __MINGW32__
        //inline int isnan(double v){ return std::isnan(v); }
    #endif

    #if defined(_WIN32) || defined(_MSC_VER)
        #ifdef max
            #undef max // Prevents definition of macro min max
        #endif
        #ifdef min
            #undef min  // Prevents definition of macro min max
        #endif
    #endif


#endif

#endif // TOOL_BOX_META_MATH_CU_HPP
