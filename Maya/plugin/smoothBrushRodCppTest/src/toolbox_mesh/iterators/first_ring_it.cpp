#include "toolbox_mesh/iterators/first_ring_it.hpp"

#include "toolbox_mesh/mesh_topology.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

First_ring_it::First_ring_it(const Mesh_topology& topo)
    : _first_ring(topo.first_ring())
{

}

First_ring_it::First_ring_it(const Mesh_topology_lvl_1& topo)
    : _first_ring(topo.first_ring())
{

}

}// END tbx_mesh NAMESPACE =====================================================
