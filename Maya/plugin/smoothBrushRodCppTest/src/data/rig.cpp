#include "data/rig.hpp"

#include <animation/skinning/skinning_utils.hpp>
#include <toolbox_maya/utils/progress_window.hpp>

#include <toolbox_algos/space_partition/grid_partition_utils.hpp>
#include "sbr_utils.hpp"

using namespace tbx;

// =============================================================================
namespace skin_brush {
// =============================================================================

Rig::~Rig() { clear(); }

// -----------------------------------------------------------------------------

void Rig::clear()
{
    _grid.release();
    _extra_vertex_links.clear();
    _user_extra_vertex_links.clear();
    _augmented_first_ring.clear();
    _augmented_per_edge_weights.clear();
    _weld_source_vertex.clear();
    _weld_list.clear();
}

// -----------------------------------------------------------------------------

Rig::Rig(const Maya_mesh& mesh, const Maya_skeleton& skel)
    : _mesh(mesh)
    , _skel(skel)
    , _user_extra_vertex_links(mesh.nb_vertices())
{
    float average_edge_len = mesh_utils::compute_average_edge_length( mesh.topo() );
    _user_radius_extra_links = average_edge_len * 0.5f;

    if( _user_radius_extra_links < 0.0f )
        _user_radius_extra_links = 0.5f;
}

// -----------------------------------------------------------------------------

Rig::Rig(const Rig& copy)
    : _mesh( copy.mesh() )
    , _skel( copy.skel() )
    , _user_radius_extra_links(copy._user_radius_extra_links)
    , _user_extra_vertex_links(copy._user_extra_vertex_links)
{
    _grid.release();

    if( is_extra_vertex_links_ready() )
        _extra_vertex_links = copy._extra_vertex_links;

    if( is_augmented_first_ring_ready() )
        _augmented_first_ring = copy._augmented_first_ring;

    if( is_augmented_per_edge_weights_ready() )
        _augmented_per_edge_weights = copy._augmented_per_edge_weights;

    if( is_weld_source_vertex_ready() )
        _weld_source_vertex = copy._weld_source_vertex;

    if( is_weld_list_ready() )
        _weld_list = copy._weld_list;

}

// -----------------------------------------------------------------------------

static inline
float get_merge_threshold(const tbx_mesh::Mesh_geometry& geom,
                          const Mesh_topology& topo,
                          tbx_mesh::Vert_idx vert_i)
{
    const Vec3 pos_i = geom.vertex( vert_i );
    float merge_threshold = std::numeric_limits<float>::infinity();
    float average_edge_len = 0.0f;
    for(tbx_mesh::Vert_idx vert_j : topo.first_ring_at(vert_i) )
    {
        Vec3 pos_j = geom.vertex(vert_j);
        average_edge_len += (pos_i - pos_j).norm();
    }
    average_edge_len /= float( topo.nb_neighbors(vert_i) );
    merge_threshold = average_edge_len * 0.05f; // Contributes less than five percent then we should merge.

    return merge_threshold;
}

// -----------------------------------------------------------------------------

/// @return every vertices within the sphere defined by 'center' and 'radius'
/// @param radius: sphere's radius
/// @param center: sphere's center
static
std::vector<tbx_mesh::Vert_idx> vertices_in_sphere(
        const tbx::Grid_partition<tbx_mesh::Vert_idx>& grid,
        const tbx_mesh::Mesh_geometry& geom,
        float radius,
        const Vec3 center)
{
    std::vector<tbx_mesh::Vert_idx> vertices;

    // radius == 0.5 * side_length of the square containing the sphere
    float half_diagonal = radius * std::sqrt(2.0f);

    // Bounding box that contain the sphere:
    tbx::Bbox3 bbox( center - Vec3(half_diagonal),
                     center + Vec3(half_diagonal));

    float cell_diagonal = grid.get_max_cell_diagonal() * 0.5f;
    for(int cell_idx : grid.get_sub_bounding_box( bbox ))
    {
        // Skip cells that are for sure outside the sphere
        float distance = (grid.cell_index_to_coordinates(cell_idx)-center).norm();
        if( (distance-radius, 0.0f) > cell_diagonal)
            continue;

        // Look up elements registered in the cell
         const std::list<tbx_mesh::Vert_idx>& list = grid.elements_at( cell_idx );
         for(int elt : list)
         {
             // Final precise check to make sure the vertex is within the sphere
             if( (geom.vertex(elt) - center).norm() <= radius )
                 vertices.push_back(elt);
         }
    }

    return vertices;
}

// -----------------------------------------------------------------------------

bool Rig::is_within_same_cluster(const std::vector<bone::Id>& rigid_partitions,
                              tbx_mesh::Vert_idx vert_i,
                              tbx_mesh::Vert_idx vert_j) const
{
    bone::Id bone_i = rigid_partitions[vert_i];
    bone::Id bone_j = rigid_partitions[vert_j];

             // Adjacent bone
    return ( skel().parent(bone_i) == bone_j ||
             skel().parent(bone_j) == bone_i ||
             // Or same bone
             bone_i == bone_j);
}

// -----------------------------------------------------------------------------

static inline
int get_nearest_to(
        const Vec3& pos_i,
        const std::vector<tbx_mesh::Vert_idx>& list,
        const tbx_mesh::Mesh_geometry& geom)
{
    int nearest = -1;
    float distance = std::numeric_limits<float>::infinity();
    for(unsigned vert_k = 0; vert_k < list.size(); ++vert_k)
    {
        float d = (geom.vertex( list[vert_k]) - pos_i).norm();
        if( d <  distance)
        {
            distance = d;
            nearest = vert_k;
        }
    }
    return nearest;
}


// -----------------------------------------------------------------------------

void Rig::compute_extra_links(
        std::vector< std::vector<tbx_mesh::Vert_idx> >& extra_vertex_links,
        std::vector< std::vector<tbx_mesh::Vert_idx> >& augmented_first_ring,
        std::vector< tbx_mesh::Vert_idx >& weld_source_vertex,
        std::vector< std::vector< tbx_mesh::Vert_idx > >& weld_list,
        float radius) const
{
    extra_vertex_links.  clear();
    extra_vertex_links.  resize( nb_vertices() );

    weld_source_vertex.clear();
    weld_source_vertex.resize(nb_vertices(), -1);

    weld_list.clear();
    weld_list.resize(nb_vertices());

    augmented_first_ring.clear();
    augmented_first_ring.resize( nb_vertices() );

    augmented_first_ring = topo().first_ring();

    // Compute rigid partitions:
    std::vector<bone::Id> rigid_partitions( skel()._weights.size() );
    for(unsigned vidx = 0; vidx < nb_vertices(); ++vidx){
        int max = anim::find_max_index(skel()._weights[vidx]);
        rigid_partitions[vidx] = max;
    }

    const tbx::Grid_partition<tbx_mesh::Vert_idx>& grid = get_grid_partition();

    Progress_window window("Compute extra edge links", nb_vertices());
    for(unsigned vert_i = 0; vert_i < nb_vertices(); ++vert_i)
    {
        if( window.is_canceled() ){
            break;
        }

        const Vec3 pos_i = geom().vertex( vert_i );

        float merge_threshold = get_merge_threshold(geom(), topo(), vert_i);

        std::vector<tbx_mesh::Vert_idx> inside_sphere = vertices_in_sphere(grid, geom(), radius, vertex(vert_i));
        std::vector<tbx_mesh::Vert_idx> filtered;
        for( tbx_mesh::Vert_idx candidate_neighbor : inside_sphere)
        {
            Vec3 pos = geom().vertex(candidate_neighbor);
            float distance = (pos_i - pos).norm();

            bool not_self          = candidate_neighbor != vert_i;
            bool can_weld          = distance < merge_threshold;
            bool same_geometry     = (topo().island_index(candidate_neighbor) == topo().island_index(vert_i));
            bool same_skin_cluster = is_within_same_cluster( rigid_partitions, vert_i, candidate_neighbor);
            if( not_self && (can_weld || (!same_geometry && same_skin_cluster)) )
            {
                filtered.push_back( candidate_neighbor );
            }
        }

        // When this number is too low relaxation or smoothing will not
        // not produce great results on complicated ares with a  bunch of
        // interleaved surfaces like belts, buttons and props gathered around the
        // same area.
        unsigned max_link_per_vert = 4;
        if(true) // Only retain nearest vertex
        {
            std::vector<tbx_mesh::Vert_idx> sorted;

            // Get two nearest vertices in order:
            for(unsigned c = 0; c < (max_link_per_vert); ++c)
            {
                int nearest = get_nearest_to(pos_i, /*in:*/filtered, geom());
                if( nearest > -1 ){
                    sorted.push_back( filtered[nearest] );
                    tbx::erase_pop(filtered, nearest);
                }

                if( filtered.size() == 0)
                    break;
            }

            filtered.clear();
            filtered = sorted;
        }

        for( tbx_mesh::Vert_idx new_neighbor : filtered)
        {            
            Vec3 pos_j = geom().vertex( new_neighbor );
            if( (pos_i - pos_j).norm() < merge_threshold /*0.0001f*/)
            {
                // Link too short:
                // dirty merge topology instead of creating a single link.

                // This is a hack to wait for the proper support of vertices weld.
                // Ideally We would like a pre-process that the input mesh and
                // makes it even cleaner for processing: including regulazing
                // triangles and welding vertices too close from each other
                // then we would map in a post process clean geom values -> to ->
                // original vertices


                /*
                    One drawback of this dirty merge is that we will have
                    redundant edges:

                       .----.----.
                      /     |     \
                     /      |      \
                   (*)-----(+)-----(*)

                   (*)-----(:)-----(*)
                     \      |      /
                      \     |     /
                       .----.----.

                       If we merge (+) and (:) we will produce redundant edges
                       if neighbors (*) are also seams!

                       In smoothing it should not be a problem (it will increase
                       computation time though)
                */

                for(tbx_mesh::Vert_idx idx : topo().first_ring_at(new_neighbor)) {
                    tbx::push_unique(augmented_first_ring[vert_i], idx);
                    tbx::push_unique(extra_vertex_links  [vert_i], idx);
                }

                // new_neighbor skin weights will be assigned to the values of
                // vert_i in a post process:
                weld_source_vertex[new_neighbor /*dst*/] = vert_i /*src*/;
                tbx::push_unique(weld_list[vert_i], new_neighbor);
            }
            else
            {
                tbx::push_unique(extra_vertex_links  [vert_i], new_neighbor);
                tbx::push_unique(augmented_first_ring[vert_i], new_neighbor);
            }
        }

        // Add user links if they exist:
        for(tbx_mesh::Vert_idx vert_j : _user_extra_vertex_links[vert_i])
        {
            tbx::push_unique(extra_vertex_links  [vert_i], vert_j);
            tbx::push_unique(augmented_first_ring[vert_i], vert_j);
        }

        window.add_progess();
    }

}

// -----------------------------------------------------------------------------

const tbx::Grid_partition<tbx_mesh::Vert_idx>&
Rig::get_grid_partition() const
{
    if( !is_grid_ready() ){
        _grid = Uptr< Grid_partition<tbx_mesh::Vert_idx> >( new Grid_partition<tbx_mesh::Vert_idx>() );
        build_grid_partition(*_grid, 64, geom());
    }
    return *_grid;
}

// -----------------------------------------------------------------------------

const std::vector< std::vector<tbx_mesh::Vert_idx> >&
Rig::get_extra_vertex_links() const
{
    if( !is_extra_vertex_links_ready() )
    {
        compute_extra_links(_extra_vertex_links,
                            _augmented_first_ring,
                            _weld_source_vertex,
                            _weld_list,
                            _user_radius_extra_links);
    }

    return _extra_vertex_links;
}

// -----------------------------------------------------------------------------

const std::vector< std::vector<tbx_mesh::Vert_idx> >&
Rig::get_augmented_first_ring() const
{
    if( !is_augmented_first_ring_ready() )
    {
        compute_extra_links(_extra_vertex_links,
                            _augmented_first_ring,
                            _weld_source_vertex,
                            _weld_list,
                            _user_radius_extra_links);
    }

    return _augmented_first_ring;
}

// -----------------------------------------------------------------------------

void Rig::compute_augmented_weights(
        const std::vector< std::vector<tbx_mesh::Vert_idx> >& augmented_first_ring) const
{
    _augmented_per_edge_weights.resize( nb_vertices() );
    for(unsigned vert_i = 0; vert_i < nb_vertices(); ++vert_i)
    {

        if(true)
        {
            if(get_extra_vertex_links()[vert_i].size() > 0)
            {
                // Extra links were created cotan doesn't make sens here
                // -> use edge length
                _augmented_per_edge_weights[vert_i] = mesh_utils::laplacian_edge_length_weights(geom(), augmented_first_ring, vert_i);
            }
            else
            {
                // Use cotan
                unsigned valence = unsigned(augmented_first_ring[vert_i].size());
                _augmented_per_edge_weights[vert_i].resize( valence );
                for(unsigned edge_j = 0; edge_j < valence; edge_j++)
                {
                    float wij = mesh_utils::laplacian_cotan_weight(geom(), topo(), vert_i, edge_j);
                    _augmented_per_edge_weights[vert_i][edge_j] = wij;
                }
            }
        }
        else
        {
            mesh_utils::uniform_weights(geom(), augmented_first_ring, _augmented_per_edge_weights);
        }
    }
}

// -----------------------------------------------------------------------------

const std::vector<tbx_mesh::Vert_idx>& Rig::get_weld_source_vertex() const
{
    if( !is_weld_source_vertex_ready() )
    {
        compute_extra_links(_extra_vertex_links,
                            _augmented_first_ring,
                            _weld_source_vertex,
                            _weld_list,
                            _user_radius_extra_links);
    }

    return _weld_source_vertex;
}

// -----------------------------------------------------------------------------

const std::vector <std::vector<int> >& Rig::get_weld_list() const
{
    if( !is_weld_list_ready() )
    {
        compute_extra_links(_extra_vertex_links,
                            _augmented_first_ring,
                            _weld_source_vertex,
                            _weld_list,
                            _user_radius_extra_links);
    }

    return _weld_list;
}

// -----------------------------------------------------------------------------

const std::vector< std::vector<float> >&
Rig::get_augmented_per_edge_weights() const
{
    if( !is_augmented_per_edge_weights_ready() )
    {
        compute_augmented_weights( get_augmented_first_ring() );
    }

    return _augmented_per_edge_weights;
}

// -----------------------------------------------------------------------------

const Maya_mesh& Rig::mesh() const { return _mesh; }

const Maya_skeleton& Rig::skel() const { return _skel; }

unsigned Rig::nb_vertices() const { return (unsigned)geom().nb_vertices(); }

Vec3 Rig::vertex(Vert_idx idx) const { return geom().vertex(idx); }

float Rig::get_user_radius_extra_links() const { return _user_radius_extra_links; }

// -----------------------------------------------------------------------------

bool Rig::is_grid_ready() const { return _grid.get() != nullptr; }

}// END tbx_maya Namespace =====================================================
