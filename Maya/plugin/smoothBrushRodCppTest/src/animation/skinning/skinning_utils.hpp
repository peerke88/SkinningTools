#pragma once

#include <toolbox_config/meta_headers/meta_math_cu.hpp>
#include <toolbox_stl/vector.hpp>
#include <toolbox_maths/calculus.hpp>

#include <toolbox_mesh/mesh_group.hpp>
#include <map>
#include <limits>

// =============================================================================
namespace anim {
// =============================================================================

/// Finds the index of the strongest weight in a weight map.
inline int find_max_index( const std::map<int, float>& weights)
{

   int max_index = -1;

   float max_value = -std::numeric_limits<float>::infinity();
   for(std::map<int, float>::const_iterator it = weights.begin(); it != weights.end(); ++it)
   {
        if (it->second > max_value)
        {
            max_value = it->second;
            max_index = it->first;
        }
    }
    tbx_assert(max_index != -1);

    return max_index;
}


// -----------------------------------------------------------------------------

inline float sum( const std::map<int, float>& weights)
{
   float sum = 0.0f;
   for(auto it = weights.begin(); it != weights.end(); ++it){
       sum += it->second;
   }
   return sum;
}


// -----------------------------------------------------------------------------

/// prune the weight map with values < eps.
inline void prune( std::map<int, float>& weights, float eps = 0.00001f)
{
   auto it = weights.begin();
   while( it != weights.end() )
   {
        if( it->second < eps)
            it = weights.erase( it );
        else
            ++it;
   }
}

// -----------------------------------------------------------------------------

inline
void prune(std::vector< std::map<int, float> >& weights, float eps = 0.00001f)
{
    for(unsigned vert_idx = 0; vert_idx < weights.size(); ++vert_idx)
        anim::prune( weights[vert_idx], eps);
}
// -----------------------------------------------------------------------------

inline void clamp( std::map<int, float>& weights, float min, float max)
{
   for(auto it = weights.begin(); it != weights.end(); ++it){
       it->second =  fminf( max, fmaxf(it->second, min));
   }
}

// -----------------------------------------------------------------------------

/// normalize the weight map by averaging
inline void normalize( std::map<int, float>& weights)
{
   float sum = 0.f;
   for( auto it = weights.begin(); it != weights.end(); ++it)
        sum += it->second;

   using namespace std;
   if( fabsf(sum) <= 0.0f || isnan(sum) )
       return;

   for( auto it = weights.begin(); it != weights.end(); ++it)
        it->second /= sum;
}

// -----------------------------------------------------------------------------

/// normalize every weight maps by averaging
inline void normalize( std::vector<std::map<int, float> >& weights )
{
    for( size_t i = 0; i < weights.size(); ++i )
        normalize( weights[i] );
}

} // END anim NAMESPACE ========================================================
