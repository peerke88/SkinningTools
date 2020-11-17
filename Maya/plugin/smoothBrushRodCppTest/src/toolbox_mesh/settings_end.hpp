#ifndef TOOLBOX_MESH_SETTINGS_END_HPP
#define TOOLBOX_MESH_SETTINGS_END_HPP

/**
 * @file settings_end.hpp
 * @brief File dedicated for internal use of the toolbox_mesh
 *
 * This file should be included at the very end of every toolbox headers.
 * It contains various definitions to configure the way the library behave.
 */

/**
 * @def TBX_MESH_ENABLE_USING_NAMESPACE_TBX_MESH
 * @brief disabling toolbox_mesh namespace ::tbx_mesh for faster code typing :)
 *
 * @warning will define using namespace ::tbx_mesh in every toolbox headers.
 * Use at your own risk.
 */
#ifdef TBX_MESH_ENABLE_USING_NAMESPACE_TBX_MESH
// Dummy namespace declaration needed for qtCreator autocompletion to work.
// Without a namespace declaration within the same file as the using namespace
// qtCreator will ignore the using namespace even though it is correctly
// included after the namespace
namespace tbx_mesh { }
using namespace tbx_mesh;
#endif

#endif // TOOLBOX_MESH_SETTINGS_END_HPP

