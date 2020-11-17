#ifndef TOOL_BOX_GRID_PARTITION_HPP
#define TOOL_BOX_GRID_PARTITION_HPP

#include <vector>
#include <list>

#include "toolbox_maths/bbox3.hpp"
#include "toolbox_algos/containers/grid_iterators.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

/**
 * @brief Axis aligned space partion with a 3D grid
 * @tparam T_idx : type of the element to be stored in the grid. Usually the
 * index of an object such as a triangle.
 *
 * Note on vocabulary:
 * - a grid node is the point connecting the edges.
 * - a grid cell is the cube defined by eight nodes.
 *
 * In this class we store the grid **cells**.
 *
 *
 * Example of usage: query of data stored locally in the grid
 * (within a bounding box  'bbox_triangle'):
   @code
   // Look up cells in the grid
   for(int cell_idx : grid_partition.get_sub_bounding_box( bbox_triangle ))
   {
        // Look up elements registered in the cell
        const std::list<int>& list = grid_partition.elements_at(cell_idx);
        for(int elt : list)
        {

        }
   }
   @endcode
 *
 */
template<class T_idx>
class Grid_partition {
public:

    /// @param[in] resolution : number of grid's cells in each direction ( total
    /// number of cells == resolution.product() )
    /// @param[in] hint_nb_elts: guess how many objects will be stored
    /// in the grid to improve performances
    Grid_partition(const Vec3_i& resolution,
                   const Vec3& size,
                   const Vec3& start,
                   int hint_nb_elts = -1);

    Grid_partition(const Vec3_i& resolution,
                   const Bbox3& bbox,
                   int hint_nb_elts = -1);

    Grid_partition() { }

    ~Grid_partition() {
        _data.clear();
        _filled_cells.clear();
    }

    /// @param[in] hint_nb_elts: guess how many objects will be stored
    /// in the grid to improve performances
    void init(const Vec3_i& resolution,
              const Bbox3& bbox,
              int hint_nb_elts = -1);

    /// Set the grid bbox.
    /// @warning will invalidate current iterators
    void set_bbox(const Bbox3& bbox);

    void set_resolution(const Vec3_i& res);

    /// @brief Insert an object index 'object_idx' into every grid cells inside the
    /// bounding box 'bbox'.
    ///
    /// If objects are ordered spatially it will improve the speed for
    /// clearing the grid
    /// @return number of cells the objext index were added to.
    int insert(const Bbox3& bbox, T_idx object_idx);

    /// Insert in cell designated by 'linear_cell_index' the object
    /// 'object_idx'
    void insert(int linear_cell_index, T_idx object_idx);

    /// Insert in cell designated by the coordinates 'pos' the object
    /// 'object_idx'
    void insert(const tbx::Vec3& pos, T_idx object_idx);

    /// Clear every inserted elements in the grid
    void clear();

    inline Vec3 cell_index_to_coordinates(int linear_idx) const;

    inline Vec3 cell_index_to_coordinates(const Vec3_i& idx) const;

    /// 3d position to the cell index in the grid
    /// (position is clamped to the extent of the grid)
    inline Vec3_i position_to_cell_index(const Vec3& pos) const;

    /// Element stored in the cell at 'pos'
    const std::list<T_idx>& elements_at(const Vec3& pos) const;

    /// Element stored in the cell at 'linear_cell_idx'
    const std::list<T_idx>& elements_at(int linear_cell_idx) const;

    /// Element stored in the cell described by the iterator 'it'
    const std::list<T_idx>& elements_at(const grid3_iterator::Sub_box::It& it) const;

    // -------------------------------------------------------------------------
    /// @name Iterator
    // -------------------------------------------------------------------------
    ///@{

    /// @brief iterates over every sub cell included in the bounding box 'bbox'
    grid3_iterator::Sub_box get_sub_bounding_box(const Bbox3& bbox) const {
        return grid3_iterator::Sub_box(bbox, Grid3_desc(_resolution, _cell_lengths, _start));
    }

    // -------------------------------------------------------------------------

    Vec3_i get_resolution() const { return _resolution; }
    Vec3 get_origin() const { return _start; }
    Vec3 get_size() const { return _size; }
    Vec3 get_cell_lengths() const { return _cell_lengths; }
    float get_max_cell_diagonal() const { return get_cell_lengths().get_max() * std::sqrt(2.0f); }
    ///@}

private:
    // -------------------------------------------------------------------------
    /// @name Attributes
    // -------------------------------------------------------------------------
    Vec3_i _resolution;    ///< the number of cells (and NOT nodes)
    Vec3 _size;
    Vec3 _cell_lengths;
    Vec3 _start;

    // TODO: instead of a std::list for each cell why not construct a huge
    // list to preallocate approximetly and dispatch the nodes of the list
    // in the cells... We will avoid to use std::list which is double ended and
    // write our own single linked list.
    //
    /// Linear storage of the grid data. We use a Vector to store every cells
    /// of the grid since the size should remain static.
    /// We use a list to store elements in each cell since objects will move
    /// dynamically.
    std::vector< std::list<T_idx> > _data;

    /// list of none empty cells in order to quickly access them.
    /// @warning the list can be redundant.
    std::vector<int> _filled_cells;

};

}// END tbx NAMESPACE ==========================================================

#include "toolbox_algos/space_partition/grid_partition.inl"

#include "toolbox_algos/settings_end.hpp"

#endif // GRID_PARTITION_HPP
