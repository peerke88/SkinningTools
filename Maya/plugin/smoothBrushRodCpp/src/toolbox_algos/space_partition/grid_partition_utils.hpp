#ifndef TOOL_BOX_GRID_PARTITION_UTILS_HPP
#define TOOL_BOX_GRID_PARTITION_UTILS_HPP

#include "toolbox_algos/space_partition/grid_partition.hpp"
#include "toolbox_mesh/mesh_geometry.hpp"
#include "toolbox_mesh/mesh_utils.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

void build_grid_partition(
        Grid_partition<tbx_mesh::Vert_idx>& grid,
        int resolution,
        const tbx_mesh::Mesh_geometry& geom)
{
    grid.init(Vec3_i(resolution), tbx_mesh::mesh_utils::bounding_box(geom));
    for(int i = 0; i < geom.nb_vertices(); ++i) {
        grid.insert( geom.vertex(i), i );
    }
}

}// END tbx NAMESPACE ==========================================================

#include "toolbox_algos/settings_end.hpp"

#endif // TOOL_BOX_GRID_PARTITION_UTILS_HPP
