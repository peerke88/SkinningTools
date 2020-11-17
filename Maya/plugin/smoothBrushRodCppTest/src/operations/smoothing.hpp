#ifndef SMOOTHING_HPP
#define SMOOTHING_HPP

#include <vector>
#include <map>
#include <toolbox_maths/vector2.hpp>

// Forward declaration ---------------------------------------------------------
namespace tbx_maya {
    class Sub_mesh;
}
namespace skin_brush {
    struct Joint_scopes;
    class Rig;
}
// Forward declaration end -----------------------------------------------------

// =============================================================================
namespace skin_brush {
// =============================================================================

enum Smoothing_type {
    /// Every neighbors weigh the same:
    /// it won't preserve mesh irregularities / details
    eUNIFORM = 0,
    /// The closer the neighbor the greater its barycentric weight:
    /// will approximately preserve mesh details but for the same shape will
    /// return different results for different triangulation of the mesh.
    eEDGE_LENGTH,
    /// Barycentric weight take into account the shape of the triangles:
    /// Preserve details
    /// Smoothing will converge to linear maps
    eCOTAN,
    /// Use edge length scheme for extra links (typically added between
    /// separated mesh islands) then use cotan weights otherwise:    
    eMIXED_LINK
};

void smooth_skin_weights_all_joints(std::vector<std::map<int, float> >& weights,
                                    const Rig& rig,                                    
                                    const std::vector<tbx::Vec2>& constraints,
                                    int max_influences,
                                    const std::vector<bool>& locked_joints,
                                    const tbx_maya::Sub_mesh& sub_mesh,
                                    Smoothing_type type = eCOTAN);


}// END skin_brush Namespace ========================================


#endif // CMD_SKINNING_WEIGHTS_HPP
