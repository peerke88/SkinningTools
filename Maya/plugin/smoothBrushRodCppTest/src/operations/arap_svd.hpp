#ifndef ARAP_SVD_HPP
#define ARAP_SVD_HPP

#include "data/skin_deformer.hpp"

#include <toolbox_maths/quat.hpp>
#include <toolbox_mesh/iterators/first_ring_it.hpp>
#include <toolbox_maya/utils/sub_mesh.hpp>

// Forward declaration ---------------------------------------------------------
namespace skin_brush {
}
// Forward declaration end -----------------------------------------------------

// =============================================================================
namespace skin_brush {
// =============================================================================

// Full SVD safest implementation I know of
void compute_SVD_rotations(std::vector<tbx::Mat3>& svd_rotations,
                           const std::vector<std::map<int, float> >& weights,
                           const First_ring_it& topo,
                           const std::vector<Vec3>& vertices,
                           const Sub_mesh& sub_mesh,
                           const std::vector< std::vector<float> >& per_edge_weights,
                           const Skin_deformer& dfm);

// Mathias implementation maybe less robust
void compute_SVD_rotations_with_quats(
        std::vector<tbx::Mat3>& svd_rotations,
        std::vector<tbx::Quat>& quat_rotations,
        const std::vector<std::map<int, float> >& weights,
        const First_ring_it& topo,
        const std::vector<Vec3>& vertices,
        const Sub_mesh& sub_mesh,
        const std::vector< std::vector<float> >& per_edge_weights,
        const Skin_deformer& dfm);

}// END skin_brush Namespace ========================================

#endif // ARAP_SVD_HPP
