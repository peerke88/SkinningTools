#ifndef TOOLBOX_MAYA_SUB_MESH_HPP
#define TOOLBOX_MAYA_SUB_MESH_HPP

#include <vector>

// =============================================================================
namespace tbx_maya {
// =============================================================================

/**
    @brief Light representation of a sub mesh with iterator

    This class is used to iterate over a sub set of mesh vertices, or to iterate
    over the whole mesh.

    Usage (iterate over a sub set):
    @code
    Sub_mesh mesh({0, 10, 20, 23, ...});
    for( unsigned vertex_index : sub_mesh) {
        Vec3 position = mesh.vertex( vertex_index);
        ...
    }
    @endcode

    Usage (iterate over the whole mesh):
    @code
    Sub_mesh mesh( mesh.nb_vertices() );
    for( unsigned vertex_index : sub_mesh) {
        Vec3 position = mesh.vertex( vertex_index);
        ...
    }
    @endcode
*/
class Sub_mesh {
public:

    Sub_mesh(){ }

    /// @param vertex_list : list of vertex indices
    Sub_mesh(const std::vector<int>& vertex_list) : _vertex_list( vertex_list )
    {
    }

    /// @param total : total number of mesh vertices.
    Sub_mesh(unsigned total);

    /// @param total : total number of mesh vertices.
    void set(unsigned total);

    inline unsigned idx(unsigned i) const {
        return _vertex_list[i];
    }

    unsigned size() const { return (unsigned)_vertex_list.size(); }

    std::vector<int> vertex_list() const;

    class Mesh_it {
        friend class Sub_mesh;
    protected:
        unsigned _i;
        const Sub_mesh& _sub_mesh;
        inline Mesh_it(const Sub_mesh& sub_mesh, unsigned idx) :
            _i(idx),
            _sub_mesh( sub_mesh )
        { }
    public:
        inline bool operator!= (const Mesh_it& oth) const { return _i != oth._i; }
        inline const Mesh_it& operator++(   ) { ++_i; return (*this); }

        unsigned operator*() const { return (_sub_mesh.idx(_i)); }
    };

    inline Mesh_it begin() const { return Mesh_it(*this, 0);       }
    inline Mesh_it end()   const { return Mesh_it(*this, size());  }


private:
    std::vector<int> _vertex_list;
};

}// END tbx_maya Namespace =====================================================

#include "toolbox_maya/settings_end.hpp"

#endif // TOOLBOX_MAYA_SUB_MESH_HPP
