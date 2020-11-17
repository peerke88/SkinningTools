#ifndef TOOLBOX_MAYA_SETTINGS_END_HPP
#define TOOLBOX_MAYA_SETTINGS_END_HPP

/**
 * @file settings_end.hpp
 * @brief File dedicated for internal use of the module toolbox_maya
 *
 * This file should be included at the very end of every toolbox_maya headers.
 * It contains various definitions to configure the way the library behave.
 */

/**
 * @def TBX_MAYA_ENABLE_USING_NAMESPACE_TBX_MAYA
 * @brief disabling tbx_maya namespace ::tbx_maya for faster code typing :)
 *
 * @warning will define using namespace ::tbx_maya in every toolbox_maya headers.
 * Use at your own risk.
 */
#ifdef TBX_MAYA_ENABLE_USING_NAMESPACE_TBX_MAYA
// Dummy namespace declaration needed for qtCreator autocompletion to work.
// Without a namespace declaration within the same file as the using namespace
// qtCreator will ignore the using namespace even though it is correctly
// included after the namespace
namespace tbx_maya { }
using namespace tbx_maya;
#endif

#endif // TOOLBOX_MAYA_SETTINGS_END_HPP

