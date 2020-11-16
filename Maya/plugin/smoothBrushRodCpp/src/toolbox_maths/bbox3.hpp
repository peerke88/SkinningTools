#pragma once

#include <float.h>
#include <vector>
#include "toolbox_config/tbx_assert.hpp"

#include "toolbox_config/tbx_assert.hpp"
#include "toolbox_maths/ray.hpp"
#include "toolbox_maths/vector3_i.hpp"

// =============================================================================
namespace tbx {
// =============================================================================

/**
 * @brief Representation with two 3d points of an axis aligned bounded box
 * @note code compatible host/device/gcc/nvcc
 *
*/
struct Bbox3{

    /// using infinity allows maximum and minimum to take the other value,
    /// always. The union of two empty bboxes is still an empty bbox,
    /// and the intersection of an empty bbox with another bbox
    /// is still empty finally a point will be considered outside the bbox
    
    inline Bbox3():
        pmin(Point3( FLT_MAX,  FLT_MAX,  FLT_MAX)),
        pmax(Point3(-FLT_MAX, -FLT_MAX, -FLT_MAX))
    {
    }

    
    inline Bbox3(const Point3& a, const Point3& b):
        pmin(Point3(fminf(a.x, b.x), fminf(a.y, b.y), fminf(a.z, b.z))),
        pmax(Point3(fmaxf(a.x, b.x), fmaxf(a.y, b.y), fmaxf(a.z, b.z)))
    {    }

    
    inline Bbox3(const Vec3& a, const Vec3& b):
        pmin(Point3(fminf(a.x, b.x), fminf(a.y, b.y), fminf(a.z, b.z))),
        pmax(Point3(fmaxf(a.x, b.x), fmaxf(a.y, b.y), fmaxf(a.z, b.z)))
    {    }

    // FIXME: we should reorder components here as well or never do it at construction
    // for now I disable this constructor to public usage
private:
    
    inline Bbox3(float xmin, float ymin, float zmin,
                 float xmax, float ymax, float zmax):
        pmin(Point3(xmin, ymin, zmin)),
        pmax(Point3(xmax, ymax, zmax))
    {  }
public:

    
    inline bool inside(const Point3& p) const;

    
    inline bool inside(const Vec3& v) const{ return inside(Point3(v)); }

    /// Does the given ray intersect the bbox ? takes into account the ray's
    /// active segment. For instance, if the ray active segment [a,b] is inside
    /// the bbox, the resulting coordinates are [a,b], if the segment [a,b] is
    /// not included in the bbox, no intersection is detected, if [a,b] is
    /// partially in the bbox (let's say that ray(b) is inside the bbox and
    /// ray(a) is outside), then t0 = t_entry, t1 = b, and so on.
    /// @param ray : ray we want to intersect the bbox with
    /// @param tmin : contains the beginning of the ray segment and
    /// will contain the lower value of t for which it intersects
    /// @param tmax : contain the end of the ray segment and
    /// will contain the greater value of t for which it intersects
    /// @return true if it intersects.
     inline
    bool isect(const Ray& ray, float& tmin, float& tmax) const;

    
    inline Bbox3 union_bbox(const Bbox3& bb) const;

    
    inline Bbox3 bbox_isect(const Bbox3& bb) const;

    
    inline void add_point(const Point3& p);

    
    inline void add_point(const Vec3& v){ add_point( Point3(v) ); }

    // FIXME: it seems to me that len should be (pmax - pmin + 1)
    // But a lot of code need to be fixed in this case...
    // We could rename it diff and add a proper length method.
    /// Get x, y and z lenghts of the bouding box
    
    inline Vec3 lengths() const;

    /// A valid bbox as lengths stricly superior to epsilon
    
    inline bool is_valid( float eps = 0.00001f) const {
        return (pmax.x - pmin.x) > eps &&
               (pmax.y - pmin.y) > eps &&
               (pmax.z - pmin.z) > eps;
    }

    /// If the bbox represent the boundary of a grid with res.x * res .y * res.z
    /// cells this compute the integer index where 'pos' lies into.
    /// @param res : resolution (nb cells) of the grid in x, y and z directions
    /// @param pos : world position we want to find the corresponding grid index
    /// @return the grid index corresponding to the world position 'pos'.
    /// @warning user must check for out of bounds indices.
    
    inline Vec3_i index_grid_cell(Vec3_i res, Vec3 pos) const;

    /// Same as get_corner()
    inline void get_corners(std::vector<Point3>& corners) const;

    /// Get the ith corner position.
    /**
        @code
            6 +----+ 7
             /|   /|
          2 +----+3|
            |4+--|-+5
            |/   |/
            +----+
           0      1
        // Vertex 0 is pmin and vertex 7 pmax
        @endcode
    */
    
    inline Point3 get_corner(int i) const;

    
    inline Vec3 get_center() const { return (pmin + pmax).to_vec3() * 0.5f; }

    Point3 get_min() const { return pmin; }
    Point3 get_max() const { return pmax; }

    float width () const { return lengths().x; }
    float height() const { return lengths().y; }
    float depth () const { return lengths().z; }

    //TODO make private?
    Point3 pmin;
    Point3 pmax;
};

// -----------------------------------------------------------------------------

 inline
bool Bbox3::inside(const Point3& p) const {
    return (p.x >= pmin.x) & (p.y >= pmin.y) & (p.z >= pmin.z) &
           (p.x <= pmax.x) & (p.y <= pmax.y) & (p.z <= pmax.z);
}

// -----------------------------------------------------------------------------

 inline
bool Bbox3::isect(const Ray& ray, float& tmin, float& tmax) const
{
    #ifndef __CUDA_ARCH__
    ///////////////
    // Host code //
    ///////////////

    //principle : compute the coordinates for each pair of slabs
    //(one per axis), and take the max of the three lower values,
    //and the min for the greater.
    float t0 = tmin;
    float t1 = tmax;

    for (int i = 0; i < 3; i++)
    {
        //compute the distance to travel along the ray
        //to reach each slab for the current axis.
        float inv_ray_dir = 1.f / ray._dir[i];

        //assume for the moment that the slab corresponding
        //to the min point is the nearest.
        float t_near = (pmin[i] - ray._pos[i]) * inv_ray_dir;
        float t_far  = (pmax[i] - ray._pos[i]) * inv_ray_dir;

        // rearrange if necessary.
        if(t_near > t_far)
        {
            float tmp = t_near;
            t_near = t_far;
            t_far  = tmp;
        }

        // update max and min.
        t0 = t_near > t0 ? t_near : t0;
        t1 = t_far  < t1 ? t_far  : t1;

        // no intersection detection.
        if(t0 > t1) return false;

    }

    //there is an intersection.
    tbx_assert( t0 >= tmin );
    tbx_assert( t1 <= tmax );

    tmin = t0;
    tmax = t1;

    return true;
    #else
    /////////////////
    // Device code //
    /////////////////
    float l1 = __fdividef(pmin.x - ray._pos.x, ray._dir.x);
    float l2 = __fdividef(pmax.x - ray._pos.x, ray._dir.x);
    tmin = fmaxf(fminf(l1,l2), tmin);
    tmax = fminf(fmaxf(l1,l2), tmax);

    l1 = __fdividef(pmin.y - ray._pos.y, ray._dir.y);
    l2 = __fdividef(pmax.y - ray._pos.y, ray._dir.y);
    tmin = fmaxf(fminf(l1,l2), tmin);
    tmax = fminf(fmaxf(l1,l2), tmax);

    l1 = __fdividef(pmin.z - ray._pos.z, ray._dir.z);
    l2 = __fdividef(pmax.z - ray._pos.z, ray._dir.z);
    tmin = fmaxf(fminf(l1,l2), tmin);
    tmax = fminf(fmaxf(l1,l2), tmax);

    return ((tmax >= tmin) & (tmax >= 0.f));
    #endif
}

// -----------------------------------------------------------------------------

 inline
Bbox3 Bbox3::union_bbox(const Bbox3& bb) const {
    return Bbox3(fminf(pmin.x, bb.pmin.x), fminf(pmin.y, bb.pmin.y), fminf(pmin.z, bb.pmin.z),
                 fmaxf(pmax.x, bb.pmax.x), fmaxf(pmax.y, bb.pmax.y), fmaxf(pmax.z, bb.pmax.z));
}

// -----------------------------------------------------------------------------

 inline
Bbox3 Bbox3::bbox_isect(const Bbox3& bb) const {
    Bbox3 res =
            Bbox3(fmaxf(pmin.x, bb.pmin.x), fmaxf(pmin.y, bb.pmin.y), fmaxf(pmin.z, bb.pmin.z),
                  fminf(pmax.x, bb.pmax.x), fminf(pmax.y, bb.pmax.y), fminf(pmax.z, bb.pmax.z));
    if((res.pmin.x > res.pmax.x) |
       (res.pmin.y > res.pmax.y) |
       (res.pmin.z > res.pmax.z)
      )
    {
        res = Bbox3();
    }
    return res;
}

// -----------------------------------------------------------------------------

 inline
void Bbox3::add_point(const Point3& p) {
    pmin.x = fminf(p.x, pmin.x);
    pmin.y = fminf(p.y, pmin.y);
    pmin.z = fminf(p.z, pmin.z);
    pmax.x = fmaxf(p.x, pmax.x);
    pmax.y = fmaxf(p.y, pmax.y);
    pmax.z = fmaxf(p.z, pmax.z);
}

// -----------------------------------------------------------------------------

 inline
Vec3 Bbox3::lengths() const{ return pmax-pmin; }

// -----------------------------------------------------------------------------

inline void Bbox3::get_corners(std::vector<Point3>& corners) const
{
    corners.resize(8);
    for (int i = 0; i < 8; ++i)
        corners[i] = get_corner( i );
}

// -----------------------------------------------------------------------------

inline Point3 Bbox3::get_corner(int i) const
{
    Vec3 diff = pmax - pmin;
    diff.x *= (i      & 0x1);
    diff.y *= (i >> 1 & 0x1);
    diff.z *= (i >> 2 & 0x1);
    return Point3( pmin.x + diff.x, pmin.y + diff.y, pmin.z + diff.z);
}

// -----------------------------------------------------------------------------

Vec3_i Bbox3::index_grid_cell(Vec3_i res, Vec3 p) const
{
    Vec3 cell_lengths = lengths().div( (Vec3)res );

    // Local coords in the grid
    Vec3 lcl = p - Vec3(pmin);
    Vec3 idx = lcl.div( cell_lengths );
    Vec3_i int_idx( (int)floorf(idx.x),
                   (int)floorf(idx.y),
                   (int)floorf(idx.z) );

    return int_idx;
}

}// END tbx NAMESPACE ==========================================================

#include "toolbox_maths/settings_end.hpp"
