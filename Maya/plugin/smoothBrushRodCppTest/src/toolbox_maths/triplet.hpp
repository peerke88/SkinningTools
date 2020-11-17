#pragma once

// =============================================================================
namespace tbx {
// =============================================================================

/// @brief A small structure to hold a non zero as a triplet (i,j,value).
/// Usefull to transfer data to Eigen Sparse matrices with
/// Eigen::SparseMatrix::setFromTriplets()
template<typename Scalar>
class Triplet {
public:
    Triplet() : _row(0), _col(0), _value(0) {}

    Triplet(unsigned i, unsigned j, Scalar v = Scalar(0))
        : _row(i), _col(j), _value(v)
    {}

    /// @returns the row index of the element
    inline unsigned row() const { return _row; }

    /// @returns the column index of the element
    inline unsigned col() const { return _col; }

    /// @returns the value of the element
    inline Scalar value() const { return _value; }

protected:
    unsigned _row;
    unsigned _col;
    Scalar _value;
};

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_maths/settings_end.hpp"

