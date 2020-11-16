#include "toolbox_mesh/topology/vertex_to_1st_ring_vertices.hpp"

#include <deque>

// =============================================================================
namespace tbx_mesh {
// =============================================================================

/** given a triangle 'tri' and one of its vertex index 'current_vert'
    return the pair corresponding to the vertex index opposite to 'current_vert'
    @code
      "current_vert"
            *
           / \
          /   \
         *_____*
    second     first  <--- find the opposite pair
    @endcode
 */
static
std::pair<int, int> pair_from_tri(const Tri_face& tri,
                                  int current_vert)
{
    int ids[2] = {-1, -1};
    for(int i = 0; i < 3; i++)
    {
        if(tri[i] == current_vert)
        {
            ids[0] = tri[ (i+1) % 3 ];
            ids[1] = tri[ (i+2) % 3 ];
            break;
        }
    }
    return std::pair<int, int>(ids[0], ids[1]);
}

// -----------------------------------------------------------------------------

/// Same as pair_from_tri() but with quads. 'n' is between [0 1] and tells
/// if the first or the seccond pair of vertex is to be choosen.
static
std::pair<int, int> pair_from_quad(const Quad_face& quad,
                                   int current_vert,
                                   int n)
{
    tbx_assert(n == 1 || n == 0);
    int ids[3] = {-1, -1, -1};
    for(int i = 0; i < 4; i++)
    {
        if(quad[i] == current_vert)
        {
            ids[0] = quad[ (i+1) % 4 ];
            ids[1] = quad[ (i+2) % 4 ];
            ids[2] = quad[ (i+3) % 4 ];
            break;
        }
    }

    return std::pair<int, int>(ids[0+n], ids[1+n]);
}

// -----------------------------------------------------------------------------

static
bool add_to_ring(std::deque<int>& ring, std::pair<int, int> p)
{
    if(ring[ring.size()-1] == p.first)
    {
        ring.push_back(p.second);
        return true;
    }
    else if(ring[ring.size()-1] == p.second)
    {

        ring.push_back(p.first);
        return true;
    }
    else if(ring[0] == p.second)
    {
        ring.push_front(p.first);
        return true;
    }
    else if(ring[0] == p.first)
    {
        ring.push_front(p.second);
        return true;
    }
    return false;
}

// -----------------------------------------------------------------------------

/// Add an element to the ring only if it does not already exists
/// @return true if already exists
static
bool add_to_ring(std::deque<int>& ring, int neigh)
{
    std::deque<int>::iterator it;
    for(it = ring.begin(); it != ring.end(); ++it)
        if(*it == neigh) return true;

    ring.push_back( neigh );
    return false;
}

void Vertex_to_1st_ring_vertices::compute(
        const Mesh_geometry& mesh,
        const Vertex_to_face& vert_to_face)
{
    _is_mesh_closed = true;
    _is_mesh_manifold = true;
    _not_manifold_verts.clear();
    _on_side_verts.clear();

    _is_vert_on_side.resize( mesh.nb_vertices() );

    _rings_per_vertex.clear();
    _rings_per_vertex.resize( mesh.nb_vertices() );
    const std::vector<std::vector<Tri_idx> >& tri_list_per_vert = vert_to_face._1st_ring_tris;
    const std::vector<std::vector<Quad_idx> >& quad_list_per_vert = vert_to_face._1st_ring_quads;
    const std::vector<bool>& is_connected = vert_to_face._is_vertex_connected;

    std::vector<std::pair<int, int> > list_pairs;
    list_pairs.reserve(16);
    for(int i = 0; i < mesh.nb_vertices(); i++)
    {
        // We suppose the faces are quads to reserve memory
        if( tri_list_per_vert[i].size() > 0)
            _rings_per_vertex[i].reserve(tri_list_per_vert[i].size());

        if( !is_connected[i] )
            continue;

        list_pairs.clear();
        // fill pairs with the first ring of neighborhood of quads and triangles
        for(unsigned j = 0; j < tri_list_per_vert[i].size(); j++)
            list_pairs.push_back(pair_from_tri(mesh.triangle( tri_list_per_vert[i][j] ), i));

        for(unsigned j = 0; j < quad_list_per_vert[i].size(); j++)
        {
            list_pairs.push_back(pair_from_quad(mesh.quad( quad_list_per_vert[i][j] ), i, 0));
            list_pairs.push_back(pair_from_quad(mesh.quad( quad_list_per_vert[i][j] ), i, 1));
        }

        // Try to build the ordered list of the first ring of neighborhood of i
        std::deque<int> ring;
        ring.push_back(list_pairs[0].first );
        ring.push_back(list_pairs[0].second);
        std::vector<std::pair<int, int> >::iterator it = list_pairs.begin();
        list_pairs.erase(it);
        size_t  pairs_left = list_pairs.size();
        bool manifold   = true;
        while( (pairs_left = list_pairs.size()) != 0)
        {
            for(it = list_pairs.begin(); it < list_pairs.end(); ++it)
            {
                if(add_to_ring(ring, *it)) {
                    list_pairs.erase(it);
                    break;
                }
            }

            if(pairs_left == list_pairs.size()) {
                // Not manifold we push neighborhoods of vert 'i'
                // in a random order
                add_to_ring(ring, list_pairs[0].first );
                add_to_ring(ring, list_pairs[0].second);
                list_pairs.erase(list_pairs.begin());
                manifold = false;
            }
        }

        if(!manifold) {
            _is_mesh_manifold = false;
            _not_manifold_verts.push_back(i);
        }

        if(ring[0] != ring[ring.size()-1]){
            _is_vert_on_side[i] = true;
            _on_side_verts.push_back(i);
            _is_mesh_closed = false;
        } else {
            _is_vert_on_side[i] = false;
            ring.pop_back();
        }

        for(unsigned int j = 0; j < ring.size(); j++)
            _rings_per_vertex[i].push_back( ring[j] );
    }// END FOR( EACH VERTEX )
}

}// END tbx_mesh NAMESPACE =====================================================
