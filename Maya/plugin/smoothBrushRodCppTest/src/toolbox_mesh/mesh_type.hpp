#ifndef TBX_MESH_TYPE_HPP
#define TBX_MESH_TYPE_HPP


#include "toolbox_config/tbx_assert.hpp"

// =============================================================================
namespace tbx_mesh {
// =============================================================================

// TODO delete this namespace:
/**
 * @brief
 */
// =============================================================================
//namespace mesh {
// =============================================================================

typedef int Vert_idx; ///< Vertex index
typedef int Edge_idx; ///< Edge index
typedef int Face_idx; ///< Face index

typedef int Tri_idx;  ///< Triangle index
typedef int Quad_idx; ///< Quad index

typedef int Island_idx; ///< Mesh island (:group of connected faces) index

// -----------------------------------------------------------------------------

/// An edge with overloaded == and < to use it in map containers.
struct Edge {
    Vert_idx a, b; ///< vertex index of the edge

    
    Edge() : a(-1), b(-1) { }

    
    Edge(Vert_idx a_, Vert_idx b_) : a(a_), b(b_) { }

    /// Edges are not oriented. Therefore (a,b) == (b,a) is true.
    
    inline bool operator==(const Edge& e) const {
        tbx_assert( a != b ); // Corruption detected: un-initialized or self-edge
        return (e.a == a && e.b == b) || (e.b == a && e.a == b);
    }

    
    inline bool operator<(const Edge& e) const {
        tbx_assert( a != b ); // Corruption detected: un-initialized or self-edge
        return (e.a == a ) ? e.b < b : e.a < a;
    }

    /*
    /// Edges can be ordered in lexicographical order.
    inline bool operator< (const Edge& e) const
    {
        tbx_assert( a != b && e.a != e.b );

        Mesh_t::Vert_idx my_min = min(a, b);
        Mesh_t::Vert_idx my_max = max(a, b);
        Mesh_t::Vert_idx other_min = min(e.a, e.b);
        Mesh_t::Vert_idx other_max = max(e.a, e.b);

        return (other_min != my_min) ? other_min < my_min : other_max < my_max;
    }
    */

    /// Acces through array operator []
    
    inline const int& operator[](int i) const{
        tbx_assert( i < 2);
        return ((int*)this)[i];
    }

    
    inline int& operator[](int i) {
        tbx_assert( i < 2);
        return ((int*)this)[i];
    }

     inline       Vert_idx& vert(int i)       { return (*this)[i]; }
     inline const Vert_idx& vert(int i) const { return (*this)[i]; }
};

// -----------------------------------------------------------------------------

/// @brief triangle face represented with three vertex index
/// you can access the indices with the attributes '.a' '.b' '.c' or the array
/// accessor []
struct Tri_face {
    
    Tri_face() : a(-1), b(-1), c(-1) { }

    
    Tri_face(Vert_idx a_, Vert_idx b_, Vert_idx c_) : a(a_), b(b_), c(c_) { }

    inline void set( Vert_idx a_, Vert_idx b_, Vert_idx c_ ){
        a = a_; b = b_; c = c_;
    }

    /// Get one of the three edges
    
    Edge edge(int i) const {
        tbx_assert( a != b && b != c && c != a ); // Corruption detected: un-initialized or self-tri
        const Edge e[3] = { Edge(a,b), Edge(b,c), Edge(c,a) };
        return e[i];
    }

    /// Get the edge opposite to vertex_i
    /**
       @code
                (vertex_i)
                    +
                   / \
                  /   \
            (v1) +-----+ (v2) -> opposite edge
       @endcode
    */
    /// 
    Edge opposite_edge(Vert_idx vertex_i) const {
        Edge edge;
        for(int i = 0; i < 3; i++)  {
            if(this->vert(i) == vertex_i) {
                edge.a = this->vert( (i+1) % 3 );
                edge.b = this->vert( (i+2) % 3 );
                return edge;
            }
        }
        tbx_assert(false && "couldn't find opposite edge");
        return edge;
    }

    /// Get the vertex opposite to edge 'e'
    /**
       @code
              (opposite vertex)
                    +
                   / \
                  /   \
        (edge.a) +-----+ (edge.b)
       @endcode
    */
    /// 
    Vert_idx opposite_vertex(const Edge& e) const {
        for(int i = 0; i < 3; i++)
        {
            Vert_idx idx = this->vert(i);
            if(idx != e.a &&  idx != e.b) {
                return idx;
            }
        }
        tbx_assert(false && "couldn't find opposite vertex");
        return -1;
    }

    /// @return true if the edge 'e' is present in this face
    
    bool has_edge(const Edge& e) const {
        for(int i = 0; i < 3; i++)  {
            if( e == this->edge(i) ) {
                return true;
            }
        }
        return false;
    }

    
    bool has_vertex(Vert_idx idx) const {
        for(int i = 0; i < 3; i++) {
            if(this->vert( i ) == idx)
                return true;
        }
        return false;
    }

    /// Acces through array operator []
    
    inline const Vert_idx& operator[](int i) const {
        tbx_assert( i < 3);
        return ((Vert_idx*)this)[i];
    }

    
    inline Vert_idx& operator[](int i) {
        tbx_assert( i < 3);
        return ((Vert_idx*)this)[i];
    }

     inline       Vert_idx& vert(int i)       { return (*this)[i]; }
     inline const Vert_idx& vert(int i) const { return (*this)[i]; }

    Vert_idx a, b, c;
};

// -----------------------------------------------------------------------------

struct Tri_edges {
    
    Tri_edges() : a(-1), b(-1), c(-1) { }

    
    Tri_edges(int a_, int b_, int c_) : a(a_), b(b_), c(c_) { }

    /// Acces through array operator []
    
    inline const int& operator[](int i) const{
        tbx_assert( i < 3);
        return ((int*)this)[i];
    }

    
    inline int& operator[](int i) {
        tbx_assert( i < 3);
        return ((int*)this)[i];
    }

    Edge_idx a, b, c; ///< edge index
};

// -----------------------------------------------------------------------------

struct Quad_face {
    
    Quad_face() : a(-1), b(-1), c(-1), d(-1) { }

    
    Quad_face(Vert_idx a_, Vert_idx b_, Vert_idx c_, Vert_idx d_) : a(a_), b(b_), c(c_), d(d_) {}

    inline void set(Vert_idx a_, Vert_idx b_, Vert_idx c_, Vert_idx d_){
        a = a_; b = b_; c = c_; d = d_;
    }

    /// Acces through array operator []
    
    inline const int& operator[](int i) const{
        tbx_assert( i < 4);
        return ((int*)this)[i];
    }

    
    inline int& operator[](int i) {
        tbx_assert( i < 4);
        return ((int*)this)[i];
    }

     inline       Vert_idx& vert(int i)       { return (*this)[i]; }
     inline const Vert_idx& vert(int i) const { return (*this)[i]; }

    Vert_idx a, b, c, d;
};

// -----------------------------------------------------------------------------

/// A set of vertex attributes for rendering.
struct Vertex_attributes
{
    Vertex_attributes()
        : _normal_idx(-1), _texture_idx(-1)
    {
    }

    //TODO : does this really belong here ?
    int _normal_idx;  ///< Index into an array of normal vectors
    int _texture_idx; ///< Index into an array of texture coordinates

    /// Vertex attributes compare equal if attributes are equal.
    /// i.e only _normal_index and _texture_index,
    /// (_triangle_index and _vertex_number are ignored)
    inline bool operator==( const Vertex_attributes& o) const
    {
        return (_normal_idx ==  o._normal_idx) && (_texture_idx == o._texture_idx);
    }
};

// -----------------------------------------------------------------------------

struct Triangle_attributes
{
    int _vertex_occurence[3];
    // maybe material id ?
};

//}// End Namespace mesh_t =====================================================

}// END tbx_mesh NAMESPACE =====================================================

#include "toolbox_mesh/settings_end.hpp"

#endif // TBX_MESH_TYPE_HPP
