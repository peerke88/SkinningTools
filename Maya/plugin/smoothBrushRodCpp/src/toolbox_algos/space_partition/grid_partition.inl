#include "toolbox_algos/space_partition/grid_partition.hpp"

#include "toolbox_maths/calculus.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

template<class T_idx>
Grid_partition<T_idx>::Grid_partition(const Vec3_i& resolution,
                               const Vec3& size,
                               const Vec3& start,
                               int hint_nb_elts)

    : _resolution(resolution)
    , _size(size)
    , _cell_lengths( _size.div( Vec3(_resolution) ) )
    , _start( start )
    , _data( resolution.product() )
{
    if( hint_nb_elts == -1 )
        _filled_cells.reserve(resolution.product()/4);
    else
        _filled_cells.reserve( tbx::min(resolution.product(), hint_nb_elts) );
}

// -----------------------------------------------------------------------------

template<class T_idx>
Grid_partition<T_idx>::Grid_partition(const Vec3_i& resolution,
                               const Bbox3& bbox,
                               int hint_nb_elts)
{
    init(resolution, bbox, hint_nb_elts);
}

// -----------------------------------------------------------------------------

template<class T_idx>
void Grid_partition<T_idx>::init(const Vec3_i& resolution,
                                 const Bbox3& bbox,
                                 int hint_nb_elts)
{
    tbx_assert( resolution.product() > 0 );
    _resolution = resolution;
    _size = bbox.lengths();
    tbx_assert( _size.product() > 0.f );
    _cell_lengths = _size.div( Vec3(_resolution) );
    _start = Vec3(bbox.pmin);

    _data.clear();
    _data.resize( resolution.product() );
    _filled_cells.clear();
    if( hint_nb_elts == -1 )
        _filled_cells.reserve(resolution.product()/4);
    else
        _filled_cells.reserve( tbx::min(resolution.product(), hint_nb_elts) );
}

// -----------------------------------------------------------------------------

template<class T_idx>
void Grid_partition<T_idx>::set_bbox(const Bbox3& bbox)
{
    tbx_assert( _resolution.product() > 0 );
    _start = Vec3( bbox.pmin );
    _size = bbox.lengths();
    _cell_lengths = _size.div( Vec3(_resolution) );
}

// -------------------------------------------------------------------------

template<class T_idx>
void Grid_partition<T_idx>::set_resolution(const Vec3_i& res)
{
    tbx_assert( _size.product() > 0.f );
    tbx_assert( res.product() > 0 );
    if( res != _resolution )
    {
        _resolution = res;
        _cell_lengths = _size.div( Vec3(_resolution) );
        _data.clear();
        _data.resize( res.product() );
        _filled_cells.clear();
    }
}

// -----------------------------------------------------------------------------

template<class T_idx>
int Grid_partition<T_idx>::insert(const Bbox3& bbox, T_idx object_idx)
{
    int nb_insertions = 0;
    for(int cell_idx : this->get_sub_bounding_box( bbox ) )
    {
        nb_insertions++;
        insert( cell_idx, object_idx );
    }
    return nb_insertions;
}


// -----------------------------------------------------------------------------

template<class T_idx>
void Grid_partition<T_idx>::insert(const tbx::Vec3& pos, T_idx object_idx)
{
    int linear_idx = Idx3(_resolution, this->position_to_cell_index(pos)).to_linear();
    insert(linear_idx, object_idx);
}

// -----------------------------------------------------------------------------

template<class T_idx>
void Grid_partition<T_idx>::insert(int cell_idx, T_idx object_idx)
{
    tbx_assert(_data.size() > 0 && "Uninitialized Grid, call Grid_partition::init()");

    if( _data[cell_idx].empty() )
    {
        // If memory completly used then double it brut force...
        if( _filled_cells.capacity() == _filled_cells.size() && _filled_cells.size() < _data.size())
            _filled_cells.reserve( tbx::min( _filled_cells.capacity() * 2, _data.size()) );

        _filled_cells.push_back( cell_idx );
    }
    _data[cell_idx].push_back( object_idx );
}

// -----------------------------------------------------------------------------

template<class T_idx>
void Grid_partition<T_idx>::clear()
{
    tbx_assert(_data.size() > 0 && "Uninitialized Grid, call Grid_partition::init()");
    for(unsigned i = 0; i < _filled_cells.size(); ++i)
        _data[ _filled_cells[i] ].clear();

    _filled_cells.clear();
}

// -----------------------------------------------------------------------------

template<class T_idx> inline
Vec3 Grid_partition<T_idx>::cell_index_to_coordinates(int linear_idx) const
{
    return cell_index_to_coordinates( Idx3(_resolution, linear_idx).to_3d() );
}

// -----------------------------------------------------------------------------

template<class T_idx> inline
Vec3 Grid_partition<T_idx>::cell_index_to_coordinates(const Vec3_i& idx) const
{
    tbx_assert(_data.size() > 0 && "Uninitialized Grid, call Grid_partition::init()");

    return _start + _cell_lengths * 0.5f + _cell_lengths * Vec3(idx);
}

// -----------------------------------------------------------------------------

template<class T_idx> inline
Vec3_i Grid_partition<T_idx>::position_to_cell_index(const Vec3& pos) const
{
    tbx_assert(_data.size() > 0 && "Uninitialized Grid, call Grid_partition::init()");

    // Local coords in the grid
    Vec3 lcl = pos - _start;
    Vec3 idx = lcl.div( _cell_lengths );
    return Vec3_i( idx.floor() ).clamp( Vec3_i(0), _resolution-1);
}

// -----------------------------------------------------------------------------

template<class T_idx>
const std::list<T_idx>& Grid_partition<T_idx>::elements_at(const Vec3& pos) const
{
    tbx_assert(_data.size() > 0 && "Uninitialized Grid, call Grid_partition::init()");
    return _data[ Idx3(_resolution, position_to_cell_index(pos)).to_linear() ];
}

// -----------------------------------------------------------------------------

template<class T_idx>
const std::list<T_idx>& Grid_partition<T_idx>::elements_at(int linear_cell_idx) const {
    tbx_assert(_data.size() > 0 && "Uninitialized Grid, call Grid_partition::init()");
    tbx_assert(linear_cell_idx < _data.size() );
    tbx_assert(linear_cell_idx > -1           );
    return _data[ linear_cell_idx ];
}

// -----------------------------------------------------------------------------

template<class T_idx>
const std::list<T_idx>& Grid_partition<T_idx>::elements_at(const grid3_iterator::Sub_box::It& it) const {
    tbx_assert(_data.size() > 0 && "Uninitialized Grid, call Grid_partition::init()");
    tbx_assert(it.to_linear() < _data.size() );
    tbx_assert(it.to_linear() > -1           );
    return _data[ it.to_linear() ];
}

}// END tbx NAMESPACE ==========================================================

