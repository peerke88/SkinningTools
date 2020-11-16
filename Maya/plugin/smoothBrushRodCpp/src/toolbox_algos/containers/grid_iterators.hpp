#ifndef TOOL_BOX_GRID_ITERATORS_HPP
#define TOOL_BOX_GRID_ITERATORS_HPP

#include "toolbox_maths/idx3.hpp"
#include "toolbox_maths/bbox3.hpp"
#include "toolbox_maths/vector3.hpp"
#include "toolbox_maths/vector3_i.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

/// @brief 3D Grid descriptor (resolution, cell size etc.
struct Grid3_desc {
    Vec3_i _resolution;
    Vec3 _cell_lengths;
    Vec3 _start;

    Grid3_desc() {}

    /// @param[in] resolution : resolution of the grid. i.e. how many cells.
    /// (2x2 cell resolution makes 3x3 nodes and 12 edges)
    /// @param[in] cell_lengths : size of the edges of the cell.
    /// i.e. distance between two nodes.
    /// @param[in] start : starting continuous 3d position: The grid's node
    /// with smallest coordinates.
    Grid3_desc(const Vec3_i& resolution, const Vec3& cell_lengths, const Vec3& start) :
        _resolution(resolution), _cell_lengths(cell_lengths), _start(start)
    { }

    /// 3d position to the integer index in the grid
    /// (position is clamped to the extent of the grid)
    inline Vec3_i pos_to_idx(const Vec3& pos) const
    {
        // Local coords in the grid
        Vec3 lcl = pos - _start;
        Vec3 idx = lcl.div( _cell_lengths );
        return Vec3_i( idx.floor() ).clamp( Vec3_i(0), _resolution-1);
    }

};


/**
 * @namespace ::tbx::grid3_iterator
 * @brief 3D grid convenient iterators
 *
 * Looking up 3D grids can be tedious especially when change of coordinates are
 * required, or when you have to convert 3D positions to indices in the grid.
 * This namespace holds tools to facilitate such look ups.
 */

// =============================================================================
namespace grid3_iterator {
// =============================================================================

/**
 * @brief Grid iterator inside a sub rectangular bounding box (axis aligned)
 *
 * Iterates over the grid's cells (and not <b>nodes</b>)
 * whithin a (sub) bounding box.
 *
   Here is an example:
   @code
   BBox3 bbox; // our 3d sub bounding box
   Grid3_desc desc; // describe the 3d grid we want to look up (size, resolution etc.)
   grid3_iterator::Sub_box sub_box( bbox, desc );
   grid3_iterator::Sub_box::It box_it = sub_box.begin()
   for (; box_it != sub_box.end(); ++box_it) // Look up every cells crossing 'bbox'.
   for (int linear_idx :  sub_box ) // <- alternative look up
   {
        int linear_idx = box_it.to_linear(); // Linear index of the current cell
        Vec3_i idx_3D  = box_it.to_3d();    // 3d index of the current cell

        /// If you know the "bottom left rear corner" (Vec3 start) and the
        /// lengths of the cells in x, y and z directions (Vec3 steps)
        /// Then you can compute the 3d positions 'pos' of the nodes
        /// (but the border are
        Vec3 pos = start + Vec3( box_it.to_3d() ) * steps;
   }
   // Letters represents nodes.
   // Digits represents cells.
   // g-----h-----i
   // |     |     |
   // |  2  |  3  |
   // d-----e-----f
   // |     |     |
   // |  0  |  1  |
   // a-----b-----c
   // The code above will look up the cells [0, 1, 2, 3] in "linear_idx"
   // And the nodes 3D positions [a, b, d, e] in 'pos'
   @endcode
 *
 */


// -------------------------------------------------------------------------

class Sub_box {
public:

    /// the grid informations
    Grid3_desc _grid_descriptor;
    Bbox3 _sub_bbox;

    /// @brief create a box iterator given a bounding box 'bbox' and a 3D grid
    /// descriptor 'desc'
    Sub_box(const Bbox3& bbox, const Grid3_desc& desc)
        : _grid_descriptor(desc)
        , _sub_bbox(bbox)
    {

    }

    // -------------------------------------------------------------------------

    class It {
        Grid3_desc _grid;    ///< the grid informations

        Idx3 _offset;       ///< offset we start looking up in the grid
        Idx3 _idx_in_box;   ///< Index local to the bounding box

        int _nb_elts_in_box;

        int _curr_idx; ///< current linear index in the grid

    public:

        It(){ }

        It(const Bbox3& bbox, const Grid3_desc& g) :
            _grid(g)
        {
            const Vec3_i start = _grid.pos_to_idx( Vec3(bbox.pmin) );
            const Vec3_i end   = _grid.pos_to_idx( Vec3(bbox.pmax) );
            _offset = Idx3(_grid._resolution, start);
            const Vec3_i sub_size = end - start + 1;
            tbx_assert( sub_size.get_max() > 0);
            _nb_elts_in_box = sub_size.product();
            _idx_in_box = Idx3(sub_size, 0);
            _curr_idx = (_offset + _idx_in_box.to_vec3i()).to_linear();
        }

        /// @brief linear index of the grid's cell
        int to_linear() const { return _curr_idx; }

        inline int operator*() const { return to_linear(); }

        /// @brief 3D index of the current grid's cell
        Vec3_i to_3d() const { return Idx3(_grid._resolution, _curr_idx).to_3d(); }

        inline bool operator != (const It&) const {
            //return _idx_in_box.is_in(); // optimized to ->
            return _idx_in_box.to_linear() < _nb_elts_in_box;
        }

        inline It& operator++() {
            ++_idx_in_box;
            _curr_idx = (_offset + _idx_in_box.to_vec3i()).to_linear();
            return (*this);
        }
    };

    // -------------------------------------------------------------------------

    inline It begin() const { return It(_sub_bbox, _grid_descriptor); }
    inline It end()   const { return It(); }
};


}// END grid3_iterator =========================================================

}// END tbx NAMESPACE ==========================================================

#include "toolbox_algos/settings_end.hpp"

#endif // TOOL_BOX_GRID_ITERATORS_HPP
