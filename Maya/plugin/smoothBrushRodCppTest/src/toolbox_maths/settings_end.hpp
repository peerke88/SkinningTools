#pragma once

/**
 * @file settings_end.hpp
 * @brief File dedicated for internal use of the tool_box
 *
 * This file should be included at the very end of every toolbox headers.
 * It contains various definitions to configure the way the library behave.
 */

/**
 * @def TBX_ENABLE_USING_NAMESPACE_TBX
 * @brief disabling tool_box namespace ::tbx for faster code typing :)
 *
 * @warning will define using namespace ::tbx in every toolbox headers. Use at
 * your own risk.
 */
#ifdef TBX_ENABLE_USING_NAMESPACE_TBX
// Dummy namespace declaration needed for qtCreator autocompletion to work.
// Without a namespace declaration within the same file as the using namespace
// qtCreator will ignore the using namespace even though it is correctly
// included after the namespace
namespace tbx { }
using namespace tbx;
#endif

