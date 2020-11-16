#pragma once

#include <vector>
#include <map>
#include <utility>
#include <toolbox_maths/dual_quat.hpp>

// =============================================================================
namespace anim {
// =============================================================================

static inline
/// Skinning with Dual Quaternions from Kavan & Al
tbx::Dual_quat dual_quaternion_blending(
        const std::map<int, float>& bones,
        const std::vector<tbx::Dual_quat>& dual_quat)
{
    tbx::Dual_quat dq_blend;
    tbx::Quat q0;
    if(bones.size() > 0)
    {
        dq_blend = tbx::Dual_quat(tbx::Quat(0.0f, 0.0f, 0.0f, 0.0f),
                                  tbx::Quat(0.0f, 0.0f, 0.0f, 0.0f));

        q0 = dual_quat[ bones.begin()->first ].get_non_dual_part();
        for( std::pair<int, float> pair : bones) {
            float w = pair.second;
            const tbx::Dual_quat& dq = dual_quat[ pair.first ];

            if( dq.get_non_dual_part().dot( q0 ) < 0.f ) // Choose the shortest rotation path
                w *= -1.f;

            dq_blend += dq * w;
        }

    }else {
        dq_blend = tbx::Dual_quat::identity();
    }

    return dq_blend;
}

} // END anim NAMESPACE ========================================================


