#include "toolbox_maya/utils/sub_mesh.hpp"

#include <numeric>
#include <toolbox_stl/vector.hpp>

// =============================================================================
namespace tbx_maya {
// =============================================================================

Sub_mesh::Sub_mesh(unsigned total)
{
    set(total);
}

// -----------------------------------------------------------------------------

void Sub_mesh::set(unsigned total)
{
    _vertex_list.resize( total );
    std::iota(std::begin(_vertex_list), std::end(_vertex_list), 0);
#if 0
    for(unsigned i = 0; i < _vertex_list.size(); ++i)
        _vertex_list[i] = i;
#endif
}

// -----------------------------------------------------------------------------

std::vector<int> Sub_mesh::vertex_list() const { return _vertex_list; }


}// END tbx_maya Namespace =====================================================
